from datetime import date, datetime
from functools import wraps
import random
import logging
import traceback
import os

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, get_jwt
)

from models import db, User, Trek, Booking, StaffProfile
from config import Config

api = Blueprint("api", __name__, url_prefix="/api")
logger = logging.getLogger("tma.routes")


# ---------- helpers ----------

def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
            if get_jwt().get("role") not in roles:
                return jsonify({"error": "Forbidden: insufficient role"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def paginate(query, default_per_page=10):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", default_per_page, type=int)
    return query.paginate(page=page, per_page=per_page, error_out=False)


def safe_cache_delete(*keys):
    try:
        from app import cache
        for k in keys:
            cache.delete(k)
    except Exception:
        pass  # Redis may not be running locally; caching is optional, not critical path


def safe_cache_get(key):
    try:
        from app import cache
        return cache.get(key)
    except Exception:
        return None  # Redis may not be running locally; caching is optional, not critical path


def safe_cache_set(key, value, timeout=None):
    try:
        from app import cache
        cache.set(key, value, timeout=timeout)
    except Exception:
        pass  # Redis may not be running locally; caching is optional, not critical path


# Aggregation endpoints (admin dashboard, reports) recompute over every trek/booking
# on each call. Cache their JSON payloads for CACHE_DEFAULT_TIMEOUT (5 min) and bust
# the cache on any write that changes treks or bookings.
DASHBOARD_CACHE_KEY = "popular_treks"
REPORTS_CACHE_KEY = "full_report"


def invalidate_stats_cache():
    safe_cache_delete(DASHBOARD_CACHE_KEY, REPORTS_CACHE_KEY)


# ---------- auth ----------

@api.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name, email, password = data.get("name"), data.get("email"), data.get("password")
    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(name=name, email=email, phone=data.get("phone"), role="user", status="active")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Registration successful", "user": user.to_dict()}), 201


@api.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email, password, expected_role = data.get("email"), data.get("password"), data.get("role")
    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401
    if user.status == "blacklisted":
        return jsonify({"error": "Your account has been blacklisted. Contact admin."}), 403
    if user.status == "inactive":
        return jsonify({"error": "Your account is inactive. Contact admin."}), 403
    if expected_role and user.role != expected_role:
        return jsonify({"error": f"This account is not registered as {expected_role}"}), 403

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "name": user.name})
    return jsonify({"message": "Login successful", "access_token": token, "user": user.to_dict()}), 200


@api.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully"}), 200


# ---------- OTP login (alternative to password, for Users and Staff only) ----------
# Uses the same Redis instance as the app's cache (see app.py / config.py) purely as
# short-lived storage for the OTP itself - not as a "may or may not be there" cache,
# so unlike safe_cache_*, failures here return a real error instead of silently no-op'ing.

OTP_TTL_SECONDS = 300          # OTP is valid for 5 minutes
OTP_RESEND_COOLDOWN_SECONDS = 60   # can't request another OTP within 60s of the last one
OTP_MAX_ATTEMPTS = 5           # wrong guesses allowed before lockout
OTP_LOCKOUT_SECONDS = 900      # lockout duration after too many wrong guesses
OTP_ELIGIBLE_ROLES = ("user", "staff")  # admin must always use password login


def _otp_key(email):
    return f"otp:{email.lower().strip()}"


def _otp_attempts_key(email):
    return f"otp_attempts:{email.lower().strip()}"


def _otp_cooldown_key(email):
    return f"otp_cooldown:{email.lower().strip()}"


@api.route("/auth/otp/request", methods=["POST"])
def request_otp():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip()
    if not email:
        return jsonify({"error": "email is required"}), 400

    # Always return the same generic message whether or not the account exists,
    # so this endpoint can't be used to check which emails are registered.
    generic_ok = jsonify({"message": "If an account with that email is eligible for OTP login, a code has been sent."})

    user = User.query.filter_by(email=email).first()
    if not user or user.role not in OTP_ELIGIBLE_ROLES or user.status != "active":
        return generic_ok, 200

    try:
        from app import cache
        if cache.get(_otp_cooldown_key(email)):
            return jsonify({"error": "An OTP was already sent recently. Please wait a minute before requesting another."}), 429

        otp = f"{random.randint(0, 999999):06d}"
        cache.set(_otp_key(email), otp, timeout=OTP_TTL_SECONDS)
        cache.set(_otp_cooldown_key(email), True, timeout=OTP_RESEND_COOLDOWN_SECONDS)
        cache.delete(_otp_attempts_key(email))
    except Exception:
        print("=" * 60)
        print("OTP REQUEST FAILED - full traceback below:")
        traceback.print_exc()
        print("=" * 60)
        return jsonify({"error": "OTP login is temporarily unavailable. Please log in with your password instead."}), 503

    try:
        from tasks import send_otp_email
        send_otp_email.delay(user.email, otp, user.name)
    except Exception as e:
        logger.warning(f"Could not queue OTP email via Celery: {e}. Attempting direct send.")
        try:
            from tasks import _send_email
            greeting = f"Hi {user.name}," if user.name else "Hi,"
            body = (
                f"<h3>Your TMA Login OTP</h3>"
                f"<p>{greeting}</p>"
                f"<p>Your one-time password is:</p>"
                f"<h2 style='letter-spacing:6px'>{otp}</h2>"
                f"<p>This code expires in 5 minutes. If you did not request this, you can safely ignore this email.</p>"
            )
            _send_email(user.email, "Your TMA Login OTP", body)
        except Exception as inner_e:
            logger.error(f"Failed to send direct OTP email: {inner_e}")

    return generic_ok, 200


@api.route("/auth/otp/verify", methods=["POST"])
def verify_otp():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip()
    otp = (data.get("otp") or "").strip()
    if not email or not otp:
        return jsonify({"error": "email and otp are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or user.role not in OTP_ELIGIBLE_ROLES:
        return jsonify({"error": "Invalid email or OTP"}), 401

    try:
        from app import cache
    except Exception:
        print("=" * 60)
        print("OTP VERIFY FAILED - full traceback below:")
        traceback.print_exc()
        print("=" * 60)
        return jsonify({"error": "OTP login is temporarily unavailable. Please log in with your password instead."}), 503

    attempts_key = _otp_attempts_key(email)
    attempts = cache.get(attempts_key) or 0
    if attempts >= OTP_MAX_ATTEMPTS:
        return jsonify({"error": "Too many incorrect attempts. Please request a new OTP in 15 minutes."}), 429

    stored_otp = cache.get(_otp_key(email))
    if not stored_otp or stored_otp != otp:
        cache.set(attempts_key, attempts + 1, timeout=OTP_LOCKOUT_SECONDS)
        return jsonify({"error": "Invalid or expired OTP"}), 401

    # Correct - OTP is one-time use, clear it immediately so it can't be replayed.
    cache.delete(_otp_key(email))
    cache.delete(attempts_key)

    if user.status == "blacklisted":
        return jsonify({"error": "Your account has been blacklisted. Contact admin."}), 403
    if user.status == "inactive":
        return jsonify({"error": "Your account is inactive. Contact admin."}), 403

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "name": user.name})
    return jsonify({"message": "Login successful", "access_token": token, "user": user.to_dict()}), 200


# ---------- users ----------

@api.route("/users", methods=["GET"])
@role_required("admin")
def list_users():
    query = User.query.filter_by(role="user")
    search, status = request.args.get("search"), request.args.get("status")
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(User.name.ilike(like), User.email.ilike(like)))
    if status:
        query = query.filter_by(status=status)
    p = paginate(query.order_by(User.created_at.desc()))
    return jsonify({"users": [u.to_dict() for u in p.items], "total": p.total, "page": p.page, "pages": p.pages}), 200


@api.route("/users/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user = User.query.get_or_404(int(get_jwt_identity()))
    data = request.get_json() or {}
    if "name" in data:
        user.name = data["name"]
    if "phone" in data:
        user.phone = data["phone"]
    if data.get("password"):
        user.set_password(data["password"])
    db.session.commit()
    return jsonify({"message": "Profile updated", "user": user.to_dict()}), 200


@api.route("/users/<int:user_id>/status", methods=["PUT"])
@role_required("admin")
def change_user_status(user_id):
    user = User.query.get_or_404(user_id)
    new_status = (request.get_json() or {}).get("status")
    if new_status not in ("active", "inactive", "blacklisted"):
        return jsonify({"error": "Invalid status"}), 400
    user.status = new_status
    db.session.commit()
    return jsonify({"message": f"User status updated to {new_status}", "user": user.to_dict()}), 200


# ---------- staff ----------

@api.route("/staff", methods=["GET"])
@role_required("admin")
def list_staff():
    query = StaffProfile.query.join(User)
    search, status = request.args.get("search"), request.args.get("status")
    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(User.name.ilike(like), User.email.ilike(like)))
    if status:
        query = query.filter(StaffProfile.status == status)
    p = paginate(query)
    return jsonify({"staff": [s.to_dict() for s in p.items], "total": p.total, "page": p.page, "pages": p.pages}), 200


@api.route("/staff", methods=["POST"])
@role_required("admin")
def create_staff():
    data = request.get_json() or {}
    name, email, password = data.get("name"), data.get("email"), data.get("password")
    if not name or not email or not password:
        return jsonify({"error": "name, email, password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already in use"}), 409

    user = User(name=name, email=email, phone=data.get("contact_number"), role="staff", status="active")
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    profile = StaffProfile(
        user_id=user.id, contact_number=data.get("contact_number"),
        specialization=data.get("specialization"), experience_years=data.get("experience_years", 0),
    )
    db.session.add(profile)
    db.session.commit()
    return jsonify({"message": "Staff created", "staff": profile.to_dict()}), 201


@api.route("/staff/<int:staff_id>", methods=["PUT"])
@role_required("admin")
def update_staff(staff_id):
    profile = StaffProfile.query.get_or_404(staff_id)
    data = request.get_json() or {}
    if "name" in data and profile.user:
        profile.user.name = data["name"]
    if "contact_number" in data:
        profile.contact_number = data["contact_number"]
        if profile.user:
            profile.user.phone = data["contact_number"]
    if "specialization" in data:
        profile.specialization = data["specialization"]
    if "experience_years" in data:
        profile.experience_years = data["experience_years"]
    db.session.commit()
    return jsonify({"message": "Staff updated", "staff": profile.to_dict()}), 200


@api.route("/staff/<int:staff_id>/status", methods=["PUT"])
@role_required("admin")
def change_staff_status(staff_id):
    profile = StaffProfile.query.get_or_404(staff_id)
    new_status = (request.get_json() or {}).get("status")
    if new_status not in ("active", "inactive", "blacklisted"):
        return jsonify({"error": "Invalid status"}), 400
    profile.status = new_status
    if profile.user:
        profile.user.status = new_status
    db.session.commit()
    return jsonify({"message": f"Staff status updated to {new_status}", "staff": profile.to_dict()}), 200


@api.route("/staff/<int:staff_id>", methods=["DELETE"])
@role_required("admin")
def delete_staff(staff_id):
    profile = StaffProfile.query.get_or_404(staff_id)
    user = profile.user
    db.session.delete(profile)
    if user:
        db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Staff deleted"}), 200


@api.route("/staff/me/dashboard", methods=["GET"])
@role_required("staff")
def staff_dashboard():
    profile = StaffProfile.query.filter_by(user_id=int(get_jwt_identity())).first_or_404()
    treks = profile.assigned_treks
    total_participants = sum(len([b for b in t.bookings if b.status == "Booked"]) for t in treks)
    ongoing = len([t for t in treks if t.status == "Open"])
    return jsonify({
        "assigned_treks_count": len(treks), "total_participants": total_participants,
        "ongoing_treks": ongoing, "treks": [t.to_dict() for t in treks],
    }), 200


# ---------- treks ----------

@api.route("/treks", methods=["GET"])
def list_treks():
    query = Trek.query
    search = request.args.get("search")
    location = request.args.get("location")
    difficulty = request.args.get("difficulty")
    status = request.args.get("status")
    min_duration = request.args.get("min_duration", type=int)
    max_duration = request.args.get("max_duration", type=int)

    if search:
        like = f"%{search}%"
        query = query.filter(db.or_(Trek.trek_name.ilike(like), Trek.location.ilike(like)))
    if location and location != "All":
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    if difficulty and difficulty != "All":
        query = query.filter(Trek.difficulty == difficulty)
    if status and status != "All":
        query = query.filter(Trek.status == status)
    if min_duration is not None:
        query = query.filter(Trek.duration >= min_duration)
    if max_duration is not None:
        query = query.filter(Trek.duration <= max_duration)

    p = paginate(query.order_by(Trek.start_date.asc()), default_per_page=12)
    return jsonify({
        "treks": [t.to_dict(include_staff=True) for t in p.items],
        "total": p.total, "page": p.page, "pages": p.pages,
    }), 200


@api.route("/treks/<int:trek_id>", methods=["GET"])
def get_trek(trek_id):
    return jsonify({"trek": Trek.query.get_or_404(trek_id).to_dict(include_staff=True)}), 200


@api.route("/treks", methods=["POST"])
@role_required("admin")
def create_trek():
    data = request.get_json() or {}
    required = ["trek_name", "location", "difficulty", "duration", "available_slots", "start_date", "end_date"]
    if not all(data.get(f) is not None for f in required):
        return jsonify({"error": f"Missing required fields: {required}"}), 400
    try:
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Dates must be in YYYY-MM-DD format"}), 400

    trek = Trek(
        trek_name=data["trek_name"], location=data["location"], difficulty=data["difficulty"],
        duration=data["duration"], price=data.get("price", 0),
        available_slots=data["available_slots"], total_slots=data["available_slots"],
        assigned_staff_id=data.get("assigned_staff_id"), status=data.get("status", "Pending"),
        start_date=start_date, end_date=end_date,
        description=data.get("description"), image=data.get("image"),
    )
    db.session.add(trek)
    db.session.commit()
    invalidate_stats_cache()
    return jsonify({"message": "Trek created", "trek": trek.to_dict()}), 201


@api.route("/treks/<int:trek_id>", methods=["PUT"])
@jwt_required()
def update_trek(trek_id):
    claims = get_jwt()
    trek = Trek.query.get_or_404(trek_id)
    data = request.get_json() or {}

    if claims.get("role") == "staff":
        profile = StaffProfile.query.filter_by(user_id=int(get_jwt_identity())).first()
        if not profile or trek.assigned_staff_id != profile.id:
            return jsonify({"error": "You are not assigned to this trek"}), 403
        # Spec: staff may only manage available slots and trek status (Open/Closed) - nothing else.
        if "available_slots" in data:
            trek.available_slots = data["available_slots"]
        if "status" in data:
            if data["status"] not in ("Open", "Closed"):
                return jsonify({"error": "Staff can only set trek status to Open or Closed"}), 400
            trek.status = data["status"]
        db.session.commit()
        return jsonify({"message": "Trek updated", "trek": trek.to_dict()}), 200

    if claims.get("role") != "admin":
        return jsonify({"error": "Forbidden"}), 403

    for field in ["trek_name", "location", "difficulty", "description", "image", "status"]:
        if field in data:
            setattr(trek, field, data[field])
    if "price" in data:
        trek.price = data["price"]
    if "available_slots" in data:
        trek.available_slots = data["available_slots"]
    if "duration" in data:
        trek.duration = data["duration"]
    if "assigned_staff_id" in data:
        trek.assigned_staff_id = data["assigned_staff_id"]
    if "start_date" in data:
        trek.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
    if "end_date" in data:
        trek.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

    db.session.commit()
    invalidate_stats_cache()
    return jsonify({"message": "Trek updated", "trek": trek.to_dict()}), 200


@api.route("/treks/<int:trek_id>/start", methods=["PUT"])
@role_required("staff")
def start_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    trek.status = "Closed"
    db.session.commit()
    invalidate_stats_cache()
    return jsonify({"message": "Trek marked as started", "trek": trek.to_dict()}), 200


@api.route("/treks/<int:trek_id>/complete", methods=["PUT"])
@role_required("staff")
def complete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    trek.status = "Completed"
    for booking in trek.bookings:
        if booking.status == "Booked":
            booking.status = "Completed"
            booking.completed_date = datetime.utcnow()
    db.session.commit()
    invalidate_stats_cache()
    return jsonify({"message": "Trek marked as completed", "trek": trek.to_dict()}), 200


@api.route("/treks/<int:trek_id>", methods=["DELETE"])
@role_required("admin")
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    invalidate_stats_cache()
    return jsonify({"message": "Trek deleted"}), 200


@api.route("/treks/<int:trek_id>/participants", methods=["GET"])
@jwt_required()
def trek_participants(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    return jsonify({"participants": [b.to_dict() for b in trek.bookings if b.status in ("Booked", "Completed")]}), 200


# ---------- bookings ----------

@api.route("/bookings", methods=["GET"])
@jwt_required()
def list_bookings():
    claims = get_jwt()
    query = Booking.query

    if claims.get("role") == "user":
        query = query.filter_by(user_id=int(get_jwt_identity()))
    elif claims.get("role") == "staff":
        profile = StaffProfile.query.filter_by(user_id=int(get_jwt_identity())).first()
        trek_ids = [t.id for t in profile.assigned_treks] if profile else []
        query = query.filter(Booking.trek_id.in_(trek_ids))

    status = request.args.get("status")
    if status:
        query = query.filter_by(status=status)

    search = request.args.get("search")
    if search:
        like = f"%{search}%"
        query = query.join(Trek, Booking.trek_id == Trek.id).join(User, Booking.user_id == User.id).filter(
            db.or_(Trek.trek_name.ilike(like), User.name.ilike(like))
        )

    p = paginate(query.order_by(Booking.booking_date.desc()))
    return jsonify({"bookings": [b.to_dict() for b in p.items], "total": p.total, "page": p.page, "pages": p.pages}), 200


@api.route("/bookings", methods=["POST"])
@role_required("user")
def create_booking():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    trek_id = data.get("trek_id")
    if not trek_id:
        return jsonify({"error": "trek_id is required"}), 400

    trek = Trek.query.get_or_404(trek_id)

    if trek.status != "Open":
        return jsonify({"error": "This trek is not open for booking"}), 400
    if trek.start_date and trek.start_date <= date.today():
        return jsonify({"error": "Booking closed: trek has already started"}), 400
    if Booking.query.filter_by(user_id=user_id, trek_id=trek_id, status="Booked").first():
        return jsonify({"error": "You already have an active booking for this trek"}), 409
    if trek.available_slots <= 0:
        return jsonify({"error": "No slots available for this trek"}), 400

    booking = Booking(
        user_id=user_id, trek_id=trek_id, status="Booked",
        amount=trek.price, payment_method=data.get("payment_method", "Card"), payment_status="Paid",
    )
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    invalidate_stats_cache()
    return jsonify({"message": "Trek booked and payment simulated successfully", "booking": booking.to_dict()}), 201


@api.route("/bookings/<int:booking_id>/cancel", methods=["PUT"])
@jwt_required()
def cancel_booking(booking_id):
    claims = get_jwt()
    booking = Booking.query.get_or_404(booking_id)

    if claims.get("role") == "user" and booking.user_id != int(get_jwt_identity()):
        return jsonify({"error": "You can only cancel your own bookings"}), 403
    if claims.get("role") == "staff":
        return jsonify({"error": "Trekking staff can view participants but cannot cancel their bookings"}), 403
    if booking.status != "Booked":
        return jsonify({"error": "Only active bookings can be cancelled"}), 400

    booking.status = "Cancelled"
    booking.payment_status = "Refunded"
    if booking.trek:
        booking.trek.available_slots += 1
    db.session.commit()
    invalidate_stats_cache()
    return jsonify({"message": "Booking cancelled and payment refunded", "booking": booking.to_dict()}), 200


# In-memory store for fallback exports when Celery worker is offline
_sync_exports = {}


@api.route("/bookings/export", methods=["POST"])
@role_required("user")
def export_history():
    user_id = int(get_jwt_identity())
    try:
        from tasks import export_booking_history_csv
        task = export_booking_history_csv.delay(user_id)
        return jsonify({"message": "Export started. You will be notified when ready.", "task_id": task.id}), 202
    except Exception as e:
        logger.warning(f"Celery export failed ({e}), executing directly.")
        from tasks import export_booking_history_csv
        filepath = export_booking_history_csv(user_id)
        task_id = f"sync_{user_id}_{int(datetime.utcnow().timestamp())}"
        _sync_exports[task_id] = {"state": "SUCCESS", "result": filepath}
        return jsonify({"message": "Export created.", "task_id": task_id}), 202


@api.route("/bookings/export/<task_id>", methods=["GET"])
@jwt_required()
def export_status(task_id):
    if task_id in _sync_exports:
        res = _sync_exports[task_id]
        return jsonify({"state": res["state"], "file_path": res.get("result")}), 200

    try:
        from tasks import celery_app
        result = celery_app.AsyncResult(task_id)
        payload = {"state": result.state}
        if result.state == "SUCCESS":
            payload["file_path"] = result.result
        return jsonify(payload), 200
    except Exception as e:
        return jsonify({"state": "FAILURE", "error": str(e)}), 200


@api.route("/bookings/export/<task_id>/download", methods=["GET"])
@jwt_required()
def download_export(task_id):
    filepath = None
    if task_id in _sync_exports:
        filepath = _sync_exports[task_id].get("result")
    else:
        try:
            from tasks import celery_app
            result = celery_app.AsyncResult(task_id)
            if result.state != "SUCCESS":
                return jsonify({"error": "Export is not ready yet"}), 409
            filepath = result.result
        except Exception:
            return jsonify({"error": "Could not check export status"}), 500

    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "Export file not found. It may have expired - please export again."}), 404

    # The task names files "booking_history_user{id}_...csv" - make sure the
    # requester can only download their own export, not someone else's task_id.
    filename = os.path.basename(filepath)
    expected_prefix = f"booking_history_user{get_jwt_identity()}_"
    if not filename.startswith(expected_prefix):
        return jsonify({"error": "You are not authorized to download this file"}), 403

    return send_file(filepath, mimetype="text/csv", as_attachment=True, download_name=filename)


# ---------- dashboard & reports ----------

@api.route("/dashboard/admin", methods=["GET"])
@role_required("admin")
def admin_dashboard():
    cached = safe_cache_get(DASHBOARD_CACHE_KEY)
    if cached is not None:
        return jsonify(cached), 200

    treks = Trek.query.all()
    bookings = Booking.query.all()

    total_revenue = sum(b.amount for b in bookings if b.status in ("Booked", "Completed"))

    # Popular treks: count bookings per trek, in plain Python (robust across SQLite/Postgres, no SQL edge cases)
    counts = {}
    for b in bookings:
        counts[b.trek_id] = counts.get(b.trek_id, 0) + 1
    trek_by_id = {t.id: t for t in treks}
    popular = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
    popular_treks = [
        {"trek_name": trek_by_id[tid].trek_name, "count": c}
        for tid, c in popular if tid in trek_by_id
    ]

    # Monthly participation (current-year bookings), plain Python grouping
    monthly = {}
    for b in bookings:
        if b.booking_date:
            m = b.booking_date.month
            monthly[m] = monthly.get(m, 0) + 1
    monthly_participation = [{"month": m, "count": c} for m, c in sorted(monthly.items())]

    trends = {}
    for b in bookings:
        trends[b.status] = trends.get(b.status, 0) + 1
    booking_trends = [{"status": s, "count": c} for s, c in trends.items()]

    recent_bookings = sorted(bookings, key=lambda b: b.booking_date or datetime.min, reverse=True)[:5]

    payload = {
        "total_treks": len(treks),
        "total_users": User.query.filter_by(role="user").count(),
        "total_staff": User.query.filter_by(role="staff").count(),
        "total_bookings": len(bookings),
        "total_revenue": total_revenue,
        "recent_bookings": [b.to_dict() for b in recent_bookings],
        "popular_treks": popular_treks,
        "monthly_participation": monthly_participation,
        "booking_trends": booking_trends,
    }
    safe_cache_set(DASHBOARD_CACHE_KEY, payload, timeout=Config.CACHE_DEFAULT_TIMEOUT)
    return jsonify(payload), 200


@api.route("/dashboard/user", methods=["GET"])
@role_required("user")
def user_dashboard():
    user_id = int(get_jwt_identity())
    upcoming = Booking.query.filter_by(user_id=user_id, status="Booked").join(Trek).order_by(Trek.start_date.asc()).all()
    completed = Booking.query.filter_by(user_id=user_id, status="Completed").all()
    all_bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()
    available_treks = Trek.query.filter_by(status="Open").order_by(Trek.start_date.asc()).limit(6).all()

    return jsonify({
        "upcoming_bookings": [b.to_dict() for b in upcoming],
        "completed_treks": [b.to_dict() for b in completed],
        "booking_history": [b.to_dict() for b in all_bookings],
        "available_treks": [t.to_dict() for t in available_treks],
    }), 200


@api.route("/reports", methods=["GET"])
@role_required("admin")
def full_report():
    cached = safe_cache_get(REPORTS_CACHE_KEY)
    if cached is not None:
        return jsonify(cached), 200

    bookings = Booking.query.all()
    treks = Trek.query.all()

    location_counts = {}
    for b in bookings:
        if b.trek:
            location_counts[b.trek.location] = location_counts.get(b.trek.location, 0) + 1
    popular_destinations = sorted(
        [{"location": loc, "count": c} for loc, c in location_counts.items()],
        key=lambda x: x["count"], reverse=True
    )[:5]

    monthly = {}
    for b in bookings:
        if b.booking_date:
            m = b.booking_date.month
            monthly[m] = monthly.get(m, 0) + 1
    monthly_participation = [{"month": m, "count": c} for m, c in sorted(monthly.items())]

    payload = {
        "total_users": User.query.filter_by(role="user").count(),
        "total_staff": User.query.filter_by(role="staff").count(),
        "total_bookings": len(bookings),
        "total_revenue": sum(b.amount for b in bookings if b.status in ("Booked", "Completed")),
        "active_treks": len([t for t in treks if t.status in ("Open", "Approved")]),
        "completed_treks": len([t for t in treks if t.status == "Completed"]),
        "popular_destinations": popular_destinations,
        "monthly_participation": monthly_participation,
    }
    safe_cache_set(REPORTS_CACHE_KEY, payload, timeout=Config.CACHE_DEFAULT_TIMEOUT)
    return jsonify(payload), 200

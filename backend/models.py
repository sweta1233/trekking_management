from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False, default="user")  # admin | staff | user
    status = db.Column(db.String(20), nullable=False, default="active")  # active | inactive | blacklisted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="user", lazy=True, cascade="all, delete-orphan")
    staff_profile = db.relationship("StaffProfile", backref="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "email": self.email, "phone": self.phone,
            "role": self.role, "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False, default="Easy")  # Easy | Moderate | Hard
    duration = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False, default=0)  # price per person
    available_slots = db.Column(db.Integer, nullable=False, default=0)
    total_slots = db.Column(db.Integer, nullable=False, default=0)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("staff_profiles.id"), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Pending")  # Pending|Approved|Open|Closed|Completed
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("Booking", backref="trek", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_staff=False):
        data = {
            "id": self.id, "trek_name": self.trek_name, "location": self.location,
            "difficulty": self.difficulty, "duration": self.duration, "price": self.price,
            "available_slots": self.available_slots, "total_slots": self.total_slots,
            "assigned_staff_id": self.assigned_staff_id, "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "description": self.description, "image": self.image,
        }
        if include_staff and self.assigned_staff_id and self.assigned_staff and self.assigned_staff.user:
            data["assigned_staff_name"] = self.assigned_staff.user.name
        return data


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="Booked")  # Booked|Cancelled|Completed
    amount = db.Column(db.Float, nullable=False, default=0)  # price charged at time of booking
    payment_method = db.Column(db.String(20), default="Card")  # Card | UPI | Cash
    payment_status = db.Column(db.String(20), nullable=False, default="Paid")
    completed_date = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else None,
            "trek_id": self.trek_id,
            "trek_name": self.trek.trek_name if self.trek else None,
            "location": self.trek.location if self.trek else None,
            "start_date": self.trek.start_date.isoformat() if self.trek and self.trek.start_date else None,
            "end_date": self.trek.end_date.isoformat() if self.trek and self.trek.end_date else None,
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "status": self.status,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
        }


class StaffProfile(db.Model):
    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    contact_number = db.Column(db.String(20))
    specialization = db.Column(db.String(150))
    experience_years = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), nullable=False, default="active")  # active | blacklisted

    assigned_treks = db.relationship("Trek", backref="assigned_staff", lazy=True,
                                      foreign_keys="Trek.assigned_staff_id")

    def to_dict(self):
        return {
            "id": self.id, "user_id": self.user_id,
            "name": self.user.name if self.user else None,
            "email": self.user.email if self.user else None,
            "contact_number": self.contact_number, "specialization": self.specialization,
            "experience_years": self.experience_years, "status": self.status,
            "assigned_treks_count": len(self.assigned_treks) if self.assigned_treks else 0,
        }

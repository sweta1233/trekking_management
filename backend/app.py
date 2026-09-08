import os
from flask import Flask, jsonify, render_template
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_cors import CORS

from config import Config, INSTANCE_DIR
from models import db, User

jwt = JWTManager()
cache = Cache()


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)

    os.makedirs(INSTANCE_DIR, exist_ok=True)
    os.makedirs(Config.EXPORT_FOLDER, exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    from routes import api
    app.register_blueprint(api)

    @jwt.unauthorized_loader
    def unauthorized(reason):
        return jsonify({"error": "Missing or invalid token", "detail": reason}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"error": "Invalid token", "detail": reason}), 422

    @jwt.expired_token_loader
    def expired_token(header, payload):
        return jsonify({"error": "Token has expired"}), 401

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/")
    def index():
        return jsonify({"message": "TMA Backend API is running", "status": "ok"}), 200

    @app.route("/health")
    @app.route("/api/health")
    def health():
        return jsonify({"status": "healthy", "service": "TMA Backend"}), 200

    with app.app_context():
        db.create_all()
        _auto_migrate()
        seed_admin()

    return app


def _auto_migrate():
    """
    Safely adds missing columns if running against an older schema.
    Uses SQLAlchemy inspector to work across both SQLite and PostgreSQL.
    """
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()

        if "treks" in table_names:
            trek_cols = {col["name"] for col in inspector.get_columns("treks")}
            with db.engine.connect() as conn:
                if "price" not in trek_cols:
                    conn.execute(text("ALTER TABLE treks ADD COLUMN price FLOAT DEFAULT 0"))
                    conn.commit()
                    print("[TMA] Migrated: added 'price' column to treks table")

        if "bookings" in table_names:
            booking_cols = {col["name"] for col in inspector.get_columns("bookings")}
            with db.engine.connect() as conn:
                if "amount" not in booking_cols:
                    conn.execute(text("ALTER TABLE bookings ADD COLUMN amount FLOAT DEFAULT 0"))
                    conn.commit()
                    print("[TMA] Migrated: added 'amount' column to bookings table")
                if "payment_method" not in booking_cols:
                    conn.execute(text("ALTER TABLE bookings ADD COLUMN payment_method VARCHAR(20) DEFAULT 'Card'"))
                    conn.commit()
                    print("[TMA] Migrated: added 'payment_method' column to bookings table")
                if "payment_status" not in booking_cols:
                    conn.execute(text("ALTER TABLE bookings ADD COLUMN payment_status VARCHAR(20) DEFAULT 'Paid'"))
                    conn.commit()
                    print("[TMA] Migrated: added 'payment_status' column to bookings table")
    except Exception as e:
        print(f"[TMA] Auto-migration check notice: {e}")


def seed_admin():
    if not User.query.filter_by(role="admin").first():
        admin = User(name=Config.DEFAULT_ADMIN_NAME, email=Config.DEFAULT_ADMIN_EMAIL, role="admin", status="active")
        admin.set_password(Config.DEFAULT_ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"[TMA] Default admin created -> email: {Config.DEFAULT_ADMIN_EMAIL} / password: {Config.DEFAULT_ADMIN_PASSWORD}")


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instances")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "tma-dev-secret-key")

    # Database: Use DATABASE_URL if available (Render Postgres / Supabase / Neon etc.), otherwise SQLite
    _db_url = os.environ.get("DATABASE_URL")
    if _db_url and _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url or ("sqlite:///" + os.path.join(INSTANCE_DIR, "tma.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "tma-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 8  # 8 hours

    REDIS_URL = os.environ.get("REDIS_URL", "")
    # Default to RedisCache only if REDIS_URL is provided, otherwise use SimpleCache (in-memory)
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "RedisCache" if REDIS_URL else "SimpleCache")
    CACHE_REDIS_URL = REDIS_URL if REDIS_URL else "redis://localhost:6379/0"
    CACHE_DEFAULT_TIMEOUT = 300

    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", REDIS_URL or "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", REDIS_URL or "redis://localhost:6379/1")

    EXPORT_FOLDER = os.path.join(INSTANCE_DIR, "exports")

    DEFAULT_ADMIN_NAME = "System Admin"
    DEFAULT_ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@tma.com")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@123")

    GOOGLE_CHAT_WEBHOOK_URL = os.environ.get("GOOGLE_CHAT_WEBHOOK_URL", "")

    # Default MAIL_* values point at a local MailHog instance (smtp on 1025, UI on 8025).
    # MailHog needs no auth and no TLS, so both are off by default.
    MAIL_ENABLED = os.environ.get("MAIL_ENABLED", "true").lower() == "true"
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 1025))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_FROM = os.environ.get("MAIL_FROM", "no-reply@tma.local")

    CURRENCY_SYMBOL = "₹"


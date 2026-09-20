import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instances")
DATA_DIR = os.path.join(BASE_DIR, "data")
UPLOADS_DIR = os.path.join(INSTANCE_DIR, "uploads")
DOCS_DIR = os.path.join(INSTANCE_DIR, "documents")
VECTOR_STORE_DIR = os.path.join(INSTANCE_DIR, "faiss_index")
ML_MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "trekmate-ai-secret-key-2026")

    # Database: Use DATABASE_URL if available (Postgres/SQLite), else fallback to SQLite
    _raw_db_url = os.environ.get("DATABASE_URL", "").strip()
    _db_url = None
    if _raw_db_url:
        if _raw_db_url.startswith("postgres://"):
            _db_url = _raw_db_url.replace("postgres://", "postgresql://", 1)
        elif _raw_db_url.startswith(("postgresql://", "sqlite:///", "mysql://", "mariadb://")):
            _db_url = _raw_db_url
        else:
            print(f"[TrekMate Config] Warning: DATABASE_URL format unsupported. Falling back to SQLite.")

    SQLALCHEMY_DATABASE_URI = _db_url or ("sqlite:///" + os.path.join(INSTANCE_DIR, "tma.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Authentication
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "trekmate-ai-jwt-key-2026")
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24  # 24 hours

    # Caching
    REDIS_URL = os.environ.get("REDIS_URL", "")
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "RedisCache" if REDIS_URL else "SimpleCache")
    CACHE_REDIS_URL = REDIS_URL if REDIS_URL else "redis://localhost:6379/0"
    CACHE_DEFAULT_TIMEOUT = 300

    # Folders
    EXPORT_FOLDER = os.path.join(INSTANCE_DIR, "exports")
    UPLOADS_FOLDER = UPLOADS_DIR
    DOCUMENTS_FOLDER = DOCS_DIR
    VECTOR_STORE_PATH = VECTOR_STORE_DIR
    ML_MODEL_PATH = os.path.join(ML_MODELS_DIR, "trek_demand_model.joblib")

    # Default Seed Admin & Credentials
    DEFAULT_ADMIN_NAME = "Admin Commander"
    DEFAULT_ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@tma.com")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@123")

    # LLM Configuration (Configurable via Environment Variables)
    # Providers: "openai", "anthropic", "gemini", "mock" (offline fallback)
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "mock").lower()
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

    # Embeddings Configuration
    EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "mock").lower()  # "openai", "huggingface", "mock"
    EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")

    # RAG Settings
    RAG_CHUNK_SIZE = int(os.environ.get("RAG_CHUNK_SIZE", 600))
    RAG_CHUNK_OVERLAP = int(os.environ.get("RAG_CHUNK_OVERLAP", 120))
    RAG_TOP_K = int(os.environ.get("RAG_TOP_K", 4))
    RAG_SIMILARITY_THRESHOLD = float(os.environ.get("RAG_SIMILARITY_THRESHOLD", 0.05))

    # General Settings
    CURRENCY_SYMBOL = "₹"
    APP_NAME = "TrekMate AI"

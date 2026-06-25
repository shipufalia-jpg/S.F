import os

class Config:

    # 🔐 Secret Key
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev_secret_key"
    )

    # ================= DATABASE =================
    DATABASE_URL = os.environ.get("DATABASE_URL")

    if DATABASE_URL:
        # Render fix
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace(
            "postgres://",
            "postgresql://"
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///local.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ================= REDIS =================
    REDIS_URL = os.environ.get(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )

    # ================= UPLOAD =================
    BASE_DIR = os.path.abspath(
        os.path.dirname(__file__)
    )

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "uploads"
    )

    # 2MB max upload
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

    # ================= SESSION =================
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_PERMANENT = False
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True

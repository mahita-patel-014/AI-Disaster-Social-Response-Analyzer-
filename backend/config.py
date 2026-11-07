import os
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# MONGODB
# ============================================================

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://127.0.0.1:27017"
)

MONGO_DB_NAME = os.getenv(
    "MONGO_DB_NAME",
    "ai_final_disaster"
)

# Compatibility with backend/database/db.py
MONGO_DB = MONGO_DB_NAME


# ============================================================
# FRONTEND CORS
# ============================================================

FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:5501,http://localhost:5501"
    ).split(",")
    if origin.strip()
]


# ============================================================
# ADMIN
# ============================================================

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

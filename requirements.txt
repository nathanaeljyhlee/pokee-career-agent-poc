import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "career_platform.db"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

WORKDAY_MODE = os.getenv("WORKDAY_MODE", "mock")  # "mock" or "live"
WORKDAY_API_URL = os.getenv("WORKDAY_API_URL", "")
WORKDAY_TENANT = os.getenv("WORKDAY_TENANT", "babson_college")

ONET_BASE_URL = "https://services.onetcenter.org/ws"
BLS_BASE_URL = "https://api.bls.gov/publicAPI/v2"

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

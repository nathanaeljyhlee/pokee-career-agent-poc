import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "career_platform.db"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

INTELLIGENCE_MODE = os.getenv("INTELLIGENCE_MODE", "offline").lower()
OFFLINE_LLM_PROVIDER = os.getenv("OFFLINE_LLM_PROVIDER", "ollama").lower()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3.1")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")

AI_EXTRACTION_TIMEOUT = float(os.getenv("AI_EXTRACTION_TIMEOUT", "20"))
AI_EMBED_TIMEOUT = float(os.getenv("AI_EMBED_TIMEOUT", "15"))
AI_ADVISOR_TIMEOUT = float(os.getenv("AI_ADVISOR_TIMEOUT", "20"))

WORKDAY_MODE = os.getenv("WORKDAY_MODE", "mock")  # "mock" or "live"
WORKDAY_API_URL = os.getenv("WORKDAY_API_URL", "")
WORKDAY_TENANT = os.getenv("WORKDAY_TENANT", "babson_college")

ONET_BASE_URL = "https://services.onetcenter.org/ws"
BLS_BASE_URL = "https://api.bls.gov/publicAPI/v2"

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

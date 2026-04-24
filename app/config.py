import os
import secrets
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data")).resolve()
VECTORSTORE_DIR = Path(os.getenv("VECTORSTORE_DIR", BASE_DIR / "vectorstore")).resolve()

DEFAULT_DATABASE_URL = f"sqlite:///{(DATA_DIR / 'users.db').as_posix()}"


def _normalize_origins(raw_value: str | None) -> list[str]:
    if not raw_value:
        return ["*"]
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> dict[str, object]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        secret_key = secrets.token_urlsafe(32)

    return {
        "app_name": os.getenv("APP_NAME", "CloudSec RAG Agent"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database_url": os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
        "secret_key": secret_key,
        "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")),
        "ollama_url": os.getenv("OLLAMA_URL", "").strip(),
        "ollama_model": os.getenv("OLLAMA_MODEL", "phi3:mini"),
        "ollama_num_predict": int(os.getenv("OLLAMA_NUM_PREDICT", "192")),
        "request_timeout_seconds": int(os.getenv("REQUEST_TIMEOUT_SECONDS", "45")),
        "backend_url": os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/"),
        "api_base_url": os.getenv("CLOUDSEC_API_URL", os.getenv("BACKEND_URL", "http://127.0.0.1:8000")).rstrip("/"),
        "port": int(os.getenv("PORT", "8000")),
        "host": os.getenv("HOST", "0.0.0.0"),
        "cors_origins": _normalize_origins(os.getenv("CORS_ORIGINS")),
        "max_query_chars": int(os.getenv("MAX_QUERY_CHARS", "4000")),
        "max_attachment_chars": int(os.getenv("MAX_ATTACHMENT_CHARS", "12000")),
        "max_attachment_count": int(os.getenv("MAX_ATTACHMENT_COUNT", "5")),
        "data_dir": DATA_DIR,
        "vectorstore_dir": VECTORSTORE_DIR,
    }

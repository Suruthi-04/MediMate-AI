import os
import json
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MediMate AI – Personal Health Copilot"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    SAMPLE_DIR: Path = BASE_DIR / "sample_files"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{(BASE_DIR / 'medimate.db').as_posix()}"
    
    # Security & limits
    MAX_FILE_SIZE_MB: int = 15
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".png", ".jpg", ".jpeg"]
    ALLOWED_MIME_TYPES: List[str] = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg",
    ]
    
    # External AI keys (Optional - prototype runs in enriched Demo Mode if not present)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    FORCE_DEMO_MODE: bool = False
    
    # CORS (Configurable via CORS_ORIGINS or FRONTEND_URL env vars)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "")
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            val = v.strip()
            if not val:
                return [
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                    "http://localhost:3000",
                ]
            if val.startswith("[") and val.endswith("]"):
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except Exception:
                    pass
            return [item.strip() for item in val.split(",") if item.strip()]
        return v

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()

# Dynamically ensure FRONTEND_URL is included in allowed CORS origins if configured
if settings.FRONTEND_URL:
    clean_frontend_url = settings.FRONTEND_URL.strip().rstrip("/")
    if clean_frontend_url and clean_frontend_url not in settings.CORS_ORIGINS:
        settings.CORS_ORIGINS.append(clean_frontend_url)

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.config import settings
from app.database import get_db, Base, engine
from app.services.ocr_service import ocr_service
from app.services.ai_service import ai_service
from app.services.sample_data import seed_sample_database

router = APIRouter(prefix="/settings", tags=["Settings & System"])

class KeyUpdateRequest(BaseModel):
    gemini_api_key: Optional[str] = None
    force_demo_mode: Optional[bool] = None

@router.get("/status")
def get_system_status(db: Session = Depends(get_db)):
    """System health check and environmental status."""
    has_gemini = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
    is_tesseract = ocr_service.is_tesseract_available()
    
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "tesseract_installed": is_tesseract,
        "pdf_extraction": "pypdf Direct Engine (Active)",
        "gemini_api_key_configured": has_gemini,
        "active_ai_provider": ai_service.get_active_model_name(),
        "is_demo_mode": ai_service.is_demo_mode(),
        "database": "SQLite (FHIR-inspired Schema)",
        "max_upload_size_mb": settings.MAX_FILE_SIZE_MB,
        "supported_formats": settings.ALLOWED_EXTENSIONS
    }

@router.post("/seed-data")
def seed_data(db: Session = Depends(get_db)):
    """Seed synthetic patient records and demo reports."""
    patient = seed_sample_database(db)
    return {
        "status": "success",
        "message": f"Demo dataset successfully seeded for Patient {patient.name} ({patient.identifier})."
    }

@router.post("/reset-database")
def reset_database(db: Session = Depends(get_db)):
    """Reset database tables and re-populate fresh demo data."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    patient = seed_sample_database(db)
    return {
        "status": "success",
        "message": "Database cleared and re-initialized with synthetic demo records."
    }

@router.post("/update-api-key")
def update_api_key(payload: KeyUpdateRequest):
    """Dynamically set or clear Gemini API key for testing during hackathon judging."""
    if payload.gemini_api_key is not None:
        settings.GEMINI_API_KEY = payload.gemini_api_key.strip()
    if payload.force_demo_mode is not None:
        settings.FORCE_DEMO_MODE = payload.force_demo_mode

    return {
        "status": "success",
        "gemini_api_key_configured": bool(settings.GEMINI_API_KEY),
        "force_demo_mode": settings.FORCE_DEMO_MODE,
        "active_ai_provider": ai_service.get_active_model_name(),
        "is_demo_mode": ai_service.is_demo_mode()
    }

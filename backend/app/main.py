
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.services.sample_data import (
    seed_sample_database,
    generate_sample_files,
)
from app.models.fhir import Patient

# Routers
from app.routers import (
    documents,
    fhir_crud,
    timeline,
    ai_summary,
    settings as settings_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)

    # Generate sample files
    generate_sample_files()

    # Seed demo data if database is empty
    db = SessionLocal()
    try:
        patient_count = db.query(Patient).count()
        if patient_count == 0:
            seed_sample_database(db)
    finally:
        db.close()

    yield


# FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "MediMate AI - Personal Health Copilot "
        "for HacXLerate 2026 Round 1 Challenge 1"
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file mounts
app.mount(
    "/static/uploads",
    StaticFiles(directory=str(settings.UPLOAD_DIR)),
    name="uploads",
)

app.mount(
    "/static/samples",
    StaticFiles(directory=str(settings.SAMPLE_DIR)),
    name="samples",
)

# API routers
app.include_router(
    documents.router,
    prefix=settings.API_V1_STR,
)
app.include_router(
    fhir_crud.router,
    prefix=settings.API_V1_STR,
)
app.include_router(
    timeline.router,
    prefix=settings.API_V1_STR,
)
app.include_router(
    ai_summary.router,
    prefix=settings.API_V1_STR,
)
app.include_router(
    settings_router.router,
    prefix=settings.API_V1_STR,
)


# Root endpoint
@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "challenge": (
            "HacXLerate 2026 Round 1 - Challenge 1: "
            "AI-Powered Personal Health Copilot"
        ),
        "status": "online",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
    }


# Health check endpoint
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }
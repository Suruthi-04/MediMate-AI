
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

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
    # Initialize SQLite database tables
    Base.metadata.create_all(bind=engine)

    # Ensure sample PDF and image files exist
    generate_sample_files()

    # Seed demo data if database is fresh
    db = SessionLocal()
    try:
        patient_count = db.query(Patient).count()
        if patient_count == 0:
            seed_sample_database(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "MediMate AI – Personal Health Copilot "
        "for HacXLerate 2026 Round 1 Challenge 1"
    ),
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file mounts for previews
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

# Include API routers
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(fhir_crud.router, prefix=settings.API_V1_STR)
app.include_router(timeline.router, prefix=settings.API_V1_STR)
app.include_router(ai_summary.router, prefix=settings.API_V1_STR)
app.include_router(settings_router.router, prefix=settings.API_V1_STR)


# Manual OpenAPI schema endpoint
@app.get("/openapi.json", include_in_schema=False)
def custom_openapi():
    schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="MediMate AI Personal Health Copilot API",
        routes=app.routes,
    )
    return JSONResponse(content=schema)


# Manual Swagger UI endpoint
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.PROJECT_NAME} - API Docs",
    )


# Root endpoint
@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "challenge": (
            "HacXLerate 2026 Round 1 - "
            "Challenge 1: AI-Powered Personal Health Copilot"
        ),
        "status": "online",
        "docs_url": "/docs",
    }


# Health check endpoint
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }

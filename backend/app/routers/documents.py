import os
import json
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.fhir import Patient, DocumentReference, Observation, Condition, MedicationStatement
from app.schemas.report_schemas import DocumentReferenceOut
from app.services.ocr_service import ocr_service
from app.services.parser_service import parser_service
from app.services.ai_service import ai_service

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentReferenceOut)
async def upload_document(
    file: UploadFile = File(...),
    doc_title: Optional[str] = Form(None),
    patient_id: int = Form(1),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze medical document (PDF, PNG, JPG).
    Extracts text, parses structured entities, runs AI health summary,
    and records to SQLite database.
    """
    # 1. File format validation
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file_ext}'. Allowed formats: PDF, PNG, JPG, JPEG."
        )

    # 2. File size validation and persistence
    upload_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    saved_file_path = settings.UPLOAD_DIR / upload_filename

    try:
        with open(saved_file_path, "wb") as buffer:
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
                )

            buffer.write(content)
        file_size = len(content)
    except HTTPException:
        if saved_file_path.exists():
            saved_file_path.unlink()
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # 3. Document text extraction (OCR / PDF)
    try:
        raw_text, ocr_confidence = ocr_service.process_file(saved_file_path, file.content_type or "")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}")

    # 4. Extract metadata, tests, medications & conditions
    meta = parser_service.detect_document_metadata(raw_text)
    title = doc_title.strip() if doc_title and doc_title.strip() else f"{meta['doc_type']} - {meta['report_date']}"

    parsed_observations = parser_service.parse_observations(raw_text)
    parsed_meds, parsed_conditions = parser_service.parse_medications_and_conditions(raw_text)

    # 5. AI Summary Generation (English & Tamil with medical safety guardrails)
    ai_result = ai_service.generate_health_summary(
        title, meta["doc_type"], raw_text, parsed_observations, parsed_meds, parsed_conditions
    )

    # 6. Verify or initialize Patient
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        patient = Patient(id=patient_id, identifier="PAT-HACX-2026", name="Arun Kumar")
        db.add(patient)
        db.commit()
        db.refresh(patient)

    # 7. Persist DocumentReference
    doc_ref = DocumentReference(
        patient_id=patient.id,
        title=title,
        doc_type=meta["doc_type"],
        category="diagnostic-report",
        file_name=file.filename,
        file_path=str(saved_file_path),
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream",
        report_date=meta["report_date"],
        facility_name=meta["facility_name"],
        doctor_name=meta["doctor_name"],
        status="current",
        raw_extracted_text=raw_text,
        summary_en=ai_result["summary_en"],
        summary_ta=ai_result["summary_ta"],
        key_findings_json=json.dumps(ai_result["key_findings"]),
        doctor_questions_json=json.dumps(ai_result["doctor_questions"]),
        ai_model=ai_result["ai_model"],
        is_demo_mode=ai_result["is_demo_mode"]
    )
    db.add(doc_ref)
    db.flush()

    # 8. Persist Observations
    for obs in parsed_observations:
        observation = Observation(
            document_id=doc_ref.id,
            patient_id=patient.id,
            display_name=obs["display_name"],
            category=obs.get("category", "laboratory"),
            value_string=obs["value_string"],
            value_quantity=obs.get("value_quantity"),
            unit=obs.get("unit"),
            reference_range_low=obs.get("reference_range_low"),
            reference_range_high=obs.get("reference_range_high"),
            reference_range_text=obs.get("reference_range_text"),
            interpretation=obs.get("interpretation", "Normal"),
            is_uncertain=obs.get("is_uncertain", False),
            confidence_score=obs.get("confidence_score", 0.95),
            notes=obs.get("notes")
        )
        db.add(observation)

    # 9. Persist Conditions
    for cond in parsed_conditions:
        c = Condition(
            document_id=doc_ref.id,
            patient_id=patient.id,
            display_name=cond["display_name"],
            clinical_status=cond.get("clinical_status", "active"),
            verification_status=cond.get("verification_status", "provisional"),
            recorded_date=cond.get("recorded_date", meta["report_date"]),
            notes=cond.get("notes")
        )
        db.add(c)

    # 10. Persist Medications
    for med in parsed_meds:
        m = MedicationStatement(
            document_id=doc_ref.id,
            patient_id=patient.id,
            medication_name=med["medication_name"],
            dosage_instruction=med.get("dosage_instruction"),
            frequency=med.get("frequency"),
            status=med.get("status", "active"),
            notes=med.get("notes")
        )
        db.add(m)

    db.commit()
    db.refresh(doc_ref)
    return doc_ref


@router.post("/load-sample", response_model=DocumentReferenceOut)
def load_sample_document(
    sample_key: str = Query("cbc", description="'cbc' or 'lipid'"),
    patient_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """
    1-Click demonstration endpoint: loads, extracts and summarizes
    one of the pre-generated sample medical reports without needing manual file upload.
    """
    if sample_key == "lipid":
        sample_path = settings.SAMPLE_DIR / "sample_diabetic_lipid_report.pdf"
        title = "Metabolic & Lipid Panel Evaluation (Sample)"
    else:
        sample_path = settings.SAMPLE_DIR / "sample_cbc_report.pdf"
        title = "Complete Blood Count Examination (Sample)"

    if not sample_path.exists():
        from app.services.sample_data import generate_sample_files
        generate_sample_files()

    # Extract text from sample file
    raw_text, _ = ocr_service.process_file(sample_path, "application/pdf")
    meta = parser_service.detect_document_metadata(raw_text)
    parsed_observations = parser_service.parse_observations(raw_text)
    parsed_meds, parsed_conditions = parser_service.parse_medications_and_conditions(raw_text)

    ai_result = ai_service.generate_health_summary(
        title, meta["doc_type"], raw_text, parsed_observations, parsed_meds, parsed_conditions
    )

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        patient = Patient(id=patient_id, identifier="PAT-HACX-2026", name="Arun Kumar")
        db.add(patient)
        db.commit()
        db.refresh(patient)

    doc_ref = DocumentReference(
        patient_id=patient.id,
        title=title,
        doc_type=meta["doc_type"],
        category="diagnostic-report",
        file_name=sample_path.name,
        file_path=str(sample_path),
        file_size=sample_path.stat().st_size,
        mime_type="application/pdf",
        report_date=meta["report_date"],
        facility_name=meta["facility_name"],
        doctor_name=meta["doctor_name"],
        status="current",
        raw_extracted_text=raw_text,
        summary_en=ai_result["summary_en"],
        summary_ta=ai_result["summary_ta"],
        key_findings_json=json.dumps(ai_result["key_findings"]),
        doctor_questions_json=json.dumps(ai_result["doctor_questions"]),
        ai_model=ai_result["ai_model"],
        is_demo_mode=ai_result["is_demo_mode"]
    )
    db.add(doc_ref)
    db.flush()

    for obs in parsed_observations:
        observation = Observation(
            document_id=doc_ref.id,
            patient_id=patient.id,
            display_name=obs["display_name"],
            category=obs.get("category", "laboratory"),
            value_string=obs["value_string"],
            value_quantity=obs.get("value_quantity"),
            unit=obs.get("unit"),
            reference_range_low=obs.get("reference_range_low"),
            reference_range_high=obs.get("reference_range_high"),
            reference_range_text=obs.get("reference_range_text"),
            interpretation=obs.get("interpretation", "Normal"),
            is_uncertain=obs.get("is_uncertain", False),
            confidence_score=obs.get("confidence_score", 0.95),
            notes=obs.get("notes")
        )
        db.add(observation)

    for cond in parsed_conditions:
        c = Condition(
            document_id=doc_ref.id,
            patient_id=patient.id,
            display_name=cond["display_name"],
            clinical_status=cond.get("clinical_status", "active"),
            verification_status=cond.get("verification_status", "confirmed"),
            recorded_date=cond.get("recorded_date", meta["report_date"]),
            notes=cond.get("notes")
        )
        db.add(c)

    for med in parsed_meds:
        m = MedicationStatement(
            document_id=doc_ref.id,
            patient_id=patient.id,
            medication_name=med["medication_name"],
            dosage_instruction=med.get("dosage_instruction"),
            frequency=med.get("frequency"),
            status=med.get("status", "active"),
            notes=med.get("notes")
        )
        db.add(m)

    db.commit()
    db.refresh(doc_ref)
    return doc_ref


@router.get("", response_model=List[DocumentReferenceOut])
def get_all_documents(
    doc_type: Optional[str] = None,
    patient_id: int = 1,
    db: Session = Depends(get_db)
):
    """Retrieve all uploaded documents for patient, optionally filtered by type."""
    query = db.query(DocumentReference).filter(DocumentReference.patient_id == patient_id)
    if doc_type:
        query = query.filter(DocumentReference.doc_type.ilike(f"%{doc_type}%"))
    return query.order_by(DocumentReference.created_at.desc()).all()


@router.get("/{doc_id}", response_model=DocumentReferenceOut)
def get_document_by_id(doc_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific document."""
    doc = db.query(DocumentReference).filter(DocumentReference.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """Delete document and cascading records."""
    doc = db.query(DocumentReference).filter(DocumentReference.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Optionally delete physical file
    try:
        fpath = Path(doc.file_path)
        if fpath.exists() and "uploads" in str(fpath):
            fpath.unlink()
    except Exception:
        pass

    db.delete(doc)
    db.commit()
    return {"status": "success", "message": f"Document {doc_id} successfully deleted"}


@router.get("/{doc_id}/raw-text")
def get_document_raw_text(doc_id: int, db: Session = Depends(get_db)):
    """Retrieve the original extracted raw text for auditability and verification."""
    doc = db.query(DocumentReference).filter(DocumentReference.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "title": doc.title,
        "raw_extracted_text": doc.raw_extracted_text or "[No raw text stored]"
    }

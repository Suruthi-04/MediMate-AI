import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fhir import DocumentReference, Observation, Condition, MedicationStatement
from app.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["AI Copilot"])

@router.post("/documents/{doc_id}/regenerate-summary")
def regenerate_document_summary(doc_id: int, db: Session = Depends(get_db)):
    """
    Recomputes the AI health summary in English and Tamil based on
    current (potentially user-corrected) lab observations and medications.
    """
    doc = db.query(DocumentReference).filter(DocumentReference.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    obs_list = [
        {
            "display_name": o.display_name,
            "category": o.category,
            "value_string": o.value_string,
            "unit": o.unit,
            "reference_range_text": o.reference_range_text,
            "interpretation": o.interpretation
        }
        for o in doc.observations
    ]

    med_list = [
        {
            "medication_name": m.medication_name,
            "dosage_instruction": m.dosage_instruction
        }
        for m in doc.medications
    ]

    cond_list = [
        {"display_name": c.display_name}
        for c in doc.conditions
    ]

    summary = ai_service.generate_health_summary(
        doc.title, doc.doc_type, doc.raw_extracted_text or "",
        obs_list, med_list, cond_list
    )

    doc.summary_en = summary["summary_en"]
    doc.summary_ta = summary["summary_ta"]
    doc.key_findings_json = json.dumps(summary["key_findings"])
    doc.doctor_questions_json = json.dumps(summary["doctor_questions"])
    doc.ai_model = summary["ai_model"]
    doc.is_demo_mode = summary["is_demo_mode"]

    db.commit()
    db.refresh(doc)

    return {
        "status": "success",
        "doc_id": doc.id,
        "summary_en": doc.summary_en,
        "summary_ta": doc.summary_ta,
        "key_findings": summary["key_findings"],
        "doctor_questions": summary["doctor_questions"],
        "ai_model": doc.ai_model,
        "is_demo_mode": doc.is_demo_mode
    }

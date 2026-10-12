from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.fhir import Patient, DocumentReference, Observation, Condition, MedicationStatement
from app.schemas.report_schemas import DashboardStatsOut, DocumentReferenceOut, ObservationOut
from app.services.ai_service import ai_service

router = APIRouter(tags=["Timeline & Analytics"])

@router.get("/timeline")
def get_health_timeline(
    doc_type: Optional[str] = None,
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    patient_id: int = 1,
    db: Session = Depends(get_db)
):
    """
    Unified chronological health timeline displaying all uploaded medical records,
    test counts, abnormal indicators, and diagnosed conditions.
    """
    query = db.query(DocumentReference).filter(DocumentReference.patient_id == patient_id)
    if doc_type and doc_type != "All":
        query = query.filter(DocumentReference.doc_type.ilike(f"%{doc_type}%"))

    if sort_order == "asc":
        docs = query.order_by(DocumentReference.report_date.asc(), DocumentReference.created_at.asc()).all()
    else:
        docs = query.order_by(DocumentReference.report_date.desc(), DocumentReference.created_at.desc()).all()

    timeline_items = []
    for doc in docs:
        obs_count = len(doc.observations)
        abnormal_count = sum(1 for o in doc.observations if o.interpretation in ["High", "Low", "Critical"])
        
        timeline_items.append({
            "id": doc.id,
            "title": doc.title,
            "doc_type": doc.doc_type,
            "report_date": doc.report_date or doc.created_at.strftime("%Y-%m-%d"),
            "facility_name": doc.facility_name,
            "doctor_name": doc.doctor_name,
            "file_name": doc.file_name,
            "total_observations": obs_count,
            "abnormal_observations": abnormal_count,
            "medications_count": len(doc.medications),
            "conditions": [c.display_name for c in doc.conditions],
            "ai_model": doc.ai_model,
            "is_demo_mode": doc.is_demo_mode,
            "created_at": doc.created_at.isoformat() if doc.created_at else None
        })

    return {
        "total_records": len(timeline_items),
        "timeline": timeline_items
    }


@router.get("/dashboard/stats", response_model=DashboardStatsOut)
def get_dashboard_statistics(
    patient_id: int = 1,
    db: Session = Depends(get_db)
):
    """
    Calculates summary metric counters, recent uploads, abnormal highlights,
    and preview timeline for the main dashboard view.
    """
    docs = db.query(DocumentReference).filter(DocumentReference.patient_id == patient_id).order_by(DocumentReference.created_at.desc()).all()
    total_reports = len(docs)
    
    all_obs = db.query(Observation).filter(Observation.patient_id == patient_id).all()
    total_tests = len(all_obs)
    abnormal_obs = [o for o in all_obs if o.interpretation in ["High", "Low", "Critical"]]
    abnormal_count = len(abnormal_obs)

    meds_count = db.query(MedicationStatement).filter(
        MedicationStatement.patient_id == patient_id,
        MedicationStatement.status == "active"
    ).count()

    recent_docs = docs[:5]
    recent_abnormals = sorted(
        abnormal_obs,
        key=lambda x: x.created_at or x.id,
        reverse=True
    )[:6]

    # Simplified timeline for dashboard
    timeline_preview = []
    for d in docs[:6]:
        timeline_preview.append({
            "id": d.id,
            "title": d.title,
            "doc_type": d.doc_type,
            "date": d.report_date or "Recent",
            "abnormal_count": sum(1 for o in d.observations if o.interpretation in ["High", "Low", "Critical"]),
            "facility": d.facility_name or "Lab"
        })

    return DashboardStatsOut(
        total_reports=total_reports,
        total_tests=total_tests,
        abnormal_tests_count=abnormal_count,
        active_medications_count=meds_count,
        recent_documents=recent_docs,
        recent_abnormal_observations=recent_abnormals,
        health_timeline=timeline_preview,
        is_demo_mode=ai_service.is_demo_mode(),
        active_ai_provider=ai_service.get_active_model_name()
    )

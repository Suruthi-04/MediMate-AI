import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.fhir import Patient, DocumentReference, Observation, Condition, MedicationStatement
from app.schemas.report_schemas import (
    ObservationOut, ObservationUpdate, ObservationCreate,
    PatientOut
)
from app.services.ai_service import ai_service

router = APIRouter(tags=["FHIR Resources"])

# Observation Endpoints
@router.put("/observations/{obs_id}", response_model=ObservationOut)
def update_observation(
    obs_id: int,
    payload: ObservationUpdate,
    db: Session = Depends(get_db)
):
    """
    User manual correction of an extracted observation.
    Marks user_corrected=True and updates fields.
    """
    obs = db.query(Observation).filter(Observation.id == obs_id).first()
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(obs, field, val)

    obs.user_corrected = True
    obs.is_uncertain = False # Clearing uncertainty once user approves/corrects

    # Re-evaluate interpretation if numeric value and ranges are present
    if obs.value_string:
        try:
            num = float(obs.value_string)
            obs.value_quantity = num
            if obs.reference_range_low is not None and num < obs.reference_range_low:
                obs.interpretation = "Low"
            elif obs.reference_range_high is not None and num > obs.reference_range_high:
                obs.interpretation = "High"
            else:
                obs.interpretation = "Normal"
        except ValueError:
            pass

    db.commit()
    db.refresh(obs)
    return obs


@router.delete("/observations/{obs_id}")
def delete_observation(obs_id: int, db: Session = Depends(get_db)):
    """Delete a single observation."""
    obs = db.query(Observation).filter(Observation.id == obs_id).first()
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    db.delete(obs)
    db.commit()
    return {"status": "success", "message": f"Observation {obs_id} deleted"}


@router.post("/observations", response_model=ObservationOut)
def create_manual_observation(
    payload: ObservationCreate,
    db: Session = Depends(get_db)
):
    """Manually add an observation record to a document."""
    if not payload.document_id:
        raise HTTPException(status_code=400, detail="document_id is required")

    obs = Observation(
        document_id=payload.document_id,
        patient_id=payload.patient_id or 1,
        display_name=payload.display_name,
        category=payload.category or "laboratory",
        value_string=payload.value_string,
        value_quantity=payload.value_quantity,
        unit=payload.unit,
        reference_range_low=payload.reference_range_low,
        reference_range_high=payload.reference_range_high,
        reference_range_text=payload.reference_range_text,
        interpretation=payload.interpretation,
        user_corrected=True,
        is_uncertain=False,
        notes=payload.notes or "Manually added by user"
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return obs


# Patient Endpoints
@router.get("/patients/active", response_model=PatientOut)
def get_active_patient(db: Session = Depends(get_db)):
    """Retrieve the primary demonstration patient."""
    patient = db.query(Patient).filter(Patient.identifier == "PAT-HACX-2026").first()
    if not patient:
        patient = db.query(Patient).first()
    if not patient:
        patient = Patient(identifier="PAT-HACX-2026", name="Arun Kumar", birth_date="1981-06-14", gender="male", blood_group="O+")
        db.add(patient)
        db.commit()
        db.refresh(patient)
    return patient

from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Observation Schemas
class ObservationBase(BaseModel):
    display_name: str
    category: Optional[str] = "laboratory"
    value_string: str
    value_quantity: Optional[float] = None
    unit: Optional[str] = None
    reference_range_low: Optional[float] = None
    reference_range_high: Optional[float] = None
    reference_range_text: Optional[str] = None
    interpretation: str = "Normal" # Normal, High, Low, Critical, Inconclusive
    is_uncertain: bool = False
    confidence_score: float = 0.95
    notes: Optional[str] = None
    effective_datetime: Optional[str] = None

class ObservationCreate(ObservationBase):
    document_id: Optional[int] = None
    patient_id: Optional[int] = 1

class ObservationUpdate(BaseModel):
    display_name: Optional[str] = None
    value_string: Optional[str] = None
    value_quantity: Optional[float] = None
    unit: Optional[str] = None
    reference_range_low: Optional[float] = None
    reference_range_high: Optional[float] = None
    reference_range_text: Optional[str] = None
    interpretation: Optional[str] = None
    is_uncertain: Optional[bool] = None
    notes: Optional[str] = None

class ObservationOut(ObservationBase):
    id: int
    document_id: int
    patient_id: int
    user_corrected: bool = False
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)



# Condition Schemas
class ConditionBase(BaseModel):
    display_name: str
    clinical_status: str = "active"
    verification_status: str = "confirmed"
    category: Optional[str] = "problem-list-item"
    severity: Optional[str] = "mild"
    recorded_date: Optional[str] = None
    notes: Optional[str] = None

class ConditionCreate(ConditionBase):
    document_id: Optional[int] = None
    patient_id: Optional[int] = 1

class ConditionOut(ConditionBase):
    id: int
    document_id: int
    patient_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Medication Schemas
class MedicationStatementBase(BaseModel):
    medication_name: str
    dosage_instruction: Optional[str] = None
    route: Optional[str] = "oral"
    frequency: Optional[str] = "as directed"
    status: str = "active"
    effective_period: Optional[str] = None
    notes: Optional[str] = None

class MedicationStatementCreate(MedicationStatementBase):
    document_id: Optional[int] = None
    patient_id: Optional[int] = 1

class MedicationStatementOut(MedicationStatementBase):
    id: int
    document_id: int
    patient_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# AI Summary Structured Schema
class KeyFinding(BaseModel):
    title: str
    description: str
    status: str # Normal, Attention, Info

class AISummaryContent(BaseModel):
    document_overview: str
    important_tests: List[Dict[str, Any]] = []
    out_of_range_values: List[Dict[str, Any]] = []
    simple_explanations: List[str] = []
    questions_for_doctor: List[str] = []
    limitations_disclaimer: str


# Document Reference Schemas
class DocumentReferenceBase(BaseModel):
    title: str
    doc_type: str = "Lab Report"
    category: Optional[str] = "diagnostic-report"
    report_date: Optional[str] = None
    facility_name: Optional[str] = None
    doctor_name: Optional[str] = None
    status: str = "current"

class DocumentReferenceCreate(DocumentReferenceBase):
    patient_id: int = 1
    file_name: str
    file_path: str
    file_size: int = 0
    mime_type: str = "application/pdf"
    raw_extracted_text: Optional[str] = None

class DocumentReferenceOut(DocumentReferenceBase):
    id: int
    patient_id: int
    file_name: str
    file_size: int
    mime_type: str
    raw_extracted_text: Optional[str] = None
    summary_en: Optional[str] = None
    summary_ta: Optional[str] = None
    key_findings_json: Optional[str] = None
    doctor_questions_json: Optional[str] = None
    ai_model: Optional[str] = None
    is_demo_mode: bool = True
    created_at: Optional[datetime] = None
    observations: List[ObservationOut] = []
    conditions: List[ConditionOut] = []
    medications: List[MedicationStatementOut] = []

    model_config = ConfigDict(from_attributes=True)


# Patient Schemas
class PatientOut(BaseModel):
    id: int
    identifier: str
    name: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    contact: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)



# Dashboard Statistics Schema
class DashboardStatsOut(BaseModel):
    total_reports: int
    total_tests: int
    abnormal_tests_count: int
    active_medications_count: int
    recent_documents: List[DocumentReferenceOut] = []
    recent_abnormal_observations: List[ObservationOut] = []
    health_timeline: List[Dict[str, Any]] = []
    is_demo_mode: bool = True
    active_ai_provider: str = "MediMate Clinical Engine (Demo Mode)"

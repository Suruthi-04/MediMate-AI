from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship

from app.database import Base

class Patient(Base):
    """
    FHIR-inspired Patient resource (Demonstration prototype).
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    identifier = Column(String(50), unique=True, index=True, default="PAT-DEMO-001")
    name = Column(String(120), nullable=False)
    birth_date = Column(String(20), nullable=True) # YYYY-MM-DD
    gender = Column(String(20), nullable=True)     # male, female, other
    blood_group = Column(String(10), nullable=True) # e.g. O+
    contact = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    documents = relationship("DocumentReference", back_populates="patient", cascade="all, delete-orphan")
    observations = relationship("Observation", back_populates="patient", cascade="all, delete-orphan")
    conditions = relationship("Condition", back_populates="patient", cascade="all, delete-orphan")
    medications = relationship("MedicationStatement", back_populates="patient", cascade="all, delete-orphan")


class DocumentReference(Base):
    """
    FHIR-inspired DocumentReference resource representing uploaded medical records.
    """
    __tablename__ = "document_references"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    doc_type = Column(String(100), default="Lab Report") # Lab Report, Prescription, Discharge Summary, Radiology
    category = Column(String(100), default="diagnostic-report")
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    mime_type = Column(String(100), default="application/pdf")
    report_date = Column(String(30), nullable=True)
    facility_name = Column(String(200), nullable=True)
    doctor_name = Column(String(200), nullable=True)
    status = Column(String(50), default="current")
    
    # Text preservation & AI summary
    raw_extracted_text = Column(Text, nullable=True)
    summary_en = Column(Text, nullable=True)
    summary_ta = Column(Text, nullable=True)
    key_findings_json = Column(Text, nullable=True)
    doctor_questions_json = Column(Text, nullable=True)
    ai_model = Column(String(100), default="MediMate Clinical Engine")
    is_demo_mode = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="documents")
    observations = relationship("Observation", back_populates="document", cascade="all, delete-orphan")
    conditions = relationship("Condition", back_populates="document", cascade="all, delete-orphan")
    medications = relationship("MedicationStatement", back_populates="document", cascade="all, delete-orphan")


class Observation(Base):
    """
    FHIR-inspired Observation resource representing laboratory results & clinical metrics.
    """
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document_references.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(50), nullable=True) # e.g. LOINC code if known
    display_name = Column(String(150), nullable=False)
    category = Column(String(100), default="laboratory")
    value_quantity = Column(Float, nullable=True)
    value_string = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=True)
    reference_range_low = Column(Float, nullable=True)
    reference_range_high = Column(Float, nullable=True)
    reference_range_text = Column(String(150), nullable=True)
    interpretation = Column(String(50), default="Normal") # Normal, High, Low, Critical, Inconclusive
    is_uncertain = Column(Boolean, default=False)
    user_corrected = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.95)
    notes = Column(Text, nullable=True)
    effective_datetime = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("DocumentReference", back_populates="observations")
    patient = relationship("Patient", back_populates="observations")


class Condition(Base):
    """
    FHIR-inspired Condition resource representing diagnoses and clinical findings.
    """
    __tablename__ = "conditions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document_references.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(50), nullable=True)
    display_name = Column(String(200), nullable=False)
    clinical_status = Column(String(50), default="active") # active, resolved, provisional
    verification_status = Column(String(50), default="confirmed")
    category = Column(String(100), default="problem-list-item")
    severity = Column(String(50), default="mild")
    recorded_date = Column(String(30), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("DocumentReference", back_populates="conditions")
    patient = relationship("Patient", back_populates="conditions")


class MedicationStatement(Base):
    """
    FHIR-inspired MedicationStatement resource representing prescribed medicines.
    """
    __tablename__ = "medication_statements"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document_references.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    medication_name = Column(String(200), nullable=False)
    dosage_instruction = Column(String(250), nullable=True)
    route = Column(String(50), default="oral")
    frequency = Column(String(100), default="as directed")
    status = Column(String(50), default="active")
    effective_period = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("DocumentReference", back_populates="medications")
    patient = relationship("Patient", back_populates="medications")

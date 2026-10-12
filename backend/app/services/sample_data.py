import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from PIL import Image, ImageDraw, ImageFont

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.config import settings
from app.models.fhir import Patient, DocumentReference, Observation, Condition, MedicationStatement
from app.services.ai_service import ai_service

def generate_sample_files():
    """Generate realistic synthetic medical PDF and image files for user testing."""
    sample_dir = settings.SAMPLE_DIR
    sample_dir.mkdir(parents=True, exist_ok=True)

    # 1. Complete Blood Count (CBC) PDF
    cbc_pdf_path = sample_dir / "sample_cbc_report.pdf"
    if not cbc_pdf_path.exists():
        doc = SimpleDocTemplate(str(cbc_pdf_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#0d9488'),
            spaceAfter=6
        )
        sub_style = ParagraphStyle(
            'SubStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#475569'),
            spaceAfter=12
        )

        elements.append(Paragraph("<b>APOLLO DIAGNOSTICS & HEALTHCARE</b>", title_style))
        elements.append(Paragraph("SYNTHETIC DEMO CLINICAL REPORT | HacXLerate 2026 Round 1", sub_style))
        elements.append(Paragraph("<b>Patient Name:</b> Arun Kumar (45Y / Male) | <b>Patient ID:</b> PAT-HACX-2026<br/><b>Ref. By:</b> Dr. S. Ramanathan, MD | <b>Date:</b> 10-Oct-2026", styles['Normal']))
        elements.append(Spacer(1, 14))

        data = [
            ["Test Parameter", "Observed Value", "Units", "Reference Range", "Flag"],
            ["Hemoglobin (Hb)", "13.8", "g/dL", "13.0 - 17.0", "NORMAL"],
            ["Total Leukocyte Count (WBC)", "7.2", "× 10^3/µL", "4.0 - 11.0", "NORMAL"],
            ["RBC Count", "4.7", "× 10^6/µL", "4.5 - 5.9", "NORMAL"],
            ["Packed Cell Volume (PCV)", "41", "%", "40.0 - 50.0", "NORMAL"],
            ["Mean Corpuscular Volume (MCV)", "87", "fL", "80.0 - 100.0", "NORMAL"],
            ["Platelet Count", "250", "× 10^3/µL", "150 - 450", "NORMAL"],
        ]

        t = Table(data, colWidths=[180, 80, 80, 110, 70])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f766e')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (4,1), (-1,-1), colors.HexColor('#0f766e')),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<i>Comments: Complete blood count parameters are within physiological reference intervals. Routine health screening profile.</i>", styles['Italic']))
        doc.build(elements)

    # 2. Diabetic & Lipid Panel PDF
    lipid_pdf_path = sample_dir / "sample_diabetic_lipid_report.pdf"
    if not lipid_pdf_path.exists():
        doc = SimpleDocTemplate(str(lipid_pdf_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle('Title2', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0d9488'), spaceAfter=6)
        elements.append(Paragraph("<b>DR. LAL PATHLABS CLINICAL BIOCHEMISTRY</b>", title_style))
        elements.append(Paragraph("COMPREHENSIVE DIABETIC & LIPID PROFILE | SYNTHETIC DEMO DATA", styles['Normal']))
        elements.append(Paragraph("<b>Patient Name:</b> Arun Kumar (45Y / Male) | <b>Date:</b> 12-Oct-2026<br/><b>Ref. Doctor:</b> Dr. K. Rajesh, Diabetologist", styles['Normal']))
        elements.append(Spacer(1, 14))

        lipid_data = [
            ["Investigation", "Result", "Units", "Biological Reference Range", "Status"],
            ["Fasting Blood Sugar (FBS)", "138", "mg/dL", "70 - 99", "HIGH"],
            ["HbA1c (Glycated Hemoglobin)", "7.4", "%", "4.0 - 5.6", "HIGH"],
            ["Total Cholesterol", "224", "mg/dL", "125 - 200", "HIGH"],
            ["HDL Cholesterol (Good)", "38", "mg/dL", "40 - 60", "LOW"],
            ["LDL Cholesterol (Bad)", "146", "mg/dL", "50 - 100", "HIGH"],
            ["Serum Triglycerides", "195", "mg/dL", "50 - 150", "HIGH"],
            ["Serum Creatinine", "0.92", "mg/dL", "0.7 - 1.3", "NORMAL"],
        ]

        t2 = Table(lipid_data, colWidths=[180, 80, 80, 110, 70])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ffffff')),
            ('TEXTCOLOR', (4,1), (4,6), colors.red),
        ]))
        elements.append(t2)
        elements.append(Spacer(1, 16))
        elements.append(Paragraph("<i>Notes: Known patient with Type 2 Diabetes Mellitus & Dyslipidemia. Follow-up consultation scheduled.</i>", styles['Italic']))
        doc.build(elements)

    # 3. Prescription JPG Image
    rx_img_path = sample_dir / "sample_prescription.jpg"
    if not rx_img_path.exists():
        img = Image.new("RGB", (900, 600), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw header banner
        draw.rectangle([0, 0, 900, 80], fill=(13, 148, 136))
        draw.text((30, 25), "METRO CARE CLINIC - PRESCRIPTION (DEMO)", fill=(255, 255, 255))
        
        # Clinical details
        draw.text((40, 105), "Patient: Arun Kumar | Age: 45 Y / M | Date: 12-Oct-2026", fill=(30, 41, 59))
        draw.text((40, 130), "Diagnosis: Type 2 Diabetes Mellitus, Dyslipidemia", fill=(30, 41, 59))
        draw.line([(40, 165), (860, 165)], fill=(203, 213, 225), width=2)
        
        draw.text((40, 185), "Rx (Medications Prescribed):", fill=(15, 23, 42))
        draw.text((60, 220), "1. Tab. Metformin 500 mg - 1 tablet twice daily after meals (BD)", fill=(30, 41, 59))
        draw.text((60, 260), "2. Tab. Atorvastatin 10 mg - 1 tablet once daily at bedtime (HS)", fill=(30, 41, 59))
        draw.text((60, 300), "3. Tab. Telmisartan 40 mg - 1 tablet once daily in the morning (OD)", fill=(30, 41, 59))
        draw.text((60, 340), "4. Cap. Vitamin D3 60K - 1 capsule once weekly for 8 weeks", fill=(30, 41, 59))
        
        draw.line([(40, 400), (860, 400)], fill=(203, 213, 225), width=2)
        draw.text((40, 420), "Instructions & Lifestyle:", fill=(15, 23, 42))
        draw.text((60, 450), "- Low glycemic index diabetic diet and 30 minutes daily brisk walk.", fill=(71, 85, 105))
        draw.text((60, 480), "- Re-check HbA1c and Lipid Profile in 3 months.", fill=(71, 85, 105))
        draw.text((600, 530), "Dr. S. Ramanathan, MD", fill=(15, 23, 42))
        
        img.save(str(rx_img_path), "JPEG", quality=90)


def seed_sample_database(db: Session):
    """Seed synthetic patient, documents, observations, conditions, and medications."""
    # Ensure physical sample files exist
    generate_sample_files()

    # Check if patient already exists
    existing_patient = db.query(Patient).filter(Patient.identifier == "PAT-HACX-2026").first()
    if existing_patient:
        return existing_patient

    patient = Patient(
        identifier="PAT-HACX-2026",
        name="Arun Kumar",
        birth_date="1981-06-14",
        gender="male",
        blood_group="O+",
        contact="+91 98765 43210"
    )
    db.add(patient)
    db.flush()

    # 1. CBC Document
    cbc_path = settings.SAMPLE_DIR / "sample_cbc_report.pdf"
    doc1 = DocumentReference(
        patient_id=patient.id,
        title="Complete Blood Count (CBC) Routine Health Screen",
        doc_type="Complete Blood Count (CBC)",
        category="diagnostic-report",
        file_name="sample_cbc_report.pdf",
        file_path=str(cbc_path),
        file_size=24500,
        mime_type="application/pdf",
        report_date="2026-10-10",
        facility_name="Apollo Diagnostics",
        doctor_name="Dr. S. Ramanathan, MD",
        status="current",
        raw_extracted_text=(
            "APOLLO DIAGNOSTICS & HEALTHCARE\n"
            "Patient: Arun Kumar (45Y / Male) | Date: 10-Oct-2026\n"
            "Hemoglobin (Hb): 13.8 g/dL (Ref: 13.0 - 17.0)\n"
            "Total Leukocyte Count (WBC): 7.2 × 10^3/µL (Ref: 4.0 - 11.0)\n"
            "RBC Count: 4.7 × 10^6/µL (Ref: 4.5 - 5.9)\n"
            "Packed Cell Volume (PCV): 41 % (Ref: 40.0 - 50.0)\n"
            "Mean Corpuscular Volume (MCV): 87 fL (Ref: 80.0 - 100.0)\n"
            "Platelet Count: 250 × 10^3/µL (Ref: 150 - 450)\n"
            "Diagnosis: Routine Health Screening / Normal CBC Profile"
        )
    )
    db.add(doc1)
    db.flush()

    # CBC Observations
    obs_cbc_data = [
        ("Hemoglobin (Hb)", "hematology", 13.8, "g/dL", 13.0, 17.0, "Normal", 0.98),
        ("Total Leukocyte Count (WBC)", "hematology", 7.2, "× 10^3/µL", 4.0, 11.0, "Normal", 0.99),
        ("RBC Count", "hematology", 4.7, "× 10^6/µL", 4.5, 5.9, "Normal", 0.97),
        ("Packed Cell Volume (PCV)", "hematology", 41.0, "%", 40.0, 50.0, "Normal", 0.96),
        ("Mean Corpuscular Volume (MCV)", "hematology", 87.0, "fL", 80.0, 100.0, "Normal", 0.95),
        ("Platelet Count", "hematology", 250.0, "× 10^3/µL", 150.0, 450.0, "Normal", 0.99),
    ]
    obs1_list = []
    for name, cat, val, unit, low, high, inter, conf in obs_cbc_data:
        obs = Observation(
            document_id=doc1.id,
            patient_id=patient.id,
            display_name=name,
            category=cat,
            value_string=str(val),
            value_quantity=val,
            unit=unit,
            reference_range_low=low,
            reference_range_high=high,
            reference_range_text=f"{low} - {high} {unit}",
            interpretation=inter,
            confidence_score=conf,
            is_uncertain=False,
            notes="Extracted from standard diagnostic lab run."
        )
        db.add(obs)
        obs1_list.append({
            "display_name": name,
            "value_string": str(val),
            "unit": unit,
            "reference_range_text": f"{low} - {high} {unit}",
            "interpretation": inter
        })

    # CBC Condition & Medication
    cond1 = Condition(
        document_id=doc1.id,
        patient_id=patient.id,
        display_name="Normal Hematological Profile (Routine Screening)",
        clinical_status="active",
        verification_status="confirmed",
        recorded_date="2026-10-10",
        notes="All Complete Blood Count parameters within physiological limits."
    )
    db.add(cond1)

    med1 = MedicationStatement(
        document_id=doc1.id,
        patient_id=patient.id,
        medication_name="Multivitamin Supplement (Routine)",
        dosage_instruction="1 tablet daily with breakfast",
        status="active"
    )
    db.add(med1)

    # Generate AI summary for doc1
    summary1 = ai_service.generate_health_summary(
        doc1.title, doc1.doc_type, doc1.raw_extracted_text, obs1_list,
        [{"medication_name": med1.medication_name, "dosage_instruction": med1.dosage_instruction}],
        [{"display_name": cond1.display_name}]
    )
    doc1.summary_en = summary1["summary_en"]
    doc1.summary_ta = summary1["summary_ta"]
    doc1.key_findings_json = json.dumps(summary1["key_findings"])
    doc1.doctor_questions_json = json.dumps(summary1["doctor_questions"])
    doc1.ai_model = summary1["ai_model"]
    doc1.is_demo_mode = summary1["is_demo_mode"]

    # 2. Diabetic & Lipid Document
    lipid_path = settings.SAMPLE_DIR / "sample_diabetic_lipid_report.pdf"
    doc2 = DocumentReference(
        patient_id=patient.id,
        title="Comprehensive Diabetic & Lipid Evaluation",
        doc_type="Lipid Profile Report",
        category="diagnostic-report",
        file_name="sample_diabetic_lipid_report.pdf",
        file_path=str(lipid_path),
        file_size=28900,
        mime_type="application/pdf",
        report_date="2026-10-12",
        facility_name="Dr Lal PathLabs",
        doctor_name="Dr. K. Rajesh, Diabetologist",
        status="current",
        raw_extracted_text=(
            "DR. LAL PATHLABS CLINICAL BIOCHEMISTRY\n"
            "Patient: Arun Kumar (45Y / Male) | Date: 12-Oct-2026\n"
            "Fasting Blood Sugar (FBS): 138 mg/dL (Ref: 70 - 99)\n"
            "HbA1c (Glycated Hemoglobin): 7.4 % (Ref: 4.0 - 5.6)\n"
            "Total Cholesterol: 224 mg/dL (Ref: 125 - 200)\n"
            "HDL Cholesterol (Good): 38 mg/dL (Ref: 40 - 60)\n"
            "LDL Cholesterol (Bad): 146 mg/dL (Ref: 50 - 100)\n"
            "Serum Triglycerides: 195 mg/dL (Ref: 50 - 150)\n"
            "Serum Creatinine: 0.92 mg/dL (Ref: 0.7 - 1.3)\n"
            "Prescriptions: Tab. Metformin 500 mg, Tab. Atorvastatin 10 mg"
        )
    )
    db.add(doc2)
    db.flush()

    obs_lipid_data = [
        ("Fasting Blood Sugar (FBS)", "diabetes", 138.0, "mg/dL", 70.0, 99.0, "High", 0.98),
        ("HbA1c (Glycated Hemoglobin)", "diabetes", 7.4, "%", 4.0, 5.6, "High", 0.99),
        ("Total Cholesterol", "lipid", 224.0, "mg/dL", 125.0, 200.0, "High", 0.97),
        ("HDL Cholesterol (Good)", "lipid", 38.0, "mg/dL", 40.0, 60.0, "Low", 0.96),
        ("LDL Cholesterol (Bad)", "lipid", 146.0, "mg/dL", 50.0, 100.0, "High", 0.98),
        ("Serum Triglycerides", "lipid", 195.0, "mg/dL", 50.0, 150.0, "High", 0.95),
        ("Serum Creatinine", "renal", 0.92, "mg/dL", 0.7, 1.3, "Normal", 0.99),
    ]
    obs2_list = []
    for name, cat, val, unit, low, high, inter, conf in obs_lipid_data:
        obs = Observation(
            document_id=doc2.id,
            patient_id=patient.id,
            display_name=name,
            category=cat,
            value_string=str(val),
            value_quantity=val,
            unit=unit,
            reference_range_low=low,
            reference_range_high=high,
            reference_range_text=f"{low} - {high} {unit}",
            interpretation=inter,
            confidence_score=conf,
            is_uncertain=False,
            notes="Extracted from standard diagnostic lab run."
        )
        db.add(obs)
        obs2_list.append({
            "display_name": name,
            "value_string": str(val),
            "unit": unit,
            "reference_range_text": f"{low} - {high} {unit}",
            "interpretation": inter
        })

    # Conditions for doc2
    cond2a = Condition(
        document_id=doc2.id,
        patient_id=patient.id,
        display_name="Type 2 Diabetes Mellitus",
        clinical_status="active",
        verification_status="confirmed",
        recorded_date="2026-10-12",
        notes="HbA1c 7.4% and Fasting Blood Sugar 138 mg/dL."
    )
    cond2b = Condition(
        document_id=doc2.id,
        patient_id=patient.id,
        display_name="Dyslipidemia / Hypercholesterolemia",
        clinical_status="active",
        verification_status="confirmed",
        recorded_date="2026-10-12",
        notes="Total Cholesterol 224 mg/dL, LDL 146 mg/dL, TG 195 mg/dL."
    )
    db.add(cond2a)
    db.add(cond2b)

    med2a = MedicationStatement(
        document_id=doc2.id,
        patient_id=patient.id,
        medication_name="Tab. Metformin 500 mg",
        dosage_instruction="500 mg, Twice daily after meals",
        status="active"
    )
    med2b = MedicationStatement(
        document_id=doc2.id,
        patient_id=patient.id,
        medication_name="Tab. Atorvastatin 10 mg",
        dosage_instruction="10 mg, Once daily at bedtime",
        status="active"
    )
    db.add(med2a)
    db.add(med2b)

    # Generate AI summary for doc2
    summary2 = ai_service.generate_health_summary(
        doc2.title, doc2.doc_type, doc2.raw_extracted_text, obs2_list,
        [
            {"medication_name": med2a.medication_name, "dosage_instruction": med2a.dosage_instruction},
            {"medication_name": med2b.medication_name, "dosage_instruction": med2b.dosage_instruction}
        ],
        [
            {"display_name": cond2a.display_name},
            {"display_name": cond2b.display_name}
        ]
    )
    doc2.summary_en = summary2["summary_en"]
    doc2.summary_ta = summary2["summary_ta"]
    doc2.key_findings_json = json.dumps(summary2["key_findings"])
    doc2.doctor_questions_json = json.dumps(summary2["doctor_questions"])
    doc2.ai_model = summary2["ai_model"]
    doc2.is_demo_mode = summary2["is_demo_mode"]

    db.commit()
    return patient

import io
import pytest
from fastapi.testclient import TestClient
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from app.main import app
from app.config import settings
from app.database import Base, engine, SessionLocal
from app.models.fhir import DocumentReference, Observation

client = TestClient(app)

def create_synthetic_pdf_in_memory() -> bytes:
    """Generates an in-memory PDF with unique synthetic test values to verify genuine extraction."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Synthetic demo headers - No real patient data
    elements.append(Paragraph("<b>METROPOLIS DIAGNOSTICS & RESEARCH (SYNTHETIC DEMO)</b>", styles['Heading1']))
    elements.append(Paragraph("Patient: Arun Kumar (Demo) | Date: 12-Oct-2026 | Ref: Dr. S. Ramanathan", styles['Normal']))
    elements.append(Spacer(1, 10))

    # Unique test values: FBS 165, Total Cholesterol 248, TSH 6.8, Creatinine 1.6
    table_data = [
        ["Investigation", "Observed Result", "Units", "Reference Range"],
        ["Fasting Blood Sugar (FBS)", "165", "mg/dL", "70 - 99"],
        ["Total Cholesterol", "248", "mg/dL", "125 - 200"],
        ["Thyroid Stimulating Hormone (TSH)", "6.8", "uIU/mL", "0.4 - 4.5"],
        ["Serum Creatinine", "1.6", "mg/dL", "0.7 - 1.3"],
    ]
    t = Table(table_data, colWidths=[200, 70, 70, 120])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.teal),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Rx: Tab. Thyroxine 50 mcg once daily in morning. Diagnosis: Hypothyroidism.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def test_actual_pdf_upload_and_genuine_extraction():
    """Verify that uploaded PDF values are genuinely parsed from document text and persisted, not mocked."""
    pdf_bytes = create_synthetic_pdf_in_memory()
    
    files = {
        "file": ("custom_synthetic_eval.pdf", pdf_bytes, "application/pdf")
    }
    data = {
        "doc_title": "Genuine Uploaded Extraction Test"
    }

    # 1. Test POST /api/documents/upload
    response = client.post("/api/documents/upload", files=files, data=data)
    assert response.status_code == 200, f"Upload failed: {response.text}"
    
    doc_data = response.json()
    new_doc_id = doc_data["id"]
    assert new_doc_id > 0
    assert doc_data["title"] == "Genuine Uploaded Extraction Test"
    
    # 2. Verify extracted observations match the exact values in the synthetic PDF
    observations = doc_data.get("observations", [])
    assert len(observations) >= 4, f"Expected at least 4 observations, got {len(observations)}"

    obs_map = {o["display_name"]: o for o in observations}
    
    # Fasting Blood Sugar: 165 mg/dL -> High
    fbs = next((o for name, o in obs_map.items() if "Fasting Blood Sugar" in name), None)
    assert fbs is not None, "Fasting Blood Sugar was not extracted"
    assert fbs["value_quantity"] == 165.0
    assert fbs["interpretation"] == "High"
    assert fbs["unit"] == "mg/dL"

    # Total Cholesterol: 248 mg/dL -> High
    tc = next((o for name, o in obs_map.items() if "Total Cholesterol" in name), None)
    assert tc is not None, "Total Cholesterol was not extracted"
    assert tc["value_quantity"] == 248.0
    assert tc["interpretation"] == "High"

    # TSH: 6.8 uIU/mL -> High
    tsh = next((o for name, o in obs_map.items() if "Thyroid" in name or "TSH" in name), None)
    assert tsh is not None, "TSH was not extracted"
    assert tsh["value_quantity"] == 6.8
    assert tsh["interpretation"] == "High"

    # Serum Creatinine: 1.6 mg/dL -> High
    creat = next((o for name, o in obs_map.items() if "Creatinine" in name), None)
    assert creat is not None, "Serum Creatinine was not extracted"
    assert creat["value_quantity"] == 1.6
    assert creat["interpretation"] == "High"

    # 3. Verify extracted prescription medication
    meds = doc_data.get("medications", [])
    assert any("Thyroxine" in m["medication_name"] for m in meds), "Tab. Thyroxine was not extracted from prescription text"

    # 4. Verify AI Health Summary contains genuine extracted findings in English & Tamil
    summary_en = doc_data.get("summary_en", "")
    summary_ta = doc_data.get("summary_ta", "")
    assert "165" in summary_en or "Fasting Blood Sugar" in summary_en
    assert "248" in summary_en or "Cholesterol" in summary_en
    assert len(summary_ta) > 50, "Tamil translation was not generated"

    # 5. Verify Database Persistence: query GET /api/documents/{new_doc_id}
    fetch_resp = client.get(f"/api/documents/{new_doc_id}")
    assert fetch_resp.status_code == 200
    persisted_doc = fetch_resp.json()
    assert persisted_doc["id"] == new_doc_id
    assert len(persisted_doc["observations"]) == len(observations)

    # 6. Verify Health Timeline persistence
    timeline_resp = client.get("/api/timeline")
    assert timeline_resp.status_code == 200
    timeline_data = timeline_resp.json()
    doc_ids_in_timeline = [item["id"] for item in timeline_data["timeline"]]
    assert new_doc_id in doc_ids_in_timeline, "Uploaded document is present in timeline"


def test_upload_invalid_file_extension_rejected():
    """Verify error handling: uploading disallowed file extensions returns 400 Bad Request."""
    invalid_file = {
        "file": ("malicious_script.exe", b"fake executable binary content", "application/x-msdownload")
    }
    response = client.post("/api/documents/upload", files=invalid_file)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_upload_file_size_exceeded_rejected(monkeypatch):
    """Verify error handling: uploading a file exceeding max size returns 413 Payload Too Large."""
    # Temporarily lower MAX_FILE_SIZE_MB to 1KB to test size restriction safely without creating huge buffers
    monkeypatch.setattr(settings, "MAX_FILE_SIZE_MB", 0.001) # ~1024 bytes
    
    oversized_bytes = b"X" * 2048 # 2KB payload
    files = {
        "file": ("oversized_report.pdf", oversized_bytes, "application/pdf")
    }
    response = client.post("/api/documents/upload", files=files)
    assert response.status_code == 413
    assert "exceeds maximum allowed size" in response.json()["detail"]


def test_nonexistent_document_returns_404():
    """Verify error handling: requesting a non-existent document ID returns 404 Not Found."""
    response = client.get("/api/documents/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_upload_synthetic_cbc_and_verify_all_parameters():
    """Verify end-to-end upload of a synthetic CBC report with all 6 clinical parameters."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>APOLLO DIAGNOSTICS & HEALTHCARE (SYNTHETIC EVAL)</b>", styles['Heading1']))
    elements.append(Paragraph("Patient: Arun Kumar (Demo) | Date: 12-Oct-2026", styles['Normal']))
    elements.append(Spacer(1, 10))

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
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()

    files = {
        "file": ("eval_synthetic_cbc.pdf", pdf_bytes, "application/pdf")
    }
    data_form = {
        "doc_title": "Synthetic CBC Analysis Verification"
    }

    response = client.post("/api/documents/upload", files=files, data=data_form)
    assert response.status_code == 200
    doc_json = response.json()
    observations = doc_json.get("observations", [])
    assert len(observations) == 6, f"Expected 6 observations, got {len(observations)}"

    obs_map = {o["display_name"]: o for o in observations}

    # 1. Hemoglobin 13.8 g/dL
    hb = next(o for name, o in obs_map.items() if "Hemoglobin" in name)
    assert hb["value_quantity"] == 13.8
    assert hb["unit"] == "g/dL"
    assert hb["interpretation"] == "Normal"

    # 2. RBC 4.7 x 10^6/µL
    rbc = next(o for name, o in obs_map.items() if "RBC" in name)
    assert rbc["value_quantity"] == 4.7
    assert "10^6" in rbc["unit"]
    assert rbc["interpretation"] == "Normal"

    # 3. WBC 7.2 x 10^3/µL
    wbc = next(o for name, o in obs_map.items() if "WBC" in name)
    assert wbc["value_quantity"] == 7.2
    assert "10^3" in wbc["unit"]
    assert wbc["interpretation"] == "Normal"

    # 4. Platelets 250 x 10^3/µL
    plt = next(o for name, o in obs_map.items() if "Platelet" in name)
    assert plt["value_quantity"] == 250.0
    assert "10^3" in plt["unit"]
    assert plt["interpretation"] == "Normal"

    # 5. PCV 41 %
    pcv = next(o for name, o in obs_map.items() if "PCV" in name)
    assert pcv["value_quantity"] == 41.0
    assert pcv["unit"] == "%"
    assert pcv["interpretation"] == "Normal"

    # 6. MCV 87 fL
    mcv = next(o for name, o in obs_map.items() if "MCV" in name)
    assert mcv["value_quantity"] == 87.0
    assert mcv["unit"] == "fL"
    assert mcv["interpretation"] == "Normal"

    # Check persistence
    new_id = doc_json["id"]
    get_resp = client.get(f"/api/documents/{new_id}")
    assert get_resp.status_code == 200
    assert len(get_resp.json()["observations"]) == 6


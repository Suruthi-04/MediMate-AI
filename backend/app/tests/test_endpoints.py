import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.services.sample_data import seed_sample_database

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_sample_database(db)
    db.close()
    yield

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_settings_status_endpoint():
    response = client.get("/api/settings/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "active_ai_provider" in data
    assert "is_demo_mode" in data

def test_dashboard_stats_endpoint():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_reports"] >= 1
    assert data["total_tests"] >= 1
    assert "health_timeline" in data

def test_timeline_endpoint():
    response = client.get("/api/timeline")
    assert response.status_code == 200
    data = response.json()
    assert "timeline" in data
    assert len(data["timeline"]) >= 1

def test_documents_list_and_detail():
    response = client.get("/api/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 1

    first_doc_id = docs[0]["id"]
    detail_resp = client.get(f"/api/documents/{first_doc_id}")
    assert detail_resp.status_code == 200
    doc_data = detail_resp.json()
    assert "observations" in doc_data
    assert "summary_en" in doc_data
    assert "summary_ta" in doc_data

def test_observation_manual_correction():
    # Fetch first observation
    docs_resp = client.get("/api/documents")
    docs = docs_resp.json()
    assert len(docs) > 0
    obs = docs[0]["observations"][0]
    obs_id = obs["id"]

    # Update value
    update_payload = {
        "value_string": "14.5",
        "reference_range_low": 13.0,
        "reference_range_high": 17.0,
        "notes": "Verified by clinical nurse"
    }
    patch_resp = client.put(f"/api/observations/{obs_id}", json=update_payload)
    assert patch_resp.status_code == 200
    updated_obs = patch_resp.json()
    assert updated_obs["value_string"] == "14.5"
    assert updated_obs["user_corrected"] is True
    assert updated_obs["interpretation"] == "Normal"

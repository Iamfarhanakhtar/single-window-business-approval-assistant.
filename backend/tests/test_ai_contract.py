"""AI & ML Contract Tests"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_analyze_business_contract():
    payload = {
        "sector": "Food Processing",
        "location": "Uttar Pradesh",
        "investment": 50000000,
        "employees": 80,
        "business_details": {}
    }
    response = client.post("/api/v1/ai/analyze-business", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "applicable_approvals" in data
    assert len(data["applicable_approvals"]) > 0
    assert "required_documents" in data
    assert "risk_score" in data
    assert 0.0 <= data["risk_score"] <= 1.0
    assert "delay_probability" in data
    assert "predicted_processing_days" in data
    assert "explanation" in data

def test_predict_delay_contract():
    payload = {
        "sector": "Food Processing",
        "state": "Uttar Pradesh",
        "investment": 50000000,
        "approval_codes": ["FIRE_NOC", "PCB_CTE"],
        "document_count": 4,
        "has_hazardous": False
    }
    response = client.post("/api/v1/ai/predict-delay", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "delay_probability" in data
    assert "expected_delay_days" in data
    assert "recommendation" in data

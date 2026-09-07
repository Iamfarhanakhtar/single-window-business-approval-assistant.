"""
Comprehensive Backend Integration Tests for Compliance Intelligence Subsystem (Step 6)
"""

import os
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ===========================================================================
# 1. Master Compliance Analysis Endpoint (/api/v1/compliance/analyze)
# ===========================================================================
def test_compliance_analyze_valid_request():
    payload = {
        "sector": "food_processing",
        "state": "Uttar Pradesh",
        "district": "Ghaziabad",
        "investment": 50000000.0,
        "employees": 80,
        "project_stage": "Pre-Operation",
        "connected_load_kw": 150.0,
        "has_boiler": True,
        "is_food_business": True,
        "water_requirement_kld": 25.0,
        "hazardous_materials": False,
        "built_up_area_sqm": 1200.0,
    }

    response = client.post("/api/v1/compliance/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verify root sections
    assert "business_profile" in data
    assert "summary" in data
    assert "approvals" in data
    assert "documents" in data
    assert "risk" in data
    assert "delay_prediction" in data
    assert "recommendations" in data
    assert "regulatory_explanations" in data
    assert "sources" in data
    assert "disclaimer" in data

    # Verify Summary counts
    summary = data["summary"]
    assert summary["total_approvals"] > 0
    assert summary["potentially_applicable"] > 0
    assert summary["documents_required"] > 0

    # Verify Rule Engine Approvals output
    approvals = data["approvals"]
    approval_names = [a["approval_name"] for a in approvals]
    assert any("Consent to Establish" in name or "CTE" in name for name in approval_names)
    assert any("Fire" in name for name in approval_names)

    # Verify ML Prediction output
    risk = data["risk"]
    assert 0 <= risk["risk_score"] <= 100
    assert risk["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert len(risk["factors"]) > 0

    delay = data["delay_prediction"]
    assert 0.0 <= delay["probability"] <= 1.0
    assert delay["predicted_days"] > 0
    assert delay["is_synthetic_model"] is True

    # Verify RAG Explanations and Sources
    rag_explanations = data["regulatory_explanations"]
    assert len(rag_explanations) > 0
    for exp in rag_explanations:
        assert "approval_name" in exp
        assert len(exp["answer"]) > 10
        assert "confidence" in exp

    sources = data["sources"]
    assert len(sources) > 0
    for src in sources:
        assert "source_name" in src
        assert "authority" in src


# ===========================================================================
# 2. Input Validation and Safe Error Handling
# ===========================================================================
def test_compliance_analyze_invalid_payload():
    # Negative investment
    bad_payload_1 = {
        "sector": "food_processing",
        "state": "Uttar Pradesh",
        "investment": -500000,
        "employees": 80,
    }
    resp1 = client.post("/api/v1/compliance/analyze", json=bad_payload_1)
    assert resp1.status_code == 422

    # Zero employees (requires >= 1)
    bad_payload_2 = {
        "sector": "food_processing",
        "state": "Uttar Pradesh",
        "investment": 50000000,
        "employees": 0,
    }
    resp2 = client.post("/api/v1/compliance/analyze", json=bad_payload_2)
    assert resp2.status_code == 422


# ===========================================================================
# 3. Deterministic Applicability & Verification Preservation
# ===========================================================================
def test_compliance_analyze_preserves_verification_status():
    payload = {
        "sector": "Manufacturing",
        "state": "Uttar Pradesh",
        "investment": 10000000,
        "employees": 15,
        "has_boiler": False,
    }
    response = client.post("/api/v1/compliance/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()

    statuses = {a["status"] for a in data["approvals"]}
    assert "POTENTIALLY_APPLICABLE" in statuses or "REQUIRES_VERIFICATION" in statuses


# ===========================================================================
# 4. Document AI Pre-Validation Endpoint (/api/v1/documents/validate)
# ===========================================================================
def test_document_validate_endpoint_valid_content():
    sample_text = (
        "GOVERNMENT OF UTTAR PRADESH\n"
        "UTTAR PRADESH FIRE SERVICE HEADQUARTERS, LUCKNOW\n"
        "PROVISIONAL FIRE SAFETY NO OBJECTION CERTIFICATE\n"
        "Certificate Number: UP-FIRE-NOC-2026-88421\n"
        "Issue Date: 2026-01-15\n"
        "Expiry Date: 2029-01-14\n"
        "Enterprise Name: Pragati Foods Private Limited\n"
        "Applicant PAN: AAACB1234F\n"
        "Aadhaar of Nominated Occupier: 4582 9182 3019\n"
    )

    payload = {
        "document_id": "DOC_TEST_001",
        "filename": "fire_noc.txt",
        "document_type": "Fire Safety NOC",
        "file_content_text": sample_text,
        "expected_entity_name": "Pragati Foods Pvt Ltd",
        "expected_document_type": "Fire Safety NOC",
    }

    response = client.post("/api/v1/documents/validate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["document_id"] == "DOC_TEST_001"
    assert data["status"] in ("VALID", "WARNING")
    assert data["entity_match"] in ("EXACT_MATCH", "LIKELY_MATCH")
    assert data["expiry_status"] == "VALID"
    assert data["requires_human_verification"] is True
    assert len(data["checks"]) > 0

    # Ensure PII is masked in redacted_preview
    assert "4582 9182 3019" not in data.get("redacted_preview", "")
    assert "XXXX-XXXX-3019" in data.get("redacted_preview", "")
    assert "AAACB1234F" not in data.get("redacted_preview", "")
    assert "XXXXX1234F" in data.get("redacted_preview", "")


# ===========================================================================
# 5. Document AI Handles Unreadable/Missing Files Gracefully
# ===========================================================================
def test_document_validate_missing_file():
    payload = {
        "document_id": "DOC_MISSING",
        "filename": "missing.txt",
        "document_type": "Fire Safety NOC",
        "file_path": "/non/existent/path/missing.txt",
    }

    response = client.post("/api/v1/documents/validate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "UNREADABLE"
    assert len(data["errors"]) > 0


# ===========================================================================
# 6. Compliance Intelligence Health Diagnostic (/api/v1/compliance/health)
# ===========================================================================
def test_compliance_health_diagnostic():
    response = client.get("/api/v1/compliance/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["rule_engine"]["loaded"] is True
    assert data["rule_engine"]["total_approvals"] > 0
    assert data["ml_predictor"]["loaded"] is True
    assert data["rag_pipeline"]["loaded"] is True
    assert data["document_ai"]["loaded"] is True

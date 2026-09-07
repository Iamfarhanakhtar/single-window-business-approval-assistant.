"""
Comprehensive Unit Tests for Document AI and Pre-Validation Subsystem

Covers text extraction across formats, PII redaction, corporate entity matching,
validity period verification, document category alignment, and completeness auditing.
"""

import os
from pathlib import Path
from datetime import datetime, date, timedelta, timezone
import pytest

from ai.document_ai.models import (
    DocumentInput,
    DocumentStatus,
    EntityMatchStatus,
    ExpiryStatus,
    DocumentTypeMatch,
)
from ai.document_ai.pii_redactor import redact_pii
from ai.document_ai.entity_matcher import match_entity_names, normalize_entity_name
from ai.document_ai.expiry_checker import check_expiry, parse_date
from ai.document_ai.extractor import DocumentExtractor
from ai.document_ai.validator import DocumentValidator, check_document_type_match
from ai.document_ai.pipeline import DocumentAIPipeline


@pytest.fixture
def demo_docs_dir():
    """Fixture returning path to sample test fixtures."""
    return Path(__file__).resolve().parent.parent / "demo_docs"


@pytest.fixture
def pipeline():
    """Fixture initializing DocumentAIPipeline."""
    return DocumentAIPipeline()


# =====================================================================
# TEST 1: PII Redaction Masks Aadhaar, PAN, and Bank Accounts
# =====================================================================
def test_pii_redaction():
    sample_text = (
        "Applicant Aadhaar: 1234 5678 9012, PAN: ABCDE1234F, "
        "Bank Acc No: 987654321012, password: MySecretPassword123"
    )
    redacted, pii_detected = redact_pii(sample_text)

    assert pii_detected is True
    assert "1234 5678 9012" not in redacted
    assert "XXXX-XXXX-9012" in redacted
    assert "ABCDE1234F" not in redacted
    assert "XXXXX1234F" in redacted
    assert "987654321012" not in redacted
    assert "[REDACTED_BANK_AC]" in redacted
    assert "MySecretPassword123" not in redacted


# =====================================================================
# TEST 2: Corporate Entity Name Normalization & Suffix Matching
# =====================================================================
def test_entity_name_matching():
    # Exact match
    status1, expl1 = match_entity_names("ABC Foods Pvt Ltd", "ABC Foods Pvt Ltd")
    assert status1 == EntityMatchStatus.EXACT_MATCH

    # Suffix variation ("Private Limited" vs "Pvt Ltd")
    status2, expl2 = match_entity_names("ABC Foods Pvt Ltd", "ABC Foods Private Limited")
    assert status2 in (EntityMatchStatus.EXACT_MATCH, EntityMatchStatus.LIKELY_MATCH)
    assert "suffix" in expl2.lower() or "matches" in expl2.lower()

    # Mismatched company names
    status3, expl3 = match_entity_names("ABC Foods Pvt Ltd", "Zenith Petrochemicals Ltd")
    assert status3 == EntityMatchStatus.NO_MATCH

    # Missing entity names
    status4, _ = match_entity_names("", "ABC Foods")
    assert status4 == EntityMatchStatus.UNKNOWN


# =====================================================================
# TEST 3: Document Expiry and Validity Period Calculation
# =====================================================================
def test_expiry_checker():
    today = date(2026, 9, 5)

    # 1. Valid future date (2 years ahead)
    future_date = (today + timedelta(days=700)).isoformat()
    st1, days1, _ = check_expiry(None, future_date, current_date=today)
    assert st1 == ExpiryStatus.VALID
    assert days1 == 700

    # 2. Expiring soon (within 20 days)
    soon_date = (today + timedelta(days=20)).isoformat()
    st2, days2, _ = check_expiry(None, soon_date, current_date=today, threshold_days=30)
    assert st2 == ExpiryStatus.EXPIRING_SOON
    assert days2 == 20

    # 3. Expired date (50 days ago)
    past_date = (today - timedelta(days=50)).isoformat()
    st3, days3, _ = check_expiry(None, past_date, current_date=today)
    assert st3 == ExpiryStatus.EXPIRED
    assert days3 == -50

    # 4. Permanent / Lifetime validity
    st4, _, _ = check_expiry(None, "Permanent", current_date=today)
    assert st4 == ExpiryStatus.VALID

    # 5. Missing expiry date
    st5, _, _ = check_expiry(None, None, current_date=today)
    assert st5 == ExpiryStatus.NO_EXPIRY_INFORMATION


# =====================================================================
# TEST 4: Document Type Alignment & Category Mismatch Detection
# =====================================================================
def test_document_type_matching():
    # Exact / Likely match
    m1, _ = check_document_type_match("Fire Safety NOC", "Fire Safety NOC", "Fire NOC Certificate text")
    assert m1 in (DocumentTypeMatch.MATCH, DocumentTypeMatch.LIKELY_MATCH)

    m2, _ = check_document_type_match("Factory License", "Factory License and Building Plan Approval", "Factories Act")
    assert m2 in (DocumentTypeMatch.MATCH, DocumentTypeMatch.LIKELY_MATCH)

    # Flagrant mismatch
    m3, expl3 = check_document_type_match("Factory License", "Electricity Bill", "Consumer electricity tariff details")
    assert m3 == DocumentTypeMatch.MISMATCH
    assert "mismatch" in expl3.lower()


# =====================================================================
# TEST 5: Text Extraction from Local .txt and .json Files
# =====================================================================
def test_local_text_extraction(demo_docs_dir):
    extractor = DocumentExtractor()

    # .txt extraction
    txt_path = str(demo_docs_dir / "valid_fire_noc.txt")
    ext_txt = extractor.extract("DOC_001", txt_path, "Fire Safety NOC")
    assert ext_txt.is_readable is True
    assert "ABC Foods" in ext_txt.extracted_text
    assert ext_txt.document_number is not None
    assert ext_txt.issue_date is not None
    assert ext_txt.expiry_date is not None
    assert ext_txt.pii_detected is True  # Redacted Aadhaar/PAN

    # .json extraction
    json_path = str(demo_docs_dir / "expiring_fssai.json")
    ext_json = extractor.extract("DOC_002", json_path, "FSSAI Food License")
    assert ext_json.is_readable is True
    assert "FSSAI" in ext_json.extracted_text
    assert ext_json.expiry_date is not None


# =====================================================================
# TEST 6: Unsupported / Missing File Handling (Safe Failures)
# =====================================================================
def test_unsupported_file_handling():
    extractor = DocumentExtractor()

    # Missing file
    ext_missing = extractor.extract("DOC_MISSING", "non_existent_file.txt", "NOC")
    assert ext_missing.is_readable is False
    assert "not found" in ext_missing.extracted_text.lower()

    # Unsupported format (.xyz)
    fake_path = Path("scratch_test.xyz")
    try:
        fake_path.write_text("dummy content")
        ext_unsupported = extractor.extract("DOC_UNSUPPORTED", str(fake_path), "NOC")
        assert ext_unsupported.is_readable is False
        assert "unsupported file extension" in ext_unsupported.extracted_text.lower()
    finally:
        if fake_path.exists():
            fake_path.unlink()


# =====================================================================
# TEST 7: Full Pipeline Validation of a Valid Document
# =====================================================================
def test_validate_clean_document(pipeline, demo_docs_dir):
    doc_input = DocumentInput(
        document_id="DOC_001",
        filename="valid_fire_noc.txt",
        document_type="Fire Safety NOC",
        file_path=str(demo_docs_dir / "valid_fire_noc.txt"),
        expected_entity_name="ABC Foods Pvt Ltd",
        expected_document_type="Fire Safety NOC",
    )

    result = pipeline.validate_document(doc_input)
    assert result.status in (DocumentStatus.VALID, DocumentStatus.WARNING)
    assert result.entity_match in (EntityMatchStatus.EXACT_MATCH, EntityMatchStatus.LIKELY_MATCH)
    assert result.expiry_status == ExpiryStatus.VALID
    assert len(result.errors) == 0
    assert result.confidence >= 0.75


# =====================================================================
# TEST 8: Full Pipeline Validation of an Expired Document
# =====================================================================
def test_validate_expired_document(pipeline, demo_docs_dir):
    doc_input = DocumentInput(
        document_id="DOC_004",
        filename="expired_factory_license.txt",
        document_type="Factory License",
        file_path=str(demo_docs_dir / "expired_factory_license.txt"),
        expected_entity_name="ABC Foods Pvt Ltd",
        expected_document_type="Factory License",
    )

    result = pipeline.validate_document(doc_input)
    assert result.status == DocumentStatus.REQUIRES_HUMAN_VERIFICATION
    assert result.expiry_status == ExpiryStatus.EXPIRED
    assert any("expired" in e.lower() for e in result.errors)
    assert result.requires_human_verification is True


# =====================================================================
# TEST 9: Full Pipeline Validation of an Entity Mismatch
# =====================================================================
def test_validate_entity_mismatch(pipeline, demo_docs_dir):
    doc_input = DocumentInput(
        document_id="DOC_003",
        filename="mismatched_entity_plan.md",
        document_type="Site Plan",
        file_path=str(demo_docs_dir / "mismatched_entity_plan.md"),
        expected_entity_name="ABC Foods Pvt Ltd",
        expected_document_type="Site Plan",
    )

    result = pipeline.validate_document(doc_input)
    assert result.status == DocumentStatus.REQUIRES_HUMAN_VERIFICATION
    assert result.entity_match == EntityMatchStatus.NO_MATCH
    assert any("mismatch" in e.lower() for e in result.errors)
    assert result.requires_human_verification is True


# =====================================================================
# TEST 10: Application Completeness Cross-Check
# =====================================================================
def test_application_completeness(pipeline, demo_docs_dir):
    uploaded = [
        DocumentInput(
            document_id="DOC_001",
            filename="valid_fire_noc.txt",
            document_type="Fire Safety NOC",
            file_path=str(demo_docs_dir / "valid_fire_noc.txt"),
        ),
        DocumentInput(
            document_id="DOC_002",
            filename="expiring_fssai.json",
            document_type="FSSAI Food License",
            file_path=str(demo_docs_dir / "expiring_fssai.json"),
        ),
    ]

    required = [
        "Fire Safety NOC",
        "FSSAI Food License",
        "Factory Site Plan",  # Missing
        "Potable Water Test", # Missing
    ]

    report = pipeline.validator.check_completeness(
        required_documents=required,
        uploaded_documents=uploaded,
        application_id="APP_2026_001",
    )

    assert report.completeness_percentage == 50.0
    assert report.is_complete is False
    assert len(report.matched_documents) == 2
    assert len(report.missing_documents) == 2
    assert "Factory Site Plan" in report.missing_documents
    assert "Potable Water Test" in report.missing_documents

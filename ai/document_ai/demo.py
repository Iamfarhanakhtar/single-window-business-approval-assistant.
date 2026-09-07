"""
Document AI & Pre-Validation CLI Demonstration

Demonstrates local text extraction, PII masking, entity matching, validity checking,
and application checklist completeness auditing without external cloud APIs.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
curr_path = Path(__file__).resolve().parent
project_root = curr_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ai.document_ai.models import DocumentInput
from ai.document_ai.pipeline import DocumentAIPipeline


def run_demo():
    print("========================================")
    print("BUSINESS COMPLIANCE HUB")
    print("DOCUMENT AI & PRE-VALIDATION")
    print("========================================")
    print()

    docs_dir = Path(__file__).resolve().parent / "demo_docs"

    expected_company = "Pragati Foods Pvt Ltd"
    print(f"Target Applicant Enterprise: '{expected_company}'")
    print()

    sample_uploads = [
        DocumentInput(
            document_id="DOC_001",
            filename="valid_fire_noc.txt",
            document_type="Fire Safety NOC",
            file_path=str(docs_dir / "valid_fire_noc.txt"),
            expected_entity_name=expected_company,
            expected_document_type="Fire Safety NOC",
            application_id="APP_2026_001",
        ),
        DocumentInput(
            document_id="DOC_002",
            filename="expiring_fssai.json",
            document_type="FSSAI Food License",
            file_path=str(docs_dir / "expiring_fssai.json"),
            expected_entity_name=expected_company,
            expected_document_type="FSSAI Food License",
            application_id="APP_2026_001",
        ),
        DocumentInput(
            document_id="DOC_003",
            filename="mismatched_entity_plan.md",
            document_type="Site Plan",
            file_path=str(docs_dir / "mismatched_entity_plan.md"),
            expected_entity_name=expected_company,
            expected_document_type="Site Plan",
            application_id="APP_2026_001",
        ),
        DocumentInput(
            document_id="DOC_004",
            filename="expired_factory_license.txt",
            document_type="Factory License",
            file_path=str(docs_dir / "expired_factory_license.txt"),
            expected_entity_name=expected_company,
            expected_document_type="Factory License",
            application_id="APP_2026_001",
        ),
    ]

    pipeline = DocumentAIPipeline()

    print("----------------------------------------------------------------------")
    print("INDIVIDUAL DOCUMENT PRE-VALIDATION RESULTS")
    print("----------------------------------------------------------------------")

    for doc in sample_uploads:
        result = pipeline.validate_document(doc)
        print(f"File: {result.filename} (ID: {result.document_id})")
        print(f"Status: [{result.status.value}]")
        print(f"Entity Match: {result.entity_match.value}")
        print(f"Validity Status: {result.expiry_status.value} (Days left: {result.days_until_expiry})")
        print(f"Type Alignment: {result.type_match.value}")
        print(f"Validation Confidence: {result.confidence * 100:.0f}%")
        
        if result.warnings:
            print("Warnings:")
            for w in result.warnings:
                print(f"  [!] {w}")

        if result.errors:
            print("Errors:")
            for e in result.errors:
                print(f"  [X] {e}")

        print()

    print("----------------------------------------------------------------------")
    print("APPLICATION CHECKLIST COMPLETENESS AUDIT")
    print("----------------------------------------------------------------------")

    # Sample required checklist from Step 2 Rule Engine
    required_checklist = [
        "Fire Safety NOC",
        "FSSAI Food License",
        "Site Plan",
        "Factory License",
        "Effluent Treatment Plant (ETP) Proposal",  # Intentionally missing from upload
        "Potable Water Test Report",                # Intentionally missing from upload
    ]

    audit = pipeline.audit_application(
        required_documents=required_checklist,
        uploaded_documents=sample_uploads,
        application_id="APP_2026_001",
    )

    comp = audit["completeness"]
    print(f"Total Required Documents: {len(comp['required_documents'])}")
    print(f"Total Uploaded Documents: {len(comp['uploaded_documents'])}")
    print(f"Matched Documents: {len(comp['matched_documents'])}")
    print(f"Missing Documents ({len(comp['missing_documents'])}):")
    for m in comp["missing_documents"]:
        print(f"  - {m}")
    print(f"Completeness: {comp['completeness_percentage']}%")
    print(f"Ready for Statutory Submission: {'YES' if audit['summary']['is_ready_for_submission'] else 'NO'}")
    print()

    print("======================================================================")
    print("PRIVACY & STATUTORY DISCLAIMER")
    print("======================================================================")
    print("All PII (Aadhaar, PAN, Bank Accounts) redacted locally before processing.")
    print("Document AI pre-validation is a data consistency and completeness check.")
    print("It does not replace administrative verification by statutory officers.")
    print("======================================================================")


if __name__ == "__main__":
    run_demo()

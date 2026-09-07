"""
Document AI Pre-Validation Pipeline

Coordinates local extraction, PII redaction, entity matching, expiry verification,
and checklist completeness cross-checks.
"""

from typing import List, Dict, Any, Optional
from ai.document_ai.models import (
    DocumentInput,
    ExtractedDocument,
    DocumentValidationResult,
    CompletenessReport,
)
from ai.document_ai.extractor import DocumentExtractor
from ai.document_ai.validator import DocumentValidator


class DocumentAIPipeline:
    """
    Unified pipeline for enterprise document pre-validation and completeness auditing.
    """

    def __init__(
        self,
        extractor: Optional[DocumentExtractor] = None,
        validator: Optional[DocumentValidator] = None,
    ):
        self.extractor = extractor or DocumentExtractor()
        self.validator = validator or DocumentValidator(extractor=self.extractor)

    def extract_document(self, doc_input: DocumentInput) -> ExtractedDocument:
        """Extracts text and metadata with PII redaction from an uploaded document."""
        return self.extractor.extract(
            document_id=doc_input.document_id,
            file_path=doc_input.file_path,
            document_type=doc_input.document_type,
        )

    def validate_document(self, doc_input: DocumentInput) -> DocumentValidationResult:
        """Extracts and executes pre-validation checks on a single uploaded document."""
        extracted = self.extract_document(doc_input)
        return self.validator.validate_document(doc_input, extracted=extracted)

    def validate_batch(self, documents: List[DocumentInput]) -> List[DocumentValidationResult]:
        """Validates a collection of uploaded documents."""
        return [self.validate_document(doc) for doc in documents]

    def audit_application(
        self,
        required_documents: List[str],
        uploaded_documents: List[DocumentInput],
        application_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Conducts an end-to-end audit comparing uploaded documents against the
        Rule Engine's required checklist, validating each document and computing completeness.
        """
        validation_results = self.validate_batch(uploaded_documents)
        completeness = self.validator.check_completeness(
            required_documents=required_documents,
            uploaded_documents=uploaded_documents,
            application_id=application_id,
        )

        valid_count = sum(1 for r in validation_results if r.status.value == "VALID")
        warning_count = sum(1 for r in validation_results if r.status.value == "WARNING")
        invalid_count = sum(1 for r in validation_results if r.status.value == "INVALID")
        unreadable_count = sum(1 for r in validation_results if r.status.value == "UNREADABLE")

        return {
            "application_id": application_id,
            "completeness": completeness.model_dump(),
            "document_validations": [r.model_dump() for r in validation_results],
            "summary": {
                "total_required": len(required_documents),
                "total_uploaded": len(uploaded_documents),
                "valid": valid_count,
                "warning": warning_count,
                "invalid": invalid_count,
                "unreadable": unreadable_count,
                "is_ready_for_submission": completeness.is_complete and invalid_count == 0 and unreadable_count == 0,
            },
            "requires_human_verification": True,
            "disclaimer": "Document AI pre-validation is a data consistency and completeness check. It does not replace statutory administrative verification by government authorities.",
        }


# Singleton instance
document_ai_pipeline = DocumentAIPipeline()

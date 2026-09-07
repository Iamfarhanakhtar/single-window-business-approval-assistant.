"""
Document AI & Pre-Validation Package for Business Compliance Hub

Provides local document text extraction, PII masking, entity matching,
validity period verification, and statutory checklist completeness auditing.
"""

from ai.document_ai.models import (
    DocumentInput,
    ExtractedDocument,
    DocumentValidationResult,
    DocumentStatus,
    EntityMatchStatus,
    ExpiryStatus,
    DocumentTypeMatch,
    CheckItem,
    CompletenessReport,
)
from ai.document_ai.pii_redactor import redact_pii
from ai.document_ai.entity_matcher import match_entity_names, normalize_entity_name
from ai.document_ai.expiry_checker import check_expiry, parse_date
from ai.document_ai.extractor import DocumentExtractor
from ai.document_ai.validator import DocumentValidator, check_document_type_match
from ai.document_ai.pipeline import DocumentAIPipeline, document_ai_pipeline

__all__ = [
    "DocumentInput",
    "ExtractedDocument",
    "DocumentValidationResult",
    "DocumentStatus",
    "EntityMatchStatus",
    "ExpiryStatus",
    "DocumentTypeMatch",
    "CheckItem",
    "CompletenessReport",
    "redact_pii",
    "match_entity_names",
    "normalize_entity_name",
    "check_expiry",
    "parse_date",
    "DocumentExtractor",
    "DocumentValidator",
    "check_document_type_match",
    "DocumentAIPipeline",
    "document_ai_pipeline",
]

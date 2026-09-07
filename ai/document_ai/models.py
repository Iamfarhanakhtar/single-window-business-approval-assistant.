"""
Strongly Typed Document AI Data Models

Defines input schemas, extraction results, validation checks, and completeness reports
with strict Pydantic v2 validation.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class DocumentStatus(str, Enum):
    """
    Categorical outcome of document pre-validation (data consistency only).
    Note: Pre-validation NEVER makes legal determinations.
    """
    VALID = "VALID"
    WARNING = "WARNING"
    INCOMPLETE = "INCOMPLETE"
    UNREADABLE = "UNREADABLE"
    REQUIRES_HUMAN_VERIFICATION = "REQUIRES_HUMAN_VERIFICATION"


class EntityMatchStatus(str, Enum):
    """Status of enterprise applicant name cross-check."""
    EXACT_MATCH = "EXACT_MATCH"
    LIKELY_MATCH = "LIKELY_MATCH"
    NO_MATCH = "NO_MATCH"
    UNKNOWN = "UNKNOWN"


class ExpiryStatus(str, Enum):
    """Status of document validity timeframe."""
    VALID = "VALID"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"
    NO_EXPIRY_INFORMATION = "NO_EXPIRY_INFORMATION"


class DocumentTypeMatch(str, Enum):
    """Status of document category classification."""
    MATCH = "MATCH"
    LIKELY_MATCH = "LIKELY_MATCH"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"


class DocumentInput(BaseModel):
    """Input payload representing an uploaded document for pre-validation."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    document_id: str = Field(..., description="Unique document upload identifier")
    filename: str = Field(..., description="Original filename (e.g. 'fire_noc_abc_foods.txt')")
    document_type: str = Field(..., description="Claimed/uploaded document type")
    file_path: str = Field(..., description="Path to local file on disk")
    expected_entity_name: Optional[str] = Field(default=None, description="Enterprise name from business profile")
    expected_document_type: Optional[str] = Field(default=None, description="Required document type from checklist")
    application_id: Optional[str] = Field(default=None, description="Associated single-window application ID")


class ExtractedDocument(BaseModel):
    """Structured fields extracted from document text with PII redaction."""
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    filename: str
    document_type: str
    extracted_text: str = Field(default="", description="Sanitized extracted text")
    redacted_text: str = Field(default="", description="PII-masked text for audit logs")
    entity_name: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    document_number: Optional[str] = None
    authority: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Extraction confidence score")
    is_readable: bool = Field(default=True, description="Whether text could be parsed cleanly")
    pii_detected: bool = Field(default=False, description="Whether sensitive PII tokens were masked")


class CheckItem(BaseModel):
    """Individual rule verification check result."""
    model_config = ConfigDict(from_attributes=True)

    check_name: str
    passed: bool
    details: str


class DocumentValidationResult(BaseModel):
    """Comprehensive pre-validation outcome for an uploaded document."""
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    filename: str
    status: DocumentStatus
    entity_match: EntityMatchStatus
    expiry_status: ExpiryStatus
    type_match: DocumentTypeMatch
    checks: List[CheckItem] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    days_until_expiry: Optional[int] = None
    requires_human_verification: bool = Field(default=True)


class CompletenessReport(BaseModel):
    """Cross-check comparing Rule Engine required documents against uploaded submissions."""
    model_config = ConfigDict(from_attributes=True)

    application_id: Optional[str] = None
    required_documents: List[str]
    uploaded_documents: List[str]
    matched_documents: List[str]
    missing_documents: List[str]
    completeness_percentage: float = Field(..., ge=0.0, le=100.0)
    is_complete: bool

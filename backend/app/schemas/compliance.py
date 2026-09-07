"""
Compliance Analysis and Document AI Schemas for SIH-130 API Contract
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# COMPLIANCE ANALYSIS SCHEMAS
# ---------------------------------------------------------------------------
class ComplianceAnalyzeRequest(BaseModel):
    """Business and project parameters for multi-pillar compliance analysis."""
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    sector: str = Field(..., description="Industrial sector (e.g. 'food_processing', 'manufacturing')")
    state: str = Field(default="Uttar Pradesh", description="State jurisdiction")
    district: Optional[str] = Field(default="Ghaziabad", description="District location")
    investment: float = Field(..., ge=0.0, description="Capital investment in INR")
    employees: int = Field(..., ge=1, description="Total workforce / employee count")
    project_stage: Optional[str] = Field(default="Pre-Operation", description="Project lifecycle stage")
    connected_load_kw: Optional[float] = Field(default=0.0, ge=0.0, description="Connected electrical load in kW")
    has_boiler: Optional[bool] = Field(default=False, description="Whether facility operates industrial steam boilers")
    is_food_business: Optional[bool] = Field(default=None, description="Explicit food business flag")
    water_requirement_kld: Optional[float] = Field(default=0.0, ge=0.0, description="Water requirement in KLD")
    hazardous_materials: Optional[bool] = Field(default=False, description="Hazardous chemicals or processes flag")
    built_up_area_sqm: Optional[float] = Field(default=0.0, ge=0.0, description="Total covered/built-up area in sqm")
    applicant_type: Optional[str] = Field(default="Enterprise", description="Applicant category (MSME, Large, etc.)")
    business_id: Optional[str] = Field(default=None, description="Optional DB Business ID")
    application_id: Optional[str] = Field(default=None, description="Optional DB Application ID")


class ApprovalItemResponse(BaseModel):
    """Details of an applicable or partially matched regulatory approval."""
    model_config = ConfigDict(from_attributes=True)

    approval_id: str
    approval_name: str
    authority: str
    status: str
    score: float
    reason: str
    documents: List[str] = Field(default_factory=list)
    processing_days: int
    statutory_fee: float = 0.0
    department: str = ""
    category: str = ""
    is_mandatory: bool = True
    prerequisites: List[str] = Field(default_factory=list)


class DocumentRequirementItem(BaseModel):
    """Aggregated statutory document requirement across all applicable clearances."""
    model_config = ConfigDict(from_attributes=True)

    document_name: str
    required_for: List[str] = Field(default_factory=list)
    status: str = "MISSING"


class RiskAnalysisResponse(BaseModel):
    """Composite compliance risk assessment from deterministic and ML signals."""
    model_config = ConfigDict(from_attributes=True)

    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str = Field(..., description="Risk category: LOW, MEDIUM, HIGH")
    factors: List[str] = Field(default_factory=list)


class DelayPredictionResponse(BaseModel):
    """ML-inferred probability of statutory SLA delay and estimated timeline."""
    model_config = ConfigDict(from_attributes=True)

    probability: float = Field(..., ge=0.0, le=1.0)
    predicted_days: float = Field(..., ge=0.0)
    factors: List[str] = Field(default_factory=list)
    is_synthetic_model: bool = True


class RegulatoryExplanationItem(BaseModel):
    """Source-grounded legal explanation for an approval requirement."""
    model_config = ConfigDict(from_attributes=True)

    approval_id: Optional[str] = None
    approval_name: str
    answer: str
    cited_acts: List[str] = Field(default_factory=list)
    confidence: float
    sources: List[Dict[str, Any]] = Field(default_factory=list)


class SourceReferenceItem(BaseModel):
    """Official act or regulation citation."""
    model_config = ConfigDict(from_attributes=True)

    source_name: str
    source_url: str
    authority: str
    jurisdiction: str
    is_official: bool = True


class ComplianceSummaryResponse(BaseModel):
    """Aggregated metrics for executive compliance roadmap."""
    model_config = ConfigDict(from_attributes=True)

    total_approvals: int
    potentially_applicable: int
    requires_verification: int
    documents_required: int


class ComplianceAnalyzeResponse(BaseModel):
    """Complete unified multi-pillar compliance analysis response."""
    model_config = ConfigDict(from_attributes=True)

    business_profile: Dict[str, Any]
    summary: ComplianceSummaryResponse
    approvals: List[ApprovalItemResponse]
    documents: List[DocumentRequirementItem]
    risk: RiskAnalysisResponse
    delay_prediction: DelayPredictionResponse
    recommendations: List[str] = Field(default_factory=list)
    regulatory_explanations: List[RegulatoryExplanationItem] = Field(default_factory=list)
    sources: List[SourceReferenceItem] = Field(default_factory=list)
    disclaimer: str = (
        "This compliance analysis is generated deterministically by the Rule Engine, "
        "supplemented by ML risk predictions and statutory RAG citations. "
        "It does not constitute statutory government approval."
    )


# ---------------------------------------------------------------------------
# DOCUMENT AI & PRE-VALIDATION SCHEMAS
# ---------------------------------------------------------------------------
class DocumentValidateRequest(BaseModel):
    """Request payload for validating a local or uploaded document."""
    model_config = ConfigDict(extra="allow")

    document_id: str
    filename: str
    document_type: str
    file_path: Optional[str] = None
    file_content_text: Optional[str] = None
    expected_entity_name: Optional[str] = None
    expected_document_type: Optional[str] = None
    application_id: Optional[str] = None


class CheckItemResponse(BaseModel):
    """Single rule pre-validation check result."""
    check_name: str
    passed: bool
    details: str


class DocumentValidationResponse(BaseModel):
    """Pre-validation audit results for an uploaded enterprise document."""
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    filename: str
    status: str
    entity_match: str
    expiry_status: str
    type_match: str
    checks: List[CheckItemResponse] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    days_until_expiry: Optional[int] = None
    requires_human_verification: bool = True
    redacted_preview: Optional[str] = None
    disclaimer: str = (
        "Document AI pre-validation is a data consistency and completeness check. "
        "It does not replace statutory administrative verification by government authorities."
    )


# ---------------------------------------------------------------------------
# SUBSYSTEM HEALTH DIAGNOSTIC SCHEMAS
# ---------------------------------------------------------------------------
class ComplianceHealthResponse(BaseModel):
    """Health and initialization diagnostics for all 4 AI/ML subsystems."""
    model_config = ConfigDict(from_attributes=True)

    status: str
    rule_engine: Dict[str, Any]
    ml_predictor: Dict[str, Any]
    rag_pipeline: Dict[str, Any]
    document_ai: Dict[str, Any]

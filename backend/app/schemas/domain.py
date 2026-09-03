"""Pydantic Schemas and Data Transfer Objects (DTOs) for SIH-130"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# ---------------------------------------------------------------------------
# AUTH & USER SCHEMAS
# ---------------------------------------------------------------------------
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    role: str = "entrepreneur"
    department_id: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    email: str
    full_name: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# BUSINESS & PROFILE SCHEMAS
# ---------------------------------------------------------------------------
class BusinessProfileBase(BaseModel):
    sector: str
    sub_sector: Optional[str] = None
    state: str
    district: str
    address: Optional[str] = None
    pincode: Optional[str] = None
    investment_amount: float = 0.0
    employee_count: int = 1
    built_up_area_sqm: Optional[float] = None
    power_requirement_kw: Optional[float] = None
    water_requirement_kld: Optional[float] = None
    hazardous_materials: bool = False
    details: Optional[Dict[str, Any]] = None

class BusinessProfileCreate(BusinessProfileBase):
    pass

class BusinessProfileResponse(BusinessProfileBase):
    id: str
    business_id: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BusinessBase(BaseModel):
    legal_name: str
    trade_name: Optional[str] = None
    registration_type: str
    pan_number: Optional[str] = None
    gstin: Optional[str] = None

class BusinessCreate(BusinessBase):
    profile: Optional[BusinessProfileCreate] = None

class BusinessResponse(BusinessBase):
    id: str
    user_id: str
    created_at: datetime
    profile: Optional[BusinessProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# DEPARTMENT & APPROVAL SCHEMAS
# ---------------------------------------------------------------------------
class ApprovalRequirementResponse(BaseModel):
    id: str
    document_type: str
    is_mandatory: bool
    description: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class ApprovalResponse(BaseModel):
    id: str
    code: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    sla_days: int
    validity_years: int
    statutory_fee: float
    requires_inspection: bool
    department_id: str
    requirements: List[ApprovalRequirementResponse] = []

    model_config = ConfigDict(from_attributes=True)

class DepartmentResponse(BaseModel):
    id: str
    code: str
    name: str
    state: Optional[str] = None
    description: Optional[str] = None
    sla_default_days: int
    is_active: bool
    approvals: List[ApprovalResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# APPLICATION SCHEMAS
# ---------------------------------------------------------------------------
class ApplicationApprovalResponse(BaseModel):
    id: str
    approval_id: str
    status: str
    sla_target_date: Optional[datetime] = None
    decision_date: Optional[datetime] = None
    decision_remarks: Optional[str] = None
    certificate_number: Optional[str] = None
    approval: Optional[ApprovalResponse] = None

    model_config = ConfigDict(from_attributes=True)

class ApplicationCreate(BaseModel):
    business_id: str
    approval_ids: List[str]  # Selected approvals to apply for

class ApplicationUpdateStatus(BaseModel):
    status: str
    remarks: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: str
    application_number: str
    business_id: str
    status: str
    submission_date: Optional[datetime] = None
    estimated_completion_date: Optional[datetime] = None
    overall_risk_score: float
    created_at: datetime
    updated_at: datetime
    application_approvals: List[ApplicationApprovalResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# DOCUMENT SCHEMAS
# ---------------------------------------------------------------------------
class DocumentValidationResponse(BaseModel):
    id: str
    status: str
    validation_score: float
    extracted_metadata: Optional[Dict[str, Any]] = None
    issues_detected: Optional[List[str]] = None
    validated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(BaseModel):
    id: str
    business_id: str
    application_id: Optional[str] = None
    document_type: str
    file_name: str
    file_size_bytes: int
    mime_type: str
    is_verified: bool
    is_reusable: bool
    uploaded_at: datetime
    validation: Optional[DocumentValidationResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# INSPECTION & QUERY SCHEMAS
# ---------------------------------------------------------------------------
class InspectionCreate(BaseModel):
    application_id: str
    department_id: str
    scheduled_date: datetime
    remarks: Optional[str] = None

class InspectionReportCreate(BaseModel):
    findings: str
    is_compliant: bool
    checklist_results: Optional[Dict[str, Any]] = None
    geo_latitude: Optional[float] = None
    geo_longitude: Optional[float] = None

class InspectionResponse(BaseModel):
    id: str
    application_id: str
    department_id: str
    scheduled_date: datetime
    status: str
    remarks: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class QueryCreate(BaseModel):
    application_id: str
    department_code: str
    query_text: str

class QueryRespond(BaseModel):
    response_text: str

class QueryResponse(BaseModel):
    id: str
    application_id: str
    raised_by_id: str
    department_code: str
    query_text: str
    response_text: Optional[str] = None
    status: str
    raised_at: datetime
    responded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# SLA, NOTIFICATIONS, RENEWALS & INCENTIVES
# ---------------------------------------------------------------------------
class SLARecordResponse(BaseModel):
    id: str
    application_id: str
    department_code: str
    target_days: int
    start_date: datetime
    due_date: datetime
    completion_date: Optional[datetime] = None
    is_breached: bool
    breach_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RenewalResponse(BaseModel):
    id: str
    business_id: str
    approval_code: str
    license_number: str
    expiry_date: datetime
    reminder_sent_date: Optional[datetime] = None
    is_renewed: bool

    model_config = ConfigDict(from_attributes=True)

class IncentiveResponse(BaseModel):
    id: str
    scheme_name: str
    authority: str
    eligible_sectors: Optional[List[str]] = None
    min_investment: float
    max_subsidy_amount: float
    subsidy_percentage: float
    description: str
    portal_link: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# AI & ML SERVICE CONTRACT SCHEMAS
# ---------------------------------------------------------------------------
class AnalyzeBusinessRequest(BaseModel):
    sector: str
    location: str
    investment: float
    employees: int
    business_details: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ApplicableApprovalItem(BaseModel):
    code: str
    name: str
    department: str
    category: str
    sla_days: int
    fee: float
    mandatory: bool
    prerequisites: List[str] = []

class AnalyzeBusinessResponse(BaseModel):
    applicable_approvals: List[ApplicableApprovalItem]
    required_documents: List[str]
    risk_score: float = Field(..., ge=0.0, le=1.0, description="0.0 low to 1.0 high risk")
    delay_probability: float = Field(..., ge=0.0, le=1.0)
    predicted_processing_days: int
    eligible_incentives: List[str] = []
    explanation: str

class PredictDelayRequest(BaseModel):
    sector: str
    state: str
    investment: float
    approval_codes: List[str]
    document_count: int
    has_hazardous: bool = False

class PredictDelayResponse(BaseModel):
    delay_probability: float
    expected_delay_days: int
    risk_factors: List[str]
    recommendation: str

class PredictClarificationRequest(BaseModel):
    sector: str
    approval_code: str
    uploaded_doc_types: List[str]
    missing_doc_types: List[str]

class PredictClarificationResponse(BaseModel):
    clarification_probability: float
    common_deficiencies: List[str]
    guidance: str

class ValidateDocRequest(BaseModel):
    document_type: str
    file_name: str
    extracted_text: Optional[str] = None

class ValidateDocResponse(BaseModel):
    status: str  # VALID, INVALID, WARNING
    confidence_score: float
    extracted_fields: Dict[str, Any] = Field(default_factory=dict)
    issues_detected: List[str] = []
    recommendation: str

class AskRAGRequest(BaseModel):
    question: str
    sector: Optional[str] = None
    state: Optional[str] = None

class AskRAGResponse(BaseModel):
    answer: str
    cited_acts: List[str]
    confidence: float
    relevant_sections: List[str]

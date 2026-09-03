"""SQLAlchemy Database Models for SIH Problem Statement 130"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import relationship
from app.database.connection import Base
import enum

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------
class UserRoleEnum(str, enum.Enum):
    ENTREPRENEUR = "entrepreneur"
    GOVERNMENT_OFFICER = "government_officer"
    DEPARTMENT_OFFICER = "department_officer"
    ADMINISTRATOR = "administrator"

class ApplicationStatusEnum(str, enum.Enum):
    DRAFT = "DRAFT"
    DOCUMENT_CHECK = "DOCUMENT_CHECK"
    READY_FOR_SUBMISSION = "READY_FOR_SUBMISSION"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    INSPECTION_REQUIRED = "INSPECTION_REQUIRED"
    INSPECTION_SCHEDULED = "INSPECTION_SCHEDULED"
    INSPECTION_COMPLETED = "INSPECTION_COMPLETED"
    QUERY_RAISED = "QUERY_RAISED"
    RESUBMITTED = "RESUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RENEWAL_MONITORING = "RENEWAL_MONITORING"

class ApprovalStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    INSPECTION_SCHEDULED = "INSPECTION_SCHEDULED"
    QUERY_RAISED = "QUERY_RAISED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class InspectionStatusEnum(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class QueryStatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    RESPONDED = "RESPONDED"
    RESOLVED = "RESOLVED"

class DocValidationStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    VALID = "VALID"
    INVALID = "INVALID"
    WARNING = "WARNING"


# ---------------------------------------------------------------------------
# USER & RBAC ENTITIES
# ---------------------------------------------------------------------------
class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    users = relationship("User", back_populates="role_rel")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    role = Column(String(50), nullable=False, default=UserRoleEnum.ENTREPRENEUR.value)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    role_rel = relationship("Role", back_populates="users")
    department = relationship("Department", back_populates="officers")
    businesses = relationship("Business", back_populates="owner")
    notifications = relationship("Notification", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


# ---------------------------------------------------------------------------
# BUSINESS & PROFILE ENTITIES
# ---------------------------------------------------------------------------
class Business(Base):
    __tablename__ = "businesses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    legal_name = Column(String(255), nullable=False)
    trade_name = Column(String(255), nullable=True)
    registration_type = Column(String(50), nullable=False)  # Pvt Ltd, LLP, Prop, etc.
    pan_number = Column(String(20), nullable=True, index=True)
    gstin = Column(String(20), nullable=True, index=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    owner = relationship("User", back_populates="businesses")
    profile = relationship("BusinessProfile", back_populates="business", uselist=False)
    applications = relationship("Application", back_populates="business")
    documents = relationship("Document", back_populates="business")
    renewals = relationship("Renewal", back_populates="business")


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("businesses.id"), unique=True, nullable=False)
    sector = Column(String(100), nullable=False)  # e.g., Food Processing, Chemicals, Textile
    sub_sector = Column(String(100), nullable=True)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    address = Column(Text, nullable=True)
    pincode = Column(String(10), nullable=True)
    investment_amount = Column(Float, nullable=False, default=0.0)  # in INR
    employee_count = Column(Integer, nullable=False, default=1)
    built_up_area_sqm = Column(Float, nullable=True)
    power_requirement_kw = Column(Float, nullable=True)
    water_requirement_kld = Column(Float, nullable=True)
    hazardous_materials = Column(Boolean, default=False)
    details = Column(JSON, nullable=True)  # custom sector attributes
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    business = relationship("Business", back_populates="profile")


# ---------------------------------------------------------------------------
# DEPARTMENT & APPROVAL ENTITIES
# ---------------------------------------------------------------------------
class Department(Base):
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False)  # e.g., UPPCB, FIRE_DEPT, FSSAI, LABOUR
    name = Column(String(255), nullable=False)
    state = Column(String(100), nullable=True)  # Central or specific state
    description = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    sla_default_days = Column(Integer, default=15)
    is_active = Column(Boolean, default=True)

    officers = relationship("User", back_populates="department")
    approvals = relationship("Approval", back_populates="department")
    inspections = relationship("Inspection", back_populates="department")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=False)
    code = Column(String(50), unique=True, nullable=False)  # e.g., FIRE_NOC, PCB_CTE, FSSAI_MFG
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)  # Environmental, Safety, Operational, Labor
    description = Column(Text, nullable=True)
    sla_days = Column(Integer, default=15)
    validity_years = Column(Integer, default=1)
    statutory_fee = Column(Float, default=0.0)
    requires_inspection = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    department = relationship("Department", back_populates="approvals")
    requirements = relationship("ApprovalRequirement", back_populates="approval")
    application_approvals = relationship("ApplicationApproval", back_populates="approval")


class ApprovalRequirement(Base):
    __tablename__ = "approval_requirements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    approval_id = Column(String(36), ForeignKey("approvals.id"), nullable=False)
    document_type = Column(String(100), nullable=False)  # e.g., Site Plan, Water Balance, PAN Card
    is_mandatory = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    validation_rules = Column(JSON, nullable=True)  # schema, file types, size limits

    approval = relationship("Approval", back_populates="requirements")


# ---------------------------------------------------------------------------
# REGULATIONS & SOURCES
# ---------------------------------------------------------------------------
class RegulatorySource(Base):
    __tablename__ = "regulatory_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)  # e.g., Factories Act 1948, Water Act 1974
    jurisdiction = Column(String(100), default="Central")
    source_url = Column(String(500), nullable=True)
    last_updated = Column(DateTime, default=utc_now)

    regulations = relationship("Regulation", back_populates="source")


class Regulation(Base):
    __tablename__ = "regulations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(String(36), ForeignKey("regulatory_sources.id"), nullable=True)
    section_code = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    full_text = Column(Text, nullable=True)
    applicable_sectors = Column(JSON, nullable=True)  # list of applicable sectors
    embedding_id = Column(String(100), nullable=True)  # link to vector DB chunk

    source = relationship("RegulatorySource", back_populates="regulations")


# ---------------------------------------------------------------------------
# APPLICATION & WORKFLOW ENTITIES
# ---------------------------------------------------------------------------
class Application(Base):
    __tablename__ = "applications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_number = Column(String(50), unique=True, nullable=False, index=True)
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    status = Column(String(50), default=ApplicationStatusEnum.DRAFT.value, nullable=False)
    submission_date = Column(DateTime, nullable=True)
    estimated_completion_date = Column(DateTime, nullable=True)
    overall_risk_score = Column(Float, default=0.0)  # 0.0 (low) to 1.0 (high)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    business = relationship("Business", back_populates="applications")
    application_approvals = relationship("ApplicationApproval", back_populates="application")
    documents = relationship("Document", back_populates="application")
    inspections = relationship("Inspection", back_populates="application")
    queries = relationship("QueryRecord", back_populates="application")
    sla_records = relationship("SLARecord", back_populates="application")
    ml_predictions = relationship("MLPrediction", back_populates="application")


class ApplicationApproval(Base):
    """Tracks parallel departmental approvals under a single master application"""
    __tablename__ = "application_approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    approval_id = Column(String(36), ForeignKey("approvals.id"), nullable=False)
    status = Column(String(50), default=ApprovalStatusEnum.PENDING.value, nullable=False)
    assigned_officer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    sla_target_date = Column(DateTime, nullable=True)
    decision_date = Column(DateTime, nullable=True)
    decision_remarks = Column(Text, nullable=True)
    certificate_number = Column(String(100), nullable=True)
    certificate_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    application = relationship("Application", back_populates="application_approvals")
    approval = relationship("Approval", back_populates="application_approvals")
    assigned_officer = relationship("User")


# ---------------------------------------------------------------------------
# DOCUMENTS & VALIDATION
# ---------------------------------------------------------------------------
class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=True)
    document_type = Column(String(100), nullable=False)  # e.g., PAN, Site Plan, Project Report
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_reusable = Column(Boolean, default=True)  # Can be reused for future applications
    uploaded_at = Column(DateTime, default=utc_now)

    business = relationship("Business", back_populates="documents")
    application = relationship("Application", back_populates="documents")
    validation = relationship("DocumentValidation", back_populates="document", uselist=False)


class DocumentValidation(Base):
    __tablename__ = "document_validations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), unique=True, nullable=False)
    status = Column(String(50), default=DocValidationStatusEnum.PENDING.value)
    validation_score = Column(Float, default=0.0)  # 0.0 to 1.0 confidence
    extracted_metadata = Column(JSON, nullable=True)  # extracted dates, IDs, signatures
    issues_detected = Column(JSON, nullable=True)  # list of warnings or error strings
    validated_at = Column(DateTime, default=utc_now)

    document = relationship("Document", back_populates="validation")


# ---------------------------------------------------------------------------
# INSPECTIONS & QUERIES
# ---------------------------------------------------------------------------
class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=False)
    inspector_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    scheduled_date = Column(DateTime, nullable=False)
    status = Column(String(50), default=InspectionStatusEnum.SCHEDULED.value)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    application = relationship("Application", back_populates="inspections")
    department = relationship("Department", back_populates="inspections")
    inspector = relationship("User")
    report = relationship("InspectionReport", back_populates="inspection", uselist=False)


class InspectionReport(Base):
    __tablename__ = "inspection_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    inspection_id = Column(String(36), ForeignKey("inspections.id"), unique=True, nullable=False)
    findings = Column(Text, nullable=False)
    is_compliant = Column(Boolean, default=True)
    checklist_results = Column(JSON, nullable=True)
    geo_latitude = Column(Float, nullable=True)
    geo_longitude = Column(Float, nullable=True)
    submitted_at = Column(DateTime, default=utc_now)

    inspection = relationship("Inspection", back_populates="report")


class QueryRecord(Base):
    __tablename__ = "queries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    raised_by_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    department_code = Column(String(50), nullable=False)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)
    status = Column(String(50), default=QueryStatusEnum.OPEN.value)
    raised_at = Column(DateTime, default=utc_now)
    responded_at = Column(DateTime, nullable=True)

    application = relationship("Application", back_populates="queries")
    raised_by = relationship("User")


# ---------------------------------------------------------------------------
# SLA, NOTIFICATIONS, RENEWALS & INCENTIVES
# ---------------------------------------------------------------------------
class SLARecord(Base):
    __tablename__ = "sla_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    department_code = Column(String(50), nullable=False)
    target_days = Column(Integer, nullable=False)
    start_date = Column(DateTime, default=utc_now)
    due_date = Column(DateTime, nullable=False)
    completion_date = Column(DateTime, nullable=True)
    is_breached = Column(Boolean, default=False)
    breach_reason = Column(Text, nullable=True)

    application = relationship("Application", back_populates="sla_records")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="INFO")  # INFO, WARNING, SLA_ALERT, ACTION_REQUIRED
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="notifications")


class Renewal(Base):
    __tablename__ = "renewals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    approval_code = Column(String(50), nullable=False)
    license_number = Column(String(100), nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    reminder_sent_date = Column(DateTime, nullable=True)
    is_renewed = Column(Boolean, default=False)

    business = relationship("Business", back_populates="renewals")


class Incentive(Base):
    __tablename__ = "incentives"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scheme_name = Column(String(255), nullable=False)
    authority = Column(String(100), nullable=False)  # State or Central Ministry
    eligible_sectors = Column(JSON, nullable=True)
    min_investment = Column(Float, default=0.0)
    max_subsidy_amount = Column(Float, default=0.0)
    subsidy_percentage = Column(Float, default=0.0)
    description = Column(Text, nullable=False)
    portal_link = Column(String(500), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(36), nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("User", back_populates="audit_logs")


class MLPrediction(Base):
    __tablename__ = "ml_predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False)
    prediction_type = Column(String(50), nullable=False)  # DELAY_RISK, CLARIFICATION_RISK
    predicted_delay_days = Column(Integer, default=0)
    delay_probability = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    feature_importance = Column(JSON, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    application = relationship("Application", back_populates="ml_predictions")

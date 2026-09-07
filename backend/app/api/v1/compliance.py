"""
Unified Compliance Analysis and Health API Endpoints (SIH-130)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.compliance import (
    ComplianceAnalyzeRequest,
    ComplianceAnalyzeResponse,
    ComplianceHealthResponse,
    DocumentValidateRequest,
    DocumentValidationResponse,
)
from app.services.compliance_analysis_service import compliance_service

router = APIRouter(prefix="/compliance", tags=["Compliance Intelligence"])


@router.post(
    "/analyze",
    response_model=ComplianceAnalyzeResponse,
    summary="Master Multi-Pillar Compliance Analysis",
    description="Evaluates business profile via Deterministic Rule Engine, ML delay/risk models, and Regulatory RAG.",
)
def analyze_compliance(
    request: ComplianceAnalyzeRequest,
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/compliance/analyze
    Accepts business profile and project parameters, computes statutory approvals,
    document requirements, risk score, delay probability, and cited statutory justifications.
    """
    try:
        return compliance_service.analyze_compliance(request, db_session=db)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance analysis failed: {str(e)}",
        )


@router.get(
    "/health",
    response_model=ComplianceHealthResponse,
    summary="AI/ML Intelligence Subsystem Health Probe",
    description="Checks operational status and dataset readiness of Rule Engine, ML models, RAG, and Document AI.",
)
def check_compliance_health():
    """
    GET /api/v1/compliance/health
    Returns health state across all 4 intelligence engines.
    """
    try:
        return compliance_service.check_health()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Compliance subsystem health check failed: {str(e)}",
        )


@router.post(
    "/validate-document",
    response_model=DocumentValidationResponse,
    summary="Pre-validate Enterprise Document",
    description="Inspects local document text for readability, corporate name match, validity period, and category alignment.",
)
def pre_validate_document(request: DocumentValidateRequest):
    """
    POST /api/v1/compliance/validate-document
    Executes local privacy-safe pre-validation without sending data to external cloud APIs.
    """
    try:
        return compliance_service.validate_document(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document pre-validation error: {str(e)}",
        )

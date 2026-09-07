"""AI & Regulatory Intelligence Gateway Routes (Live AI/ML Integration)"""
from fastapi import APIRouter
from app.schemas.domain import (
    AnalyzeBusinessRequest,
    AnalyzeBusinessResponse,
    ApplicableApprovalItem,
    PredictDelayRequest,
    PredictDelayResponse,
    PredictClarificationRequest,
    PredictClarificationResponse,
    ValidateDocRequest,
    ValidateDocResponse,
    AskRAGRequest,
    AskRAGResponse
)
from app.schemas.compliance import ComplianceAnalyzeRequest, DocumentValidateRequest
from app.services.compliance_analysis_service import compliance_service
from ai.rag.pipeline import rag_pipeline
from ml.inference.predictor import risk_predictor

router = APIRouter(prefix="/ai", tags=["AI & Regulatory Intelligence"])

@router.post("/analyze-business", response_model=AnalyzeBusinessResponse)
def analyze_business_profile(request: AnalyzeBusinessRequest):
    """
    POST /ai/analyze-business
    Analyzes business parameters with deterministic Rule Engine and ML models.
    """
    comp_req = ComplianceAnalyzeRequest(
        sector=request.sector,
        state=request.location or "Uttar Pradesh",
        investment=float(request.investment),
        employees=int(request.employees),
        project_stage="Pre-Operation",
        business_id=None,
    )
    res = compliance_service.analyze_compliance(comp_req)

    app_items = [
        ApplicableApprovalItem(
            code=a.approval_id,
            name=a.approval_name,
            department=a.authority,
            category=a.category or "General",
            sla_days=a.processing_days,
            fee=a.statutory_fee,
            mandatory=a.is_mandatory,
            prerequisites=a.prerequisites,
        )
        for a in res.approvals
    ]

    return AnalyzeBusinessResponse(
        applicable_approvals=app_items,
        required_documents=[d.document_name for d in res.documents],
        risk_score=round(res.risk.risk_score / 100.0, 2),
        delay_probability=res.delay_prediction.probability,
        predicted_processing_days=int(round(res.delay_prediction.predicted_days)),
        eligible_incentives=[
            "UP Food Processing Industry Policy 2023 - 35% Capital Subsidy",
            "Interest Subvention Scheme (5% for 5 years)",
        ] if "food" in request.sector.lower() else ["Industrial Investment Promotion Scheme"],
        explanation="Deterministic Rule Engine identified statutory clearances. ML model estimated processing duration and risk factors."
    )

@router.post("/predict-delay", response_model=PredictDelayResponse)
def predict_processing_delay(request: PredictDelayRequest):
    """
    POST /ai/predict-delay
    Evaluates risk factors and predicts approval bottlenecks.
    """
    features = {
        "investment": float(request.investment),
        "employees": 50,
        "approval_count": max(1, len(request.approval_codes)),
        "document_count": max(1, request.document_count),
        "missing_document_count": 0,
        "inspection_required": bool(request.has_hazardous),
        "department_count": 2,
        "previous_queries": 0,
        "sla_days": 30,
        "state": request.state or "Uttar Pradesh",
        "sector": request.sector or "Manufacturing",
    }
    ml_res = risk_predictor.predict(features)
    return PredictDelayResponse(
        delay_probability=ml_res["delay_probability"],
        expected_delay_days=int(round(ml_res["predicted_processing_days"])),
        risk_factors=ml_res["risk_factors"],
        recommendation="Submit parallel applications and pre-validate documentation to minimize clearance lead time."
    )

@router.post("/predict-clarification", response_model=PredictClarificationResponse)
def predict_clarification_risk(request: PredictClarificationRequest):
    """
    POST /ai/predict-clarification
    Forecasts probability of deficiency queries from scrutiny officers based on document gaps.
    """
    missing_cnt = len(request.missing_doc_types)
    prob = min(0.95, round(0.15 + (missing_cnt * 0.25), 2))
    deficiencies = [f"Missing {d}" for d in request.missing_doc_types] if request.missing_doc_types else ["No obvious document deficiencies detected."]
    return PredictClarificationResponse(
        clarification_probability=prob,
        common_deficiencies=deficiencies,
        guidance="Upload complete statutory documents prior to application lock to avoid scrutiny query rounds."
    )

@router.post("/validate-document", response_model=ValidateDocResponse)
def pre_validate_document(request: ValidateDocRequest):
    """
    POST /ai/validate-document
    Pre-validates document formatting and checklist criteria.
    """
    val_res = compliance_service.validate_document(DocumentValidateRequest(
        document_id="DOC_TEMP",
        filename=request.file_name,
        document_type=request.document_type,
        file_content_text=request.extracted_text,
    ))
    return ValidateDocResponse(
        status=val_res.status,
        confidence_score=val_res.confidence,
        extracted_fields={"days_until_expiry": val_res.days_until_expiry, "entity_match": val_res.entity_match},
        issues_detected=val_res.warnings + val_res.errors,
        recommendation="Ensure document certificate number and validity dates are clearly legible."
    )

@router.post("/ask", response_model=AskRAGResponse)
def ask_regulatory_rag(request: AskRAGRequest):
    """
    POST /ai/ask
    RAG-powered regulatory Q&A assistant for entrepreneurs.
    """
    rag_res = rag_pipeline.ask(
        query=request.question,
        state=request.state or "Uttar Pradesh",
        top_k=4,
    )
    relevant = [
        f"{c.get('source_name', 'Act')} - {c.get('section', 'Clause')}"
        for c in rag_res.get("retrieved_chunks", [])
    ]
    return AskRAGResponse(
        answer=rag_res.get("answer", "No statutory evidence found for query."),
        cited_acts=rag_res.get("cited_acts", []),
        confidence=float(rag_res.get("confidence", 0.0)),
        relevant_sections=relevant
    )


"""AI & Regulatory Intelligence Gateway Routes (Contract Implementation)"""
from fastapi import APIRouter
from app.schemas.domain import (
    AnalyzeBusinessRequest,
    AnalyzeBusinessResponse,
    PredictDelayRequest,
    PredictDelayResponse,
    PredictClarificationRequest,
    PredictClarificationResponse,
    ValidateDocRequest,
    ValidateDocResponse,
    AskRAGRequest,
    AskRAGResponse
)
from ai.services.mock_ai_service import mock_ai_service

router = APIRouter(prefix="/ai", tags=["AI & Regulatory Intelligence"])

@router.post("/analyze-business", response_model=AnalyzeBusinessResponse)
def analyze_business_profile(request: AnalyzeBusinessRequest):
    """
    POST /ai/analyze-business
    Analyzes business parameters and generates dynamic statutory approval checklist,
    required documents, and risk/delay scores.
    """
    return mock_ai_service.analyze_business(request)

@router.post("/predict-delay", response_model=PredictDelayResponse)
def predict_processing_delay(request: PredictDelayRequest):
    """
    POST /ai/predict-delay
    Evaluates risk factors and predicts approval bottlenecks.
    """
    return mock_ai_service.predict_delay(request)

@router.post("/predict-clarification", response_model=PredictClarificationResponse)
def predict_clarification_risk(request: PredictClarificationRequest):
    """
    POST /ai/predict-clarification
    Forecasts probability of deficiency queries from scrutiny officers.
    """
    return mock_ai_service.predict_clarification(request)

@router.post("/validate-document", response_model=ValidateDocResponse)
def pre_validate_document(request: ValidateDocRequest):
    """
    POST /ai/validate-document
    Pre-validates document formatting and checklist criteria.
    """
    return mock_ai_service.validate_document(request)

@router.post("/ask", response_model=AskRAGResponse)
def ask_regulatory_rag(request: AskRAGRequest):
    """
    POST /ai/ask
    RAG-powered regulatory Q&A assistant for entrepreneurs.
    """
    return mock_ai_service.ask_regulatory_rag(request)

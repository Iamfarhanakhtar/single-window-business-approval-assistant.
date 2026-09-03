"""Abstract AI Service Interface - Developer 1 Contract"""
from abc import ABC, abstractmethod
from typing import Dict, Any
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

class AIServiceInterface(ABC):
    @abstractmethod
    def analyze_business(self, request: AnalyzeBusinessRequest) -> AnalyzeBusinessResponse:
        """Determines applicable approvals, documents, and initial risk score."""
        pass

    @abstractmethod
    def predict_delay(self, request: PredictDelayRequest) -> PredictDelayResponse:
        """ML inference for bottleneck probability and expected delay."""
        pass

    @abstractmethod
    def predict_clarification(self, request: PredictClarificationRequest) -> PredictClarificationResponse:
        """Predicts risk of department queries/deficiency memos."""
        pass

    @abstractmethod
    def validate_document(self, request: ValidateDocRequest) -> ValidateDocResponse:
        """Pre-validates document schema, metadata, and validity."""
        pass

    @abstractmethod
    def ask_regulatory_rag(self, request: AskRAGRequest) -> AskRAGResponse:
        """RAG Q&A over acts, state rules, and single-window policies."""
        pass

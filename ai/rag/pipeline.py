"""
Regulatory RAG Pipeline and Rule Engine Integration Bridge

Provides the unified ask() API and explain_approval() bridge connecting
the Deterministic Rule Engine to source-grounded regulatory retrieval.
"""

from typing import Optional, Dict, Any, Union
from ai.rag.models import (
    GeneratedAnswer,
)
from ai.rag.retriever import RegulatoryRetriever
from ai.rag.generator import RegulatoryAnswerGenerator
from ai.rules.models import BusinessProfile


class RegulatoryRAGPipeline:
    """
    End-to-end RAG pipeline for statutory document retrieval and evidence-grounded answers.
    """

    def __init__(
        self,
        regulations_dir: Optional[str] = None,
        retriever: Optional[RegulatoryRetriever] = None,
        generator: Optional[RegulatoryAnswerGenerator] = None,
    ):
        if retriever:
            self.retriever = retriever
        else:
            from ai.rag.ingest import RegulatoryDataIngester
            ingester = RegulatoryDataIngester(regulations_dir=regulations_dir) if regulations_dir else None
            self.retriever = RegulatoryRetriever(ingester=ingester)

        self.generator = generator or RegulatoryAnswerGenerator()

    def ask(
        self,
        query: str,
        top_k: int = 5,
        state: Optional[str] = None,
        approval_id: Optional[str] = None,
        authority: Optional[str] = None,
        min_score: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Answers a compliance inquiry grounded strictly in retrieved statutory evidence.
        """
        evidence = self.retriever.search(
            query=query,
            top_k=top_k,
            min_score=min_score,
            state=state,
            approval_id=approval_id,
            authority=authority,
        )

        answer_obj: GeneratedAnswer = self.generator.generate_answer(query, evidence)
        return answer_obj.model_dump()

    def explain_approval(
        self,
        approval_name: str,
        approval_id: str,
        business_profile: Optional[Union[BusinessProfile, Dict[str, Any]]] = None,
        state: Optional[str] = "Uttar Pradesh",
    ) -> Dict[str, Any]:
        """
        Bridge method connecting Rule Engine approval output to RAG retrieval.
        Combines approval name, ID, and business context into a focused retrieval query.
        """
        context_parts = [approval_name, approval_id]

        if business_profile:
            if isinstance(business_profile, BusinessProfile):
                context_parts.append(f"state: {business_profile.state}")
                context_parts.append(f"sector: {business_profile.sector}")
                if business_profile.project_stage:
                    context_parts.append(f"stage: {business_profile.project_stage}")
                if business_profile.has_boiler:
                    context_parts.append("industrial steam boiler")
                if business_profile.connected_load_kw > 0:
                    context_parts.append(f"power load: {business_profile.connected_load_kw} kW")
            elif isinstance(business_profile, dict):
                for k, v in business_profile.items():
                    if v and k in ("state", "sector", "stage", "project_stage"):
                        context_parts.append(f"{k}: {v}")

        composite_query = " ".join(context_parts)

        return self.ask(
            query=composite_query,
            approval_id=approval_id,
            state=state,
            top_k=3,
        )


# Singleton instance
rag_pipeline = RegulatoryRAGPipeline()

"""
Source-Grounded Answer and Citation Generator

Generates explainable answers strictly from retrieved statutory evidence.
Enforces zero hallucination: returns INSUFFICIENT_EVIDENCE when no verified context matches.
"""

from typing import List, Set
from ai.rag.models import (
    RetrievedChunk,
    SourceItem,
    GeneratedAnswer,
)

VERIFICATION_NOTICE = (
    "Always verify current requirements against the relevant official authority before submission."
)


class RegulatoryAnswerGenerator:
    """
    Constructs explainable compliance answers directly grounded in retrieved statutory text.
    """

    def generate_answer(self, query: str, evidence: List[RetrievedChunk]) -> GeneratedAnswer:
        """
        Synthesizes a grounded answer from retrieved evidence chunks.
        """
        if not evidence:
            return GeneratedAnswer(
                query=query,
                answer="INSUFFICIENT_EVIDENCE: No verified statutory provisions or approval criteria were found matching your inquiry.",
                confidence=0.0,
                sources=[],
                evidence_found=False,
                requires_verification=True,
                evidence=[],
                verification_notice=VERIFICATION_NOTICE,
            )

        # Extract structured citations
        sources: List[SourceItem] = []
        seen_sources: Set[str] = set()

        for chunk in evidence:
            s_key = f"{chunk.document_id}_{chunk.section}"
            if s_key not in seen_sources:
                seen_sources.add(s_key)
                sources.append(
                    SourceItem(
                        document_id=chunk.document_id,
                        title=chunk.document_title,
                        section=chunk.section,
                        source_url=chunk.source_url,
                        relevance_score=chunk.relevance_score,
                    )
                )

        # Format evidence excerpts
        evidence_texts = [f"[{c.document_title} - {c.section}]: {c.text}" for c in evidence]

        # Construct grounded answer
        top_chunk = evidence[0]
        points: List[str] = []
        for idx, chunk in enumerate(evidence, 1):
            points.append(
                f"{idx}. {chunk.document_title} ({chunk.section}): {chunk.text}"
            )

        answer_text = (
            f"The retrieved regulatory material indicates the following statutory requirements under {top_chunk.jurisdiction} jurisdiction:\n\n"
            + "\n\n".join(points)
        )

        # Average confidence from top scores
        avg_confidence = round(sum(c.relevance_score for c in evidence) / len(evidence), 2)

        return GeneratedAnswer(
            query=query,
            answer=answer_text,
            confidence=avg_confidence,
            sources=sources,
            evidence_found=True,
            requires_verification=True,
            evidence=evidence_texts,
            verification_notice=VERIFICATION_NOTICE,
        )

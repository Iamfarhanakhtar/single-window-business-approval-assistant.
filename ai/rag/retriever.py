"""
Regulatory Document Retriever

Provides semantic vector similarity and keyword retrieval over statutory chunks
with metadata filtering (jurisdiction, approval ID, authority) and score ranking.
"""

from typing import List, Optional
import numpy as np

from ai.rag.models import (
    DocumentChunk,
    RetrievedChunk,
    RegulatoryDocument,
)
from ai.rag.embeddings import (
    EmbeddingProvider,
    TFIDFEmbeddingProvider,
    default_embedding_provider,
)
from ai.rag.ingest import RegulatoryDataIngester
from ai.rag.chunk import chunk_all_documents


class RegulatoryRetriever:
    """
    Retrieves ranked statutory evidence chunks matching compliance queries.
    """

    def __init__(
        self,
        ingester: Optional[RegulatoryDataIngester] = None,
        embedding_provider: Optional[EmbeddingProvider] = None,
    ):
        self.ingester = ingester or RegulatoryDataIngester()
        self.embedding_provider = embedding_provider or default_embedding_provider

        # Ingest and chunk documents
        self.documents: List[RegulatoryDocument] = self.ingester.ingest_all()
        self.chunks: List[DocumentChunk] = chunk_all_documents(self.documents)

        # Build search index
        corpus = [c.text for c in self.chunks]
        if isinstance(self.embedding_provider, TFIDFEmbeddingProvider):
            self.embedding_provider.fit_corpus(corpus)

        self.total_documents_indexed = len(self.documents)
        self.total_chunks_indexed = len(self.chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.05,
        state: Optional[str] = None,
        approval_id: Optional[str] = None,
        authority: Optional[str] = None,
    ) -> List[RetrievedChunk]:
        """
        Executes hybrid similarity search with metadata filtering.
        """
        if not query or not query.strip() or len(self.chunks) == 0:
            return []

        # Compute similarities
        if isinstance(self.embedding_provider, TFIDFEmbeddingProvider):
            scores = self.embedding_provider.compute_similarity(query)
        else:
            # Generic vector cosine calculation
            q_emb = np.array(self.embedding_provider.embed_text(query))
            doc_embs = np.array(self.embedding_provider.embed_documents([c.text for c in self.chunks]))
            scores = np.dot(doc_embs, q_emb) / (np.linalg.norm(doc_embs, axis=1) * np.linalg.norm(q_emb) + 1e-9)

        if len(scores) == 0:
            return []

        # Sort indices descending
        ranked_indices = np.argsort(scores)[::-1]
        results: List[RetrievedChunk] = []

        for idx in ranked_indices:
            score = float(scores[idx])
            if score < min_score:
                continue

            chunk = self.chunks[idx]

            # 1. State filter
            if state:
                req_state = state.strip().lower()
                chunk_jur = chunk.jurisdiction.strip().lower()
                is_universal = chunk_jur in ("central", "national", "all india", "uttar pradesh / central")
                if not (is_universal or req_state in chunk_jur):
                    continue

            # 2. Authority filter
            if authority:
                req_auth = authority.strip().lower()
                if req_auth not in chunk.authority.strip().lower():
                    continue

            # 3. Approval ID filter
            if approval_id:
                req_aid = approval_id.strip().upper()
                if req_aid not in chunk.document_id.upper() and req_aid not in chunk.text.upper():
                    continue

            results.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    document_title=chunk.document_title,
                    section=chunk.section,
                    source_name=chunk.source_name,
                    source_url=chunk.source_url,
                    authority=chunk.authority,
                    jurisdiction=chunk.jurisdiction,
                    is_official=chunk.is_official,
                    text=chunk.text,
                    relevance_score=round(score, 4),
                )
            )

            if len(results) >= top_k:
                break

        return results

"""
Regulatory RAG Package for Business Compliance Hub

Provides grounded statutory document ingestion, vector retrieval, and citation-backed
explanation generation.
"""

from ai.rag.models import (
    RegulatoryDocument,
    DocumentChunk,
    RetrievedChunk,
    SourceItem,
    GeneratedAnswer,
    SectionItem,
)
from ai.rag.ingest import RegulatoryDataIngester, compute_content_hash
from ai.rag.chunk import chunk_regulatory_document, chunk_all_documents
from ai.rag.embeddings import (
    EmbeddingProvider,
    TFIDFEmbeddingProvider,
    default_embedding_provider,
)
from ai.rag.retriever import RegulatoryRetriever
from ai.rag.generator import RegulatoryAnswerGenerator
from ai.rag.pipeline import RegulatoryRAGPipeline, rag_pipeline

__all__ = [
    "RegulatoryDocument",
    "DocumentChunk",
    "RetrievedChunk",
    "SourceItem",
    "GeneratedAnswer",
    "SectionItem",
    "RegulatoryDataIngester",
    "compute_content_hash",
    "chunk_regulatory_document",
    "chunk_all_documents",
    "EmbeddingProvider",
    "TFIDFEmbeddingProvider",
    "default_embedding_provider",
    "RegulatoryRetriever",
    "RegulatoryAnswerGenerator",
    "RegulatoryRAGPipeline",
    "rag_pipeline",
]

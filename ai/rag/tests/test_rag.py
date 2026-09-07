"""
Comprehensive Unit Tests for Regulatory RAG System

Covers ingestion of multi-format documents, duplicate detection, chunking stability,
vector similarity, metadata preservation, citation grounding, empty/no-evidence safety,
and the Rule Engine integration bridge.
"""

import pytest
from ai.rag.models import (
    RegulatoryDocument,
    SectionItem,
    GeneratedAnswer,
)
from ai.rag.ingest import RegulatoryDataIngester, compute_content_hash
from ai.rag.chunk import chunk_regulatory_document, chunk_all_documents
from ai.rag.embeddings import TFIDFEmbeddingProvider
from ai.rag.retriever import RegulatoryRetriever
from ai.rag.generator import RegulatoryAnswerGenerator
from ai.rag.pipeline import RegulatoryRAGPipeline
from ai.rules.models import BusinessProfile


@pytest.fixture
def pipeline():
    """Fixture returning a fresh RegulatoryRAGPipeline."""
    return RegulatoryRAGPipeline()


# =====================================================================
# TEST 1: Multi-Format Document Ingestion (.json, .md, .txt, .csv)
# =====================================================================
def test_document_ingestion():
    ingester = RegulatoryDataIngester()
    docs = ingester.ingest_all()

    assert len(docs) >= 15
    for doc in docs:
        assert doc.document_id
        assert doc.title
        assert doc.authority
        assert doc.source_url.startswith("http")
        assert doc.content_hash
        assert len(doc.content_hash) == 64  # Valid SHA-256


# =====================================================================
# TEST 2: Duplicate Document Detection via Content Hash
# =====================================================================
def test_duplicate_detection():
    ingester = RegulatoryDataIngester()
    docs1 = ingester.load_regulations()
    # Loading again with same instance should skip duplicates
    docs2 = ingester.load_regulations()
    assert len(docs2) == 0


# =====================================================================
# TEST 3: Chunk Generation Integrity
# =====================================================================
def test_chunk_generation():
    doc = RegulatoryDocument(
        document_id="TEST_ACT_001",
        title="Test Environmental Safety Act",
        source_name="Gov Portal",
        source_url="https://example.gov.in",
        authority="Pollution Board",
        jurisdiction="Uttar Pradesh",
        retrieved_at="2026-09-04T00:00:00Z",
        last_verified_at="2026-09-04T00:00:00Z",
        content_hash=compute_content_hash("test"),
        sections=[
            SectionItem(section_number="Section 1", title="Scope", text="Applies to all factories."),
            SectionItem(section_number="Section 2", title="Penalties", text="Violations result in fines."),
        ]
    )

    chunks = chunk_regulatory_document(doc)
    assert len(chunks) == 2
    assert chunks[0].section == "Section 1"
    assert chunks[1].section == "Section 2"


# =====================================================================
# TEST 4: Stable Chunk IDs ({document_id}_{chunk_order:04d})
# =====================================================================
def test_stable_chunk_ids():
    doc = RegulatoryDocument(
        document_id="UP_PCB_WATER_ACT_001",
        title="Water Act",
        source_name="UPPCB",
        source_url="https://niveshmitra.up.nic.in",
        authority="UPPCB",
        jurisdiction="Uttar Pradesh",
        retrieved_at="2026-09-04T00:00:00Z",
        last_verified_at="2026-09-04T00:00:00Z",
        content_hash=compute_content_hash("sample"),
        sections=[
            SectionItem(section_number="Section 25", title="CTE", text="Consent required."),
            SectionItem(section_number="Section 26", title="CTO", text="Operation consent required."),
        ]
    )
    chunks = chunk_regulatory_document(doc)
    assert chunks[0].chunk_id == "UP_PCB_WATER_ACT_001_0001"
    assert chunks[1].chunk_id == "UP_PCB_WATER_ACT_001_0002"


# =====================================================================
# TEST 5: Metadata Preservation on Chunks
# =====================================================================
def test_metadata_preservation():
    ingester = RegulatoryDataIngester()
    docs = ingester.ingest_all()
    chunks = chunk_all_documents(docs)

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.document_id
        assert chunk.source_url.startswith("http")
        assert chunk.authority
        assert chunk.jurisdiction
        assert chunk.chunk_order >= 1


# =====================================================================
# TEST 6: Retrieval Returns Top-K Results
# =====================================================================
def test_retrieval_returns_top_k(pipeline):
    query = "effluent treatment and industrial emission consent"
    res3 = pipeline.ask(query=query, top_k=3)
    assert len(res3["sources"]) <= 3

    res1 = pipeline.ask(query=query, top_k=1)
    assert len(res1["sources"]) == 1


# =====================================================================
# TEST 7: Retrieval Preserves Official Source URLs
# =====================================================================
def test_retrieval_preserves_source_url(pipeline):
    result = pipeline.ask("Water pollution consent to establish", top_k=2)
    assert result["evidence_found"] is True
    for source in result["sources"]:
        assert source["source_url"].startswith("http")
        assert len(source["section"]) > 0


# =====================================================================
# TEST 8: Empty Query Handling (Safe Execution)
# =====================================================================
def test_empty_query_handling(pipeline):
    result = pipeline.ask("")
    assert result["evidence_found"] is False
    assert "INSUFFICIENT_EVIDENCE" in result["answer"]
    assert result["confidence"] == 0.0


# =====================================================================
# TEST 9: No Evidence Handling (Zero Hallucination)
# =====================================================================
def test_no_evidence_handling(pipeline):
    result = pipeline.ask("completely fictitious Martian quantum interstellar trade agreement", min_score=0.40)
    assert result["evidence_found"] is False
    assert "INSUFFICIENT_EVIDENCE" in result["answer"]
    assert len(result["sources"]) == 0
    assert result["requires_verification"] is True


# =====================================================================
# TEST 10: Deterministic Retrieval (Repeatability Guarantee)
# =====================================================================
def test_deterministic_retrieval(pipeline):
    query = "boiler inspection and hydraulic testing certificate pressure"
    res1 = pipeline.ask(query, top_k=3)
    res2 = pipeline.ask(query, top_k=3)

    assert res1["confidence"] == res2["confidence"]
    assert len(res1["sources"]) == len(res2["sources"])
    for s1, s2 in zip(res1["sources"], res2["sources"]):
        assert s1["document_id"] == s2["document_id"]
        assert s1["relevance_score"] == s2["relevance_score"]
        assert s1["section"] == s2["section"]


# =====================================================================
# TEST 11: Source Citation Preservation
# =====================================================================
def test_source_citation_preservation(pipeline):
    res = pipeline.ask("food processing business fssai license potable water test", top_k=2)
    assert res["evidence_found"] is True
    assert len(res["sources"]) > 0
    assert any("FSSAI" in s["title"] or "Food" in s["title"] for s in res["sources"])


# =====================================================================
# TEST 12: Synthetic Document Labelling Verification
# =====================================================================
def test_synthetic_document_labelling():
    ingester = RegulatoryDataIngester()
    docs = ingester.ingest_all()
    # Check that demo documents carry explicit disclaimers
    demo_docs = [d for d in docs if not d.is_official]
    assert len(demo_docs) > 0
    for d in demo_docs:
        assert "DEMO" in d.disclaimer or "SYNTHETIC" in d.disclaimer


# =====================================================================
# TEST 13: Rule Engine Approval -> RAG Query Bridge
# =====================================================================
def test_rule_engine_rag_bridge(pipeline):
    profile = BusinessProfile(
        state="Uttar Pradesh",
        sector="Food Processing",
        investment=50000000.0,
        employees=80,
        project_stage="Pre-Operation",
        connected_load_kw=75.0,
        has_boiler=True,
        boiler_pressure=2.0,
        uses_water=True,
        generates_effluent=True,
        food_business=True,
    )

    res = pipeline.explain_approval(
        approval_name="Consent to Operate (CTO)",
        approval_id="UP_PCB_CTO_002",
        business_profile=profile
    )

    assert res["evidence_found"] is True
    assert len(res["sources"]) > 0
    assert any("UP_PCB_CTO_002" in s["document_id"] or "Water" in s["title"] for s in res["sources"])

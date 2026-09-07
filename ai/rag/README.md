# Regulatory RAG (Retrieval-Augmented Generation) System

## Project
**Business Compliance Hub**  
*Unified Intelligent Single-Window Clearance & Compliance Automation (SIH Problem Statement 130)*  
**Domain**: AI/ML + Regulatory Intelligence (Step 3)

---

> [!IMPORTANT]
> **Statutory Disclaimer**:
> The Regulatory RAG System is an informational decision-support tool. It retrieves authorized legal text and generates grounded explanations with source provenance, but does not replace formal determination by the respective government department or legal counsel.

---

## 1. System Architecture

```
Official / Authorized Documents (.json, .md, .txt, .csv)
        ↓
Document Ingestion (ai/rag/ingest.py)
        ↓
Text Chunking (ai/rag/chunk.py)
        ↓
Embeddings (ai/rag/embeddings.py)
        ↓
Retriever (ai/rag/retriever.py)
        ↓
Relevant Evidence
        ↓
Answer Generator (ai/rag/generator.py)
        ↓
Answer + Sources + Verification Notice
```

### End-to-End System Separation
```
                  BUSINESS PROFILE
                         │
                         ▼
                ┌─────────────────┐
                │ DETERMINISTIC   │
                │ RULE ENGINE     │
                └────────┬────────┘
                         │
                         ▼
                POTENTIALLY
                APPLICABLE
                  APPROVAL
                         │
                         ▼
                ┌─────────────────┐
                │      RAG        │
                └────────┬────────┘
                         │
                  Retrieve Evidence
                         │
                         ▼
                ┌─────────────────┐
                │ SOURCE-GROUNDED │
                │   GENERATOR     │
                └────────┬────────┘
                         │
                         ▼
                 EXPLANATION
                    + SOURCES
                    + VERIFY
```

---

## 2. Why RAG is Separate from the Rule Engine

1. **Deterministic Applicability**: The **Rule Engine** (`ai/rules/`) evaluates rigid statutory criteria (workforce count, electrical load, boiler pressure) using deterministic Python logic. An LLM or vector search must **never** be allowed to override or guess legal thresholds.
2. **Context & Evidence Retrieval**: The **RAG System** (`ai/rag/`) takes applicable approvals or user questions and retrieves verbatim statutory clauses and citations from authorized documents.
3. **Auditability**: Every generated answer must cite specific section numbers, issuing authorities, and official URLs.
4. **Zero Hallucination**: If no verified context matches, the system returns `INSUFFICIENT_EVIDENCE` rather than fabricating laws.

---

## 3. Core Modules

| Module | Purpose |
| :--- | :--- |
| [`models.py`](file:///Users/farhan/Desktop/SIH/ai/rag/models.py) | Strongly typed Pydantic models (`RegulatoryDocument`, `DocumentChunk`, `RetrievedChunk`, `SourceItem`, `GeneratedAnswer`). |
| [`ingest.py`](file:///Users/farhan/Desktop/SIH/ai/rag/ingest.py) | Discovers and normalizes multi-format files (`.json`, `.md`, `.txt`, `.csv`), computes SHA-256 content hashes, and detects duplicate documents. |
| [`chunk.py`](file:///Users/farhan/Desktop/SIH/ai/rag/chunk.py) | Preserves statutory hierarchy (Sections, Rules, Schedules) and formats stable chunk IDs (`{document_id}_{chunk_order:04d}`). |
| [`embeddings.py`](file:///Users/farhan/Desktop/SIH/ai/rag/embeddings.py) | `EmbeddingProvider` interface with deterministic, offline `TFIDFEmbeddingProvider` fallback (zero API keys required). |
| [`retriever.py`](file:///Users/farhan/Desktop/SIH/ai/rag/retriever.py) | Hybrid vector similarity + keyword retrieval with jurisdiction, authority, and approval ID filtering. |
| [`generator.py`](file:///Users/farhan/Desktop/SIH/ai/rag/generator.py) | Synthesizes grounded explanations with structured citations and handles `INSUFFICIENT_EVIDENCE` states. |
| [`pipeline.py`](file:///Users/farhan/Desktop/SIH/ai/rag/pipeline.py) | Unified `RegulatoryRAGPipeline` exposing `.ask()` and the `.explain_approval()` bridge for Rule Engine integration. |

---

## 4. Document Provenance & Synthetic Disclaimer

- **Official vs. Demo Flag**: Every document carries `is_official: bool`.
- **Prototype Demonstration Text**: Sample texts in [`ai/regulatory_data/regulations/`](file:///Users/farhan/Desktop/SIH/ai/regulatory_data/regulations/) are labeled:
  `"DEMO / SYNTHETIC — NOT OFFICIAL REGULATORY TEXT (Curated for SIH 2026 Prototype)"`.
- **Prohibition on Scraping**: The system does NOT scrape NSWS, private portal APIs, or user accounts.

---

## 5. Verification Commands

### Run Step 3 Unit Tests (13 Tests)
```bash
pytest ai/rag/tests/ -v
```

### Run Combined AI Test Suite (Rule Engine + RAG: 25 Tests)
```bash
pytest ai/rules/tests/ ai/rag/tests/ -v
```

### Run RAG CLI Demo
```bash
python3 ai/rag/demo.py
```

### Run Dataset Validator
```bash
python3 ai/regulatory_data/validate_dataset.py
```

---

## 6. Future Extensions
1. **pgvector Storage**: In Step 5, replace the local in-memory index with PostgreSQL `pgvector` tables.
2. **Dense Embeddings**: Plug in local `SentenceTransformers` (`all-MiniLM-L6-v2`) via the `EmbeddingProvider` interface.
3. **FastAPI Endpoints**: Expose `POST /api/v1/compliance/rag/query` and `POST /api/v1/compliance/rag/explain-approval`.

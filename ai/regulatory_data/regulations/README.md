# Authorized Regulatory Document Repository

## Overview
This directory (`ai/regulatory_data/regulations/`) contains the local regulatory document collection used by the **Regulatory RAG System** in the **Business Compliance Hub** (*SIH Problem Statement 130*).

---

## 1. Document Classification Policy

Every document ingested by the RAG system is explicitly tagged with `is_official: bool`:

| Classification | Meaning | Labeling Requirement |
| :--- | :--- | :--- |
| **OFFICIAL DOCUMENT** (`is_official: true`) | Verbatim statutory text extracted from official government gazettes, Acts, or departmental notifications. | Verified source URL and gazette reference mandatory. |
| **DEMO / SYNTHETIC DOCUMENT** (`is_official: false`) | Curated sample excerpts or synthesized statutory summaries created for the **SIH 2026 prototype demonstration**. | **MUST** contain header: `"DEMO / SYNTHETIC — NOT OFFICIAL REGULATORY TEXT"`. |

---

## 2. Supported File Formats

The ingestion engine ([`ai/rag/ingest.py`](file:///Users/farhan/Desktop/SIH/ai/rag/ingest.py)) natively discovers and parses:
- **`.json`**: Structured documents containing explicit metadata headers and section arrays.
- **`.md`**: Markdown documents with frontmatter or statutory heading structure (`# Title`, `## Section X`).
- **`.txt`**: Plain text files with standardized statutory headers.

---

## 3. Adding New Official Regulations

To add an official government Act or notification:
1. Save the file in this directory with a descriptive name (e.g. `air_act_1981.md`).
2. Provide statutory provenance metadata in the header or companion JSON:
   - `document_id`: Unique identifier (e.g. `UP_PCB_AIR_ACT_1981`)
   - `title`: Official statutory title
   - `authority`: Regulatory department / board
   - `jurisdiction`: State (`Uttar Pradesh`) or `Central`
   - `document_type`: `Act`, `Rule`, `Notification`, or `Citizen Charter`
   - `source_name`: Government portal / gazette source
   - `source_url`: Verifiable public URL
   - `is_official`: `true` (if official gazette) or `false` (if prototype demo)

---

> [!CAUTION]
> **Scraping Prohibition**:
> Automated scraping of NSWS, private portal APIs, or user-authenticated government portals is strictly prohibited. All documents must be authorized, locally managed files.

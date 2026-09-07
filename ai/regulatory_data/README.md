# Regulatory Dataset

## Project
**Business Compliance Hub**  
*Unified Intelligent Single-Window Clearance & Compliance Automation (SIH Problem Statement 130)*

---

## 1. Purpose

This dataset serves as the core **regulatory knowledge foundation** for the Business Compliance Hub. It defines a standardized, tabular catalog of statutory clearances, industrial licenses, No Objection Certificates (NOCs), registrations, and utility clearances across central and state jurisdictions.

This structured data layer is designed to:
- Feed the **Deterministic Rule Engine** (`ai/rules/`) for calculating dynamic applicant checklists based on enterprise sector, investment scale, and worker count.
- Supply statutory metadata and citations for the **RAG Knowledge Base** (`ai/rag/`) to answer compliance inquiries with legal fidelity.
- Normalize heterogeneous state single-window data (e.g. UP Nivesh Mitra, NSWS) into relational database entities (`approvals`, `approval_requirements`, `departments`).

---

## 2. Dataset Schema & Column Definitions

The `approvals.csv` dataset adheres to the following 19 columns:

| Column Name | Type | Description | Mandatory | Example |
| :--- | :--- | :--- | :--- | :--- |
| `approval_id` | String | Unique statutory clearance identifier | **Yes** | `UP_PCB_CTE_001` |
| `approval_name` | String | Official nomenclature of the consent / NOC / license | **Yes** | `Consent to Establish (CTE)` |
| `authority` | String | Department or statutory regulatory body issuing the clearance | **Yes** | `Uttar Pradesh Pollution Control Board` |
| `state` | String | Jurisdiction state or Central | **Yes** | `Uttar Pradesh` |
| `sector` | String | Primary applicable industry sector | **Yes** | `Manufacturing`, `Food Processing` |
| `stage` | String | Stage of enterprise setup (`Pre-Establishment`, `Pre-Operation`, `Post-Operation`) | **Yes** | `Pre-Establishment` |
| `description` | String | Functional summary of statutory requirement and scope | **Yes** | *Text description* |
| `who_can_apply` | String | Enterprise eligibility parameters and trigger thresholds | **Yes** | *Thresholds / criteria* |
| `documents` | String | Semicolon-delimited list of mandatory application attachments | No | `Site Plan; DPR; Land Deed` |
| `fee` | String | Statutory application fee structure (left blank if tiered/variable) | No | `₹5,000` or blank |
| `validity` | String | Statutory validity duration of granted certificate | No | `5 Years`, `1 Year` |
| `processing_days` | Integer | Statutory SLA timeline under Citizen's Charter / Single Window Act | No | `30`, `15` |
| `act_rules` | String | Governing Act, rules, and specific section clauses | **Yes** | `Water Act 1974 Sec 25/26` |
| `conditions` | String | Key statutory prerequisites and operational conditions | No | *Conditions text* |
| `nsws_available` | String | Whether available on National Single Window System (`Yes`/`No`) | **Yes** | `Yes` |
| `source_name` | String | Name of the official government authority or portal cited | **Yes** | `UPPCB / Nivesh Mitra` |
| `source_url` | String | Publicly verifiable official URL for the clearance | **Yes** | `https://niveshmitra.up.nic.in` |
| `retrieved_at` | String | ISO-8601 timestamp when data was gathered | **Yes** | `2026-09-04T00:00:00Z` |
| `last_verified_at` | String | ISO-8601 timestamp when data was cross-checked | **Yes** | `2026-09-04T00:00:00Z` |

---

## 3. Data Integrity & Verification Policy

> [!IMPORTANT]
> **Prototype Demonstration Disclaimer**:
> Records in this repository are curated specifically for the **Smart India Hackathon (SIH 2026) prototype demonstration** covering **Uttar Pradesh**, **Manufacturing**, and **Food Processing** sectors.
> 
> - **Never represent demo records as officially certified live government records without independent verification.**
> - **Source URLs and verification timestamps are mandatory** for every record.
> - **Tiered and variable fees / timelines**: If exact statutory fee amounts depend on sliding-scale capital investment matrices and cannot be verified with a static figure, the `fee` field is **intentionally left blank** rather than inventing numbers.

---

## 4. Recommended Data Lifecycle

```
Official Public Source (NSWS / UP Nivesh Mitra / Acts & Gazettes)
                       │
                       ▼
          Manual / Authorized Collection
                       │
                       ▼
          CSV Normalization (approvals.csv)
                       │
                       ▼
       Automated Validation (validate_dataset.py)
                       │
                       ▼
       PostgreSQL / pgvector Storage Layer
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
Deterministic Rule Engine      RAG Embeddings & LLM
(ai/rules/rule_engine.py)     (ai/rag/retrieval_engine.py)
```

---

## 5. How to Validate Locally

Run the validator script from the repository root:

```bash
# Using Python
python3 ai/regulatory_data/validate_dataset.py

# Or using the backend virtual environment
backend/.venv/bin/python ai/regulatory_data/validate_dataset.py
```

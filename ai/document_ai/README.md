# Document AI & Pre-Validation Subsystem

## Project
**Business Compliance Hub**  
*Unified Intelligent Single-Window Clearance & Compliance Automation (SIH Problem Statement 130)*  
**Domain**: AI/ML + Regulatory Intelligence (Step 5)

---

> [!IMPORTANT]
> **Statutory & Privacy Disclaimer**:
> - **Zero Legal Determination**: Document AI is an automated **consistency and completeness support tool**. It does not make legal determinations or decide whether a submission is legally sufficient. Final administrative approval rests solely with statutory government officers.
> - **100% Local Processing & PII Protection**: Document parsing is executed entirely locally. No documents are transmitted to cloud OCR services or external third-party APIs (OpenAI, Google, AWS, Azure). Sensitive identifiers (Aadhaar, PAN, Bank Accounts, Passwords) are redacted before storage or auditing.

---

## 1. System Architecture & Boundaries

```
                  BUSINESS PROFILE
                         │
                         ▼
                ┌─────────────────┐
                │   RULE ENGINE   │ (ai/rules/)
                └────────┬────────┘
                         │ (Determines Required Document Checklist)
                         ▼
                ┌─────────────────┐
                │ DOCUMENT UPLOAD │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  DOCUMENT AI    │ (ai/document_ai/)
                └────────┬────────┘
                         │
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
      Extraction     Validation    Completeness
     (extractor.py) (validator.py) (pipeline.py)
           │             │             │
           └─────────────┼─────────────┘
                         ▼
                 DOCUMENT RESULT
                         │
               ┌─────────┼─────────┐
               ▼         ▼         ▼
             VALID     WARNING   INVALID
                         │
                         ▼
              Human / Officer Review
```

---

## 2. Core Modules

| Module | Purpose |
| :--- | :--- |
| [`models.py`](file:///Users/farhan/Desktop/SIH/ai/document_ai/models.py) | Strongly typed Pydantic schemas (`DocumentInput`, `ExtractedDocument`, `DocumentValidationResult`, `CompletenessReport`). |
| [`pii_redactor.py`](file:///Users/farhan/Desktop/SIH/ai/document_ai/pii_redactor.py) | Regex-based sanitization masking Aadhaar (`XXXX-XXXX-1234`), PAN (`XXXXX1234X`), bank accounts, and passwords. |
| [`extractor.py`](file:///Users/farhan/Desktop/SIH/ai/document_ai/extractor.py) | Local file reader with 10MB memory guards, regex metadata extraction, and safe handlers for unsupported formats. |
| [`entity_matcher.py`](file:///Users/farhan/Desktop/SIH/ai/document_ai/entity_matcher.py) | Canonical corporate suffix normalization (`Pvt Ltd` $\leftrightarrow$ `Private Limited`, `LLP`, `Inc`) and token overlap matching. |
| [`expiry_checker.py`](file:///Users/farhan/Desktop/SIH/ai/document_ai/expiry_checker.py) | Calendar date comparison computing days until expiry and flagging expired or soon-expiring certificates. |
| [`validator.py`](file:///Users/farhan/Desktop/SIH/ai/document_ai/validator.py) | Rule-based document validator and checklist completeness engine. |
| [`pipeline.py`](file:///Users/farhan/Desktop/SIH/ai/document_ai/pipeline.py) | Unified `DocumentAIPipeline` coordinating single, batch, and application-level audits. |
| [`demo.py`](file:///Users/farhan/Desktop/SIH/ai/document_ai/demo.py) | Interactive CLI demonstration script. |

---

## 3. Supported Formats & Safe Degradation

- **Natively Supported**: `.txt`, `.md`, `.csv`, `.json`.
- **PDF Handling**: If local PDF libraries (e.g. `pypdf`/`pymupdf`) are not installed, the engine gracefully returns `PDF_EXTRACTION_NOT_AVAILABLE` without crashing.
- **Image / OCR Handling**: If local OCR (e.g. Tesseract) is not installed, the engine gracefully returns `OCR_NOT_AVAILABLE` without crashing.

---

## 4. Pre-Validation Status Categories

> [!IMPORTANT]
> **Data Quality / Pre-Screening Findings Only**: Document AI never labels a document "legally invalid". Findings such as expiration, entity name divergence, or category discrepancies are pre-validation alerts that route to statutory officer verification.

| Status | Meaning |
| :--- | :--- |
| **`VALID`** | Document text was parsed, entity name matches applicant profile, certificate is within validity period, and category aligns with requirements. |
| **`WARNING`** | Document is readable but has non-blocking advisory flags (e.g. expiring within 30 days, minor corporate suffix variation, or missing registration number). |
| **`REQUIRES_HUMAN_VERIFICATION`** | Pre-validation finding detected (e.g. certificate expiration, enterprise name divergence, or document category discrepancy) requiring administrative inspection by a statutory officer. |
| **`INCOMPLETE`** | Mandatory checklist documents are missing from the application submission package. |
| **`UNREADABLE`** | File is corrupted, empty (0 bytes), exceeds memory safety limit (>10MB), or uses an unsupported file format. |

### Individual Sub-Check Dimensions

- **`entity_match`**: `EXACT_MATCH` / `LIKELY_MATCH` / `NO_MATCH` / `UNKNOWN`
- **`expiry_status`**: `VALID` / `EXPIRING_SOON` / `EXPIRED` / `NO_EXPIRY_INFORMATION`
- **`type_match`**: `MATCH` / `LIKELY_MATCH` / `MISMATCH` / `UNKNOWN`

---

## 5. How to Run & Verify

### Run Document AI Unit Tests (10 Tests)
```bash
pytest ai/document_ai/tests/ -v
```

### Run Full AI & ML Test Suite (Rule Engine + RAG + ML + Document AI: 49 Tests)
```bash
pytest ai/rules/tests/ ai/rag/tests/ ml/tests/ ai/document_ai/tests/ -v
```

### Run Document AI CLI Demo
```bash
python3 ai/document_ai/demo.py
```

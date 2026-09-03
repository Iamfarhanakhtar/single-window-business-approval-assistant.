# Team Responsibilities & Handover Guide - SIH PS-130

---

## 👥 Developer 1: AI/ML + Regulatory Intelligence

### Focus Directory:
- `ai/` (`rag/`, `regulatory_data/`, `rules/`, `document_ai/`, `services/`)
- `ml/` (`data/`, `training/`, `models/`, `evaluation/`, `inference/`)

### Key Deliverables & Immediate Next Steps:
1. **Regulatory Knowledge Base & RAG (`ai/rag/`)**:
   - Ingest central & state regulatory acts (Water Act 1974, Air Act 1981, Factories Act 1948, UP Single Window Act 2018).
   - Implement vector embedding pipeline and retrieval engine connecting with pgvector.
2. **Deterministic Rule Matrix (`ai/rules/rule_engine.py`)**:
   - Expand the business parameters evaluation matrix (industry classification into Red/Orange/Green/White categories, investment thresholds, worker count).
3. **ML Delay & Bottleneck Prediction (`ml/training/`)**:
   - Train Scikit-learn classification & regression models using synthetic dataset (`ml/data/synthetic_training_data.csv`).
   - Implement predictor inference classes implementing `MLPredictorInterface`.
4. **Document AI Pre-Validation (`ai/document_ai/`)**:
   - Implement OCR / Layout analysis to detect signatures, certificate dates, and structural blueprint schemas.

---

## 👥 Developer 2: Backend + Database + Workflow

### Focus Directory:
- `backend/app/` (`api/`, `models/`, `schemas/`, `services/`, `workflow/`, `auth/`, `database/`)

### Key Deliverables & Immediate Next Steps:
1. **Business Logic & Workflow Engine (`backend/app/workflow/`)**:
   - Wire up dynamic transition triggers when department officers approve/reject sub-approvals.
   - Implement automated SLA breach countdown alerts.
2. **Document Upload & Storage (`backend/app/services/document_service.py`)**:
   - Finalize file upload handlers, hash-based deduplication, and reusable credential vaults.
3. **Inspection Scheduling & Query Workflow (`backend/app/api/v1/inspections.py`, `queries.py`)**:
   - Implement joint multi-department slot booking algorithms and query response resubmission hooks.
4. **PostgreSQL / pgvector Integration**:
   - Run Alembic migrations and verify seamless deployment on Docker container.

---

## 👥 Developer 3: Frontend + UI/UX + Dashboards

### Focus Directory:
- `frontend/` (`app/`, `components/`, `services/`, `types/`, `lib/`)

### Key Deliverables & Immediate Next Steps:
1. **Application Creation Wizard (`frontend/app/(entrepreneur)/applications/new/`)**:
   - Multi-step application submission wizard integrating `aiService.analyzeBusiness()` to dynamically render custom document upload checklists.
2. **Interactive Approval Roadmap (`frontend/app/(entrepreneur)/approvals/`)**:
   - Visual interactive Gantt / dependency graph of parallel departmental clearances.
3. **Department Scrutiny & Inspection Modals (`frontend/app/(government)/government/`)**:
   - Interactive review drawer for department officers to raise deficiency queries and schedule joint site inspection slots.
4. **AI Regulatory Assistant Widget (`frontend/app/(entrepreneur)/assistant/`)**:
   - Real-time streaming chat interface with citation chips for regulatory clauses.

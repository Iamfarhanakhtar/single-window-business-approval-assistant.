# System Architecture - SIH Problem Statement 130
## Unified Intelligent Approval and Compliance Management Solution

---

### 1. Architectural Overview

The platform uses a layered, contract-driven architecture designed to support a 3-member developer team working independently. It cleanly separates:
1. **Deterministic Rule Engines & Workflow Orchestration** (Backend & State Machine)
2. **Predictive Analytics & Document Intelligence** (AI/ML Services)
3. **Statutory Knowledge Retrieval** (RAG + Acts KB)
4. **Accessible Gov-Tech User Experience** (Next.js App Router + Design System)

```
+-----------------------------------------------------------------------------------+
|                               Next.js Frontend                                    |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  | Entrepreneur Portal|  | Government Oversight |  | System Admin / Regulations|  |
|  +--------------------+  +----------------------+  +---------------------------+  |
+-----------------------------------------|-----------------------------------------+
                                          | REST API (JSON / JWT Bearer)
+-----------------------------------------v-----------------------------------------+
|                               FastAPI Backend                                     |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  |  Auth & RBAC Core  |  | Workflow State Mach. |  |   SLA & Inspection Engine |  |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  | Document Vault Svc |  |  Application Router  |  |  Audit Log & Analytics    |  |
|  +--------------------+  +----------------------+  +---------------------------+  |
+-------------------|---------------------------------------------|-----------------+
                    |                                             |
     SQLAlchemy 2.0 |                              Contract Call  | (Pydantic DTOs)
+-------------------v-------------------+       +-----------------v-----------------+
|      PostgreSQL / pgvector / SQLite   |       |           AI / ML Subsystem       |
|  17 Relational Entities:              |       |  +-----------------------------+  |
|  - Users & Roles                      |       |  | RAG Regulatory Engine (Acts)|  |
|  - Businesses & Profiles              |       |  +-----------------------------+  |
|  - Departments & Approvals            |       |  | Deterministic Rule Matrix   |  |
|  - Applications & Approvals           |       |  +-----------------------------+  |
|  - Documents & Validations            |       |  | Document AI & OCR Matcher   |  |
|  - Inspections & Reports              |       |  +-----------------------------+  |
|  - Queries, SLA, Renewals, Incentives |       |  | ML Bottleneck / Delay Model |  |
+---------------------------------------+       +-----------------------------------+
```

---

### 2. Application Lifecycle State Machine

Applications transition through 12 deterministic statutory states:

```
[DRAFT]
   │
   ▼
[DOCUMENT_CHECK] ──(Validation Failed)──► [DRAFT]
   │
   ▼
[READY_FOR_SUBMISSION]
   │
   ▼
[SUBMITTED]
   │
   ▼
[UNDER_REVIEW] ◄────────────────────────────────────────┐
   │                                                    │
   ├──► [INSPECTION_REQUIRED]                           │
   │        │                                           │
   │        ▼                                           │
   │    [INSPECTION_SCHEDULED]                          │
   │        │                                           │
   │        ▼                                           │
   │    [INSPECTION_COMPLETED] ──► [UNDER_REVIEW]       │
   │                                                    │
   ├──► [QUERY_RAISED]                                  │
   │        │                                           │
   │        ▼                                           │
   │    [RESUBMITTED] ──────────────────────────────────┘
   │
   ├──► [APPROVED] ──► [RENEWAL_MONITORING]
   │
   └──► [REJECTED]
```

---

### 3. Parallel Departmental Approvals Architecture

Multiple clearance agencies process sub-approvals concurrently without blocking other departments:

```
Master Application (APP-2026-UP-0042) [UNDER_REVIEW]
│
├── 1. Fire Safety NOC (FIRE_DEPT) ────────────► [APPROVED] (Cert: UP-FIRE-9812)
├── 2. Pollution Consent CTE (UPPCB) ──────────► [IN_REVIEW] (Joint Inspection in 4 days)
├── 3. FSSAI State Mfg License (FSSAI) ────────► [PENDING]
└── 4. Factory Plan Approval (FACTORIES_DEPT) ──► [IN_REVIEW]
```
The Workflow Engine evaluates all parallel approvals to compute overarching application status and SLA deadlines.

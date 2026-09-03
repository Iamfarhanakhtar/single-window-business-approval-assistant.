# Bharat Compliance Portal (SIH Problem Statement 130)
> **Unified Intelligent Approval and Compliance Management Solution for Industrial Units & Entrepreneurs**

---

## 📌 Problem Statement Overview
Setting up and operating an industrial enterprise requires navigating multiple statutory departments (Pollution Control, Fire Safety, Labor, Factories, Food Safety). Applicants face fragmented portals, repetitive document submissions, lack of statutory timeline visibility, and unexpected deficiency queries.

**Bharat Compliance Portal** solves this through:
- **Intelligent Single-Window Orchestration**: Dynamic approval checklist generator using deterministic rules & RAG.
- **Parallel Departmental Clearances**: Concurrent processing across agencies without blocking independent approvals.
- **Document Vault & AI Pre-Validation**: Reusable credential vault and schema pre-screening to eliminate 85% of query delays.
- **Predictive SLA & Delay Forecasting**: ML inference models forecasting review bottlenecks and tracking statutory countdowns.
- **Synchronized Joint Inspections**: Coordinated site audits preventing repeated departmental visits.

---

## 🏛️ System Architecture

```
sih-problem-130/
├── frontend/             # Next.js 14 (App Router) + Tailwind CSS + Gov-Tech Design System
│   ├── app/              # Role-based routes (Entrepreneur, Government Officer, Admin)
│   ├── components/       # Reusable UI component library & domain widgets
│   ├── services/         # Dedicated API service layer (auth, application, AI, dashboard)
│   └── types/            # Strongly-typed TypeScript data contracts
│
├── backend/              # FastAPI Backend + SQLAlchemy 2.0 ORM + Pydantic v2
│   ├── app/api/v1/       # REST API endpoints (Auth, Approvals, Applications, AI, SLA)
│   ├── app/models/       # 17 Relational database entities
│   ├── app/workflow/     # 12-state deterministic workflow machine & parallel coordinator
│   ├── app/database/     # DB connection & synthetic demo seed script
│   └── tests/            # Automated pytest test suites
│
├── ai/                   # AI & Regulatory Intelligence Subsystem (Developer 1)
│   ├── rag/              # Regulatory knowledge base retrieval engine
│   ├── rules/            # Deterministic statutory rule engine
│   ├── document_ai/      # Document pre-validation & OCR checker
│   └── services/         # AI Service interface contracts & mock test engine
│
├── ml/                   # Machine Learning Subsystem (Developer 1)
│   ├── data/             # Feature definitions & synthetic training data
│   ├── inference/        # Delay & clarification risk prediction interfaces
│   └── training/         # Model training scripts
│
├── docs/                 # Architectural specifications, DB schemas & API contracts
├── docker/               # Dockerfiles & PostgreSQL pgvector init scripts
├── .env.example          # Environment variable template
└── docker-compose.yml    # Multi-container orchestration
```

---

## 👥 3-Developer Task Breakdown

| Developer | Domain | Key Responsibilities |
| :--- | :--- | :--- |
| **Developer 1** | **AI/ML + Regulatory Intelligence** | RAG knowledge base (`ai/rag/`), deterministic compliance rules (`ai/rules/`), ML delay prediction (`ml/`), and Document AI pre-validation (`ai/document_ai/`). |
| **Developer 2** | **Backend + Database + Workflow** | FastAPI endpoints (`backend/app/api/`), 17 SQLAlchemy models, JWT auth & RBAC, parallel state machine (`backend/app/workflow/`), and PostgreSQL/pgvector storage. |
| **Developer 3** | **Frontend + UI/UX + Dashboards** | Next.js App Router (`frontend/app/`), Gov-Tech design system (`frontend/components/ui/`), interactive roadmap, and executive oversight dashboards. |

---

## 🚀 Quick Start & Local Setup

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**
- *(Optional)* Docker & Docker Compose

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend (SQLite database and demo records will auto-seed on startup)
python -m uvicorn app.main:app --port 8000 --reload
```
- Backend API will run at: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/health`

### 3. Frontend Setup
```bash
# In a separate terminal window
cd frontend

# Install Node dependencies
npm install

# Start Next.js development server
npm run dev
```
- Frontend Web App will run at: `http://localhost:3000`

### 4. Running via Docker Compose
```bash
docker-compose up --build
```

---

## 🔑 Pre-Seeded Demonstration Accounts

All accounts use the password: `password123`

| Role | Email | Use Case |
| :--- | :--- | :--- |
| **Entrepreneur** | `entrepreneur@abcfoods.com` | Applicant portal for *ABC Foods Pvt Ltd* (Clearances, uploads, roadmap) |
| **Government Officer** | `collector.ghaziabad@gov.in` | District Magistrate / Nodal Officer executive dashboard & state SLA |
| **Department Officer** | `officer.uppcb@gov.in` | Scrutiny officer reviewing UPPCB Consent to Establish and scheduling visits |
| **System Admin** | `admin@gov.in` | Regulatory rule configuration and department management |

---

## 🧪 Automated Testing
Run backend unit tests verifying database initialization, JWT security, workflow state machine, and AI contracts:
```bash
cd backend
python -m pytest tests/ -v
```

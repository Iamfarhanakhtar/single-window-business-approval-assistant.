# REST API Specification & Service Contracts - SIH PS-130

---

## 1. Authentication Endpoints

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register a new user | Public |
| `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT Bearer token | Public |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | Authenticated |

---

## 2. Business & Profile Endpoints

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/businesses` | List businesses for user or all (Govt) | Authenticated |
| `POST` | `/api/v1/businesses` | Register a new business unit | Entrepreneur |
| `GET` | `/api/v1/businesses/{id}` | Get business details & profile | Authenticated |

---

## 3. Approvals & Department Catalog

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/approvals` | List statutory clearances & fee schedule | Public / Authenticated |
| `GET` | `/api/v1/approvals/departments` | List regulatory departments | Public / Authenticated |
| `GET` | `/api/v1/approvals/{id}` | Get approval requirements & checklist | Public / Authenticated |

---

## 4. Master Applications & Workflow

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/applications` | List applications (filtered by role) | Authenticated |
| `POST` | `/api/v1/applications` | Create master application with selected approvals | Entrepreneur |
| `GET` | `/api/v1/applications/{id}` | Detailed application status & approvals | Authenticated |
| `POST` | `/api/v1/applications/{id}/submit` | Transition application to `SUBMITTED` & start SLA | Entrepreneur |
| `PATCH` | `/api/v1/applications/{id}/status` | Update status (validated against state graph) | Officers / System |

---

## 5. Documents, Inspections & Queries

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/documents` | List uploaded documents | Authenticated |
| `POST` | `/api/v1/documents/upload` | Upload document with AI pre-validation | Authenticated |
| `GET` | `/api/v1/inspections` | List scheduled site visits | Authenticated |
| `POST` | `/api/v1/inspections` | Schedule joint inspection | Department Officer |
| `POST` | `/api/v1/inspections/{id}/report` | Submit site inspection report & findings | Department Officer |
| `GET` | `/api/v1/queries` | List queries on an application | Authenticated |
| `POST` | `/api/v1/queries` | Raise deficiency query | Department Officer |
| `POST` | `/api/v1/queries/{id}/respond` | Respond to query with clarification | Entrepreneur |

---

## 6. AI & Regulatory Intelligence Service Contracts

### `POST /api/v1/ai/analyze-business`
**Request:**
```json
{
  "sector": "Food Processing",
  "location": "Uttar Pradesh",
  "investment": 50000000,
  "employees": 80,
  "business_details": {}
}
```
**Response:**
```json
{
  "applicable_approvals": [
    {
      "code": "FIRE_NOC",
      "name": "Fire Safety NOC (Form-B)",
      "department": "State Fire Prevention Service",
      "category": "Safety",
      "sla_days": 15,
      "fee": 5000.0,
      "mandatory": true,
      "prerequisites": []
    }
  ],
  "required_documents": [
    "Certificate of Incorporation / PAN",
    "Building Layout Plan & Fire Safety Evacuation Map"
  ],
  "risk_score": 0.22,
  "delay_probability": 0.35,
  "predicted_processing_days": 38,
  "eligible_incentives": [
    "UP Industrial Investment & Employment Promotion Policy"
  ],
  "explanation": "..."
}
```

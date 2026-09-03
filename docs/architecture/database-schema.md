# Database Schema Specification - SIH PS-130

The platform defines **17 relational database entities** using SQLAlchemy 2.0 with UUID primary keys and standard foreign keys.

---

### Core Entity Dictionary

| Table Name | Description | Key Relationships |
| :--- | :--- | :--- |
| `roles` | System roles (Entrepreneur, Govt Officer, Dept Officer, Admin) | `users.role_id` |
| `users` | Authenticated users with hashed credentials & assigned department | `businesses`, `notifications`, `audit_logs` |
| `businesses` | Enterprise entities (Pvt Ltd, LLP, Partnership) | `users.id`, `business_profiles`, `applications` |
| `business_profiles` | Sector, location, investment, employee count, technical specs | `businesses.id` |
| `departments` | Statutory bodies (UPPCB, Fire, FSSAI, Factories) | `approvals`, `inspections`, `users` |
| `approvals` | Statutory clearances (FIRE_NOC, PCB_CTE, FSSAI_MFG) | `departments.id`, `approval_requirements` |
| `approval_requirements` | Mandatory documentation checklist per approval | `approvals.id` |
| `regulations` | Statutory clauses and legal provisions with embeddings | `regulatory_sources.id` |
| `regulatory_sources` | Central & State Acts (Factories Act, Water Act) | `regulations` |
| `applications` | Master single-window application with state machine tracking | `businesses.id`, `application_approvals` |
| `application_approvals` | Parallel departmental sub-approval status & SLA dates | `applications.id`, `approvals.id` |
| `documents` | Uploaded blueprints, certificates, and reusable credentials | `businesses.id`, `applications.id` |
| `document_validations` | Pre-validation score, extracted metadata, and OCR issues | `documents.id` |
| `inspections` | Scheduled site inspections and physical audits | `applications.id`, `departments.id` |
| `inspection_reports` | Findings, compliance verdicts, geo-coordinates | `inspections.id` |
| `queries` | Clarifications & deficiency memos raised by scrutiny officers | `applications.id`, `users.id` |
| `sla_records` | Statutory SLA countdown, breach flags, and metrics | `applications.id` |
| `notifications` | In-app alerts for milestone updates & queries | `users.id` |
| `renewals` | License expiration dates and renewal tracking | `businesses.id` |
| `incentives` | State policy subsidies and capital incentive schemes | Sector matching |
| `audit_logs` | Immutable audit trail for all workflow decisions | `users.id` |
| `ml_predictions` | Risk scores, predicted delay days, and feature importance | `applications.id` |

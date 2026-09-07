# Deterministic Regulatory Rule Engine

## Project
**Business Compliance Hub**  
*Unified Intelligent Single-Window Clearance & Compliance Automation (SIH Problem Statement 130)*  
**Domain**: AI/ML + Regulatory Intelligence (Step 2)

---

> [!IMPORTANT]
> **Statutory Disclaimer**:
> The Rule Engine is an **informational decision-support component**. It does not replace legal advice or the formal determination of the relevant government statutory authority.

---

## 1. Purpose & Architecture

The **Deterministic Regulatory Rule Engine** evaluates an enterprise/applicant profile against the statutory approvals catalog ([`ai/regulatory_data/approvals.csv`](file:///Users/farhan/Desktop/SIH/ai/regulatory_data/approvals.csv)) to determine:
1. **Applicable Clearances & Licenses**: Identify which central and state NOCs/consents are relevant.
2. **Transparent Decision Explanations**: Provide explainable statutory reasons for every match or rejection.
3. **Consolidated Document Checklist**: Deduplicate and aggregate required submission documents.
4. **Prerequisite Sequencing**: Topological ordering of dependent clearances (e.g., Consent to Establish $\rightarrow$ Consent to Operate).

### Architectural Boundary
```
┌─────────────────────────────────────────────────────────────┐
│ 1. RULE ENGINE (ai/rules/)                                 │
│    Deterministic applicability, thresholds & dependencies    │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. RAG RETRIEVAL (ai/rag/)                                  │
│    Retrieves verbatim clauses & legal acts for citations    │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. LLM ASSISTANT                                            │
│    Summarizes & explains statutory guidance to applicant    │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. FASTAPI & FRONTEND                                       │
│    REST API endpoints feeding the Single-Window portal      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Why Deterministic (No LLM)?

1. **Zero Hallucination**: Statutory compliance requires 100% reproducibility. An LLM cannot be trusted to calculate rigid legal thresholds (e.g. employee counts, power loads, or boiler steam pressure).
2. **Auditability & Legal Proof**: Every match score and reason can be traced directly to an explicit condition in the statutory act or single-window rules.
3. **High Performance**: Evaluates hundreds of approvals in sub-millisecond execution times without API latency or network costs.

---

## 3. Business Profile Model (`BusinessProfile`)

Input profiles are strongly typed and validated using Pydantic v2. Invalid inputs (such as negative employees or blank sectors) raise clean, informative validation errors.

```python
from ai.rules import BusinessProfile

profile = BusinessProfile(
    state="Uttar Pradesh",
    sector="Food Processing",
    investment=50000000.0,       # ₹5 Crore INR
    employees=80,
    project_stage="Pre-Operation",
    connected_load_kw=75.0,
    has_boiler=True,
    boiler_pressure=2.0,         # kg/cm2
    uses_water=True,
    generates_effluent=True,
    food_business=True
)
```

---

## 4. Matching Logic & Scoring Methodology

Scoring uses a transparent 100-point rubric normalized to `0.0 – 1.0`:

| Criterion | Weight | Evaluation Logic |
| :--- | :--- | :--- |
| **State Match** | **30 pts** | Exact state match (`Uttar Pradesh`) or universal Central/National jurisdiction. Non-matching states receive 0 pts. |
| **Sector Match** | **30 pts** | Exact sector match, general industrial applicability, or sector hierarchy recognition (e.g., *Food Processing* is a subsector of *Manufacturing*). |
| **Stage Match** | **20 pts** | Exact match with current project lifecycle stage (`Pre-Establishment`, `Pre-Operation`). Partial credit given for antecedent stages. |
| **Explicit Condition** | **20 pts** | Trigger evaluations (e.g., connected load $\ge 50$ kW for CEIG, boiler pressure $> 1.0$ kg/cm², workforce $\ge 10$ with power for Factory Act). |

---

## 5. Result Categories (`ApprovalStatus`)

| Status | Interpretation |
| :--- | :--- |
| `POTENTIALLY_APPLICABLE` | Strong deterministic match (Score $\ge 0.70$) meeting state, sector, stage, and statutory threshold conditions. |
| `PARTIALLY_MATCHED` | Important criteria match (Score $0.40 - 0.69$), but certain operational parameters require confirmation. |
| `REQUIRES_VERIFICATION` | The dataset or profile lacks physical site data (e.g. plot tree surveys) to make a definitive determination. |
| `NOT_MATCHED` | The enterprise clearly falls outside the statutory jurisdiction, sector, or technical criteria. |

---

## 6. Document Aggregation & Prerequisite Sequencing

- **Deduplicated Checklist**: Merges identical document requirements across multiple approvals (e.g., Site Plan, DPR, Land Deed) while preserving first-seen order.
- **Topological Sorting**: Uses Kahn's algorithm over `RULE_DEPENDENCIES` to ensure prerequisites (such as CTE before CTO) are sequenced correctly.

---

## 7. How to Run

### Run Unit Tests
```bash
pytest ai/rules/tests/ -v
```

### Run the Interactive CLI Demo
```bash
python3 ai/rules/demo.py
```

### Run Dataset Validation
```bash
python3 ai/regulatory_data/validate_dataset.py
```

---

## 8. Limitations & Future Integration

- **Dataset Scope**: Currently indexed for 10 prototype demo approvals for UP Manufacturing & Food Processing.
- **Future RAG Integration**: In Step 3, matched approvals will pass their `approval_id` and legal citations to the vector retrieval engine to generate context-grounded Q&A.
- **FastAPI Endpoint**: In Step 5, the rule engine will be wired directly into `POST /api/v1/compliance/checklist`.

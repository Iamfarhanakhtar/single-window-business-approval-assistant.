# ML Risk & Delay Prediction Subsystem

## Project
**Business Compliance Hub**  
*Unified Intelligent Single-Window Clearance & Compliance Automation (SIH Problem Statement 130)*  
**Domain**: AI/ML + Regulatory Intelligence (Step 4)

---

> [!CAUTION]
> **Synthetic Prototype Model Disclaimer**:
> Current models are **trained on synthetic/demo data and are intended ONLY for Smart India Hackathon (SIH 2026) prototype demonstration**.
> - **NOT an Official Government Prediction**: Predictions do not constitute legal determinations, official government commitments, or statutory guarantees.
> - **No Government Data Scraped**: No private government portals or NSWS internal APIs were accessed.
> - **Strict Architectural Separation**: The ML model **never** determines which approvals are legally required. Statutory applicability is evaluated deterministically by the **Rule Engine** ([`ai/rules/`](file:///Users/farhan/Desktop/SIH/ai/rules/)).

---

## 1. System Responsibilities & Boundaries

```
                 BUSINESS PROFILE
                        │
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
    RULE ENGINE         ML            RAG
   (ai/rules/)        (ml/)         (ai/rag/)
          │             │             │
          ↓             ↓             ↓
   Which approvals?  Delay/Risk   Why / Evidence
          │             │             │
          └─────────────┼─────────────┘
                        ↓
             COMPLIANCE INSIGHT
                        ↓
             Backend Integration
                        ↓
                  Frontend UI
```

| Subsystem | Responsibility |
| :--- | :--- |
| **Deterministic Rule Engine** (`ai/rules/`) | Evaluates whether a statutory clearance is applicable based on legal rules and thresholds. |
| **Regulatory RAG** (`ai/rag/`) | Retrieves verbatim legal text and provides citation-grounded evidence explaining why a rule applies. |
| **ML Predictive Engine** (`ml/`) | Forecasts estimated processing days, probability of SLA breach, and composite risk factors. |

---

## 2. Synthetic Training Dataset

- **File**: [`ml/data/synthetic_applications.csv`](file:///Users/farhan/Desktop/SIH/ml/data/synthetic_applications.csv)
- **Size**: 1,500 application records
- **Generator**: [`ml/data/generate_data.py`](file:///Users/farhan/Desktop/SIH/ml/data/generate_data.py) with fixed seed (`seed=42`).

### Features & Target Variables

| Feature Type | Attributes |
| :--- | :--- |
| **Numerical Features** | `investment`, `employees`, `approval_count`, `document_count`, `missing_document_count`, `inspection_required`, `department_count`, `previous_queries`, `sla_days` |
| **Categorical Features** | `state`, `sector`, `project_stage`, `applicant_type`, `season` |
| **Target Variable 1 (Regression)** | `actual_processing_days` (Continuous target) |
| **Target Variable 2 (Classification)** | `delayed` (Binary indicator: 1 if actual > SLA, else 0) |

> [!IMPORTANT]
> **Zero Data Leakage**: Target variables (`actual_processing_days` and `delayed`) are strictly excluded from the feature matrix during training and inference.

---

## 3. Machine Learning Models

1. **SLA Delay Classifier** (`RandomForestClassifier`):
   - Predicts binary SLA breach indicator and probability $P(\text{delay})$.
   - Performance on holdout test set: **Accuracy: ~87.7%**, **ROC-AUC: ~93.5%**, **F1-Score: ~0.90**.
2. **Processing Time Regressor** (`RandomForestRegressor`):
   - Predicts estimated processing timeline in days.
   - Performance on holdout test set: **MAE: ~2.69 days**, **$R^2$: ~0.92**.

---

## 4. Transparent Risk Scoring Formula (0–100)

The composite risk score combines model probability with operational friction indicators:

$$\text{Risk Score} = 0.40 \times (P(\text{delay}) \times 100) + 0.20 \times \min\left(100, \frac{\text{missing\_docs}}{3} \times 100\right) + 0.15 \times (\text{inspection} \times 100) + 0.15 \times \min\left(100, \frac{\text{departments}-1}{3} \times 100\right) + 0.10 \times \min\left(100, \frac{\text{queries}}{2} \times 100\right)$$

### Categorical Risk Levels:
- **`LOW`**: Score $< 35$
- **`MEDIUM`**: Score $35 - 64$
- **`HIGH`**: Score $\ge 65$

---

## 5. Future FastAPI Integration Contract

In Step 5, the ML predictor will be wired into:

### `POST /api/v1/ml/predict-risk`

**Request Body:**
```json
{
  "state": "Uttar Pradesh",
  "sector": "Food Processing",
  "investment": 50000000,
  "employees": 80,
  "approval_count": 9,
  "document_count": 43,
  "missing_document_count": 2,
  "inspection_required": true,
  "department_count": 5,
  "previous_queries": 1,
  "project_stage": "Pre-Operation",
  "applicant_type": "Enterprise",
  "season": "Q3",
  "sla_days": 30
}
```

**Response Body:**
```json
{
  "delay_probability": 0.68,
  "predicted_processing_days": 31.4,
  "risk_score": 72,
  "risk_level": "HIGH",
  "risk_factors": [
    "High number of approvals (9 clearances) increases aggregate workflow complexity.",
    "Missing documents detected (2 missing) - increases clarification risk and query rounds.",
    "Mandatory physical on-site inspection required by statutory authorities.",
    "Multiple regulatory departments (5 departments) involved in parallel processing."
  ],
  "model_type": {
    "delay": "RandomForestClassifier",
    "processing_time": "RandomForestRegressor"
  },
  "is_synthetic_model": true
}
```

---

## 6. How to Run & Verify

### Run ML Unit Tests (14 Tests)
```bash
pytest ml/tests/ -v
```

### Run Model Evaluation
```bash
python3 ml/evaluation/evaluate_models.py
```

### Run ML CLI Demo
```bash
python3 ml/demo.py
```

### Run All Project Tests (Rule Engine + RAG + ML: 39 Tests)
```bash
pytest ai/rules/tests/ ai/rag/tests/ ml/tests/ -v
```

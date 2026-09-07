# Synthetic Application Dataset

## Overview
This directory contains the synthetic training dataset used for prototyping the **ML Risk & Delay Prediction Subsystem** for the **Business Compliance Hub** (*SIH Problem Statement 130*).

---

> [!CAUTION]
> **Prototype Data Disclaimer**:
> This dataset is **synthetic/demo data created for SIH prototype development**. It is **not official government historical data and must not be used to make real-world regulatory claims**.
> - No government portals were scraped.
> - No private or authenticated NSWS endpoints were called.
> - Target variables represent mathematical modeling simulations designed to demonstrate system architecture.

---

## 1. Dataset Schema (`synthetic_applications.csv`)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `application_id` | String | Unique synthetic identifier (e.g. `APP_SYN_0001`) |
| `state` | String | Jurisdiction state (`Uttar Pradesh`, `Maharashtra`, `Gujarat`, etc.) |
| `sector` | String | Industrial classification (`Food Processing`, `Manufacturing`, `Textiles`, etc.) |
| `investment` | Float | Capital investment amount in INR |
| `employees` | Integer | Total workforce count |
| `approval_count` | Integer | Number of statutory approvals required |
| `document_count` | Integer | Total required application documents |
| `missing_document_count` | Integer | Deficient/missing application documents |
| `inspection_required` | Integer | Binary flag (1 = on-site inspection required, 0 = document-only) |
| `department_count` | Integer | Number of distinct government departments involved |
| `previous_queries` | Integer | Clarification queries previously raised by officers |
| `project_stage` | String | Lifecycle stage (`Pre-Establishment`, `Pre-Operation`, `Operation`) |
| `applicant_type` | String | Enterprise scale (`MSME`, `Enterprise`, `Individual`) |
| `season` | String | Application filing quarter (`Q1`, `Q2`, `Q3`, `Q4`) |
| `authority` | String | Primary coordinating department |
| `sla_days` | Integer | Statutory Citizen's Charter SLA baseline (days) |
| `actual_processing_days` | Float | **Target Variable 1**: Total days taken for final clearance |
| `delayed` | Integer | **Target Variable 2**: Binary SLA breach indicator (1 if actual > SLA, else 0) |

---

## 2. Reproducibility
The dataset is deterministically generated via [`ml/data/generate_data.py`](file:///Users/farhan/Desktop/SIH/ml/data/generate_data.py) using a fixed seed (`seed=42`).
To regenerate:
```bash
python3 ml/data/generate_data.py
```

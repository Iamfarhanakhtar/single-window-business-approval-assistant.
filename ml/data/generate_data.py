"""
Synthetic Application Dataset Generator

Generates a reproducible, balanced dataset of 1,500 industrial approval applications
for training prototype risk & delay prediction models for SIH Problem Statement 130.
"""

import numpy as np
import pandas as pd
from pathlib import Path


def generate_synthetic_dataset(output_path: str = "ml/data/synthetic_applications.csv", n_rows: int = 1500, seed: int = 42):
    np.random.seed(seed)

    states = ["Uttar Pradesh", "Maharashtra", "Gujarat", "Karnataka", "Tamil Nadu", "Rajasthan"]
    state_probs = [0.45, 0.15, 0.15, 0.10, 0.10, 0.05]

    sectors = ["Food Processing", "Manufacturing", "Textiles", "Chemicals", "Pharmaceuticals", "Information Technology"]
    sector_probs = [0.35, 0.30, 0.10, 0.10, 0.08, 0.07]

    project_stages = ["Pre-Establishment", "Pre-Operation", "Operation"]
    applicant_types = ["MSME", "Enterprise", "Individual"]
    seasons = ["Q1", "Q2", "Q3", "Q4"]
    authorities = ["UPPCB", "UP Fire Service", "Directorate of Factories", "FSSAI", "CEIG", "Legal Metrology", "Boilers Directorate"]

    records = []

    for i in range(1, n_rows + 1):
        app_id = f"APP_SYN_{i:04d}"
        state = np.random.choice(states, p=state_probs)
        sector = np.random.choice(sectors, p=sector_probs)
        stage = np.random.choice(project_stages, p=[0.4, 0.45, 0.15])
        applicant_type = np.random.choice(applicant_types, p=[0.6, 0.3, 0.1])
        season = np.random.choice(seasons)
        authority = np.random.choice(authorities)

        # Numerical attributes
        if applicant_type == "MSME":
            investment = float(np.random.lognormal(mean=15.5, sigma=0.8))  # ~₹10L to ₹20 Cr
            employees = int(np.random.randint(5, 100))
            approval_count = int(np.random.randint(2, 7))
            department_count = int(min(approval_count, np.random.randint(1, 4)))
        elif applicant_type == "Enterprise":
            investment = float(np.random.lognormal(mean=17.5, sigma=0.9))  # ~₹10 Cr to ₹200 Cr
            employees = int(np.random.randint(50, 600))
            approval_count = int(np.random.randint(4, 12))
            department_count = int(min(approval_count, np.random.randint(2, 6)))
        else:
            investment = float(np.random.lognormal(mean=14.0, sigma=0.6))
            employees = int(np.random.randint(1, 20))
            approval_count = int(np.random.randint(1, 3))
            department_count = 1

        # Document parameters
        docs_per_approval = np.random.randint(3, 6)
        document_count = approval_count * docs_per_approval
        
        # Missing docs (correlated with previous queries)
        missing_doc_count = int(np.random.choice([0, 1, 2, 3, 4], p=[0.55, 0.22, 0.13, 0.07, 0.03]))
        missing_doc_count = min(missing_doc_count, document_count)

        inspection_required = int(np.random.choice([0, 1], p=[0.45, 0.55])) if sector in ("Manufacturing", "Food Processing", "Chemicals") else int(np.random.choice([0, 1], p=[0.8, 0.2]))
        previous_queries = int(np.random.choice([0, 1, 2, 3], p=[0.60, 0.22, 0.12, 0.06]))

        # Statutory SLA baseline (days)
        sla_days = int(np.random.choice([15, 20, 30, 45, 60], p=[0.25, 0.30, 0.30, 0.10, 0.05]))

        # Balanced delay multiplier formula centered around 1.0
        base_multiplier = 0.78
        delay_multiplier = (
            base_multiplier
            + (0.14 * missing_doc_count)
            + (0.06 * (department_count - 1))
            + (0.10 * previous_queries)
            + (0.08 if inspection_required == 1 else -0.04)
            + (0.05 if approval_count >= 6 else 0.0)
            + (0.04 if season in ("Q3", "Q4") else -0.02)
            + np.random.normal(loc=0.0, scale=0.10)
        )
        delay_multiplier = max(0.4, delay_multiplier)

        actual_processing_days = round(sla_days * delay_multiplier, 1)
        delayed = 1 if actual_processing_days > sla_days else 0

        records.append({
            "application_id": app_id,
            "state": state,
            "sector": sector,
            "investment": round(investment, 2),
            "employees": employees,
            "approval_count": approval_count,
            "document_count": document_count,
            "missing_document_count": missing_doc_count,
            "inspection_required": inspection_required,
            "department_count": department_count,
            "previous_queries": previous_queries,
            "project_stage": stage,
            "applicant_type": applicant_type,
            "season": season,
            "authority": authority,
            "sla_days": sla_days,
            "actual_processing_days": actual_processing_days,
            "delayed": delayed,
        })

    df = pd.DataFrame(records)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    delayed_count = df['delayed'].sum()
    print(f"[SUCCESS] Generated {len(df)} synthetic records. Delayed: {delayed_count} ({delayed_count/len(df)*100:.1f}%), On-Time: {len(df)-delayed_count} ({(len(df)-delayed_count)/len(df)*100:.1f}%)")
    return df


if __name__ == "__main__":
    generate_synthetic_dataset()

"""
ML Risk & Delay Prediction CLI Demonstration

Demonstrates model inference, estimated processing timeline, probability of SLA breach,
and explainable risk factors for a sample industrial enterprise application.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
curr_path = Path(__file__).resolve().parent
project_root = curr_path.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ml.inference.predictor import ComplianceRiskPredictor


def run_demo():
    print("========================================")
    print("BUSINESS COMPLIANCE HUB")
    print("ML RISK & DELAY PREDICTION")
    print("========================================")
    print()

    sample_application = {
        "state": "Uttar Pradesh",
        "sector": "Food Processing",
        "investment": 50000000.0,
        "employees": 80,
        "approval_count": 9,
        "document_count": 43,
        "missing_document_count": 2,
        "inspection_required": True,
        "department_count": 5,
        "previous_queries": 1,
        "project_stage": "Pre-Operation",
        "applicant_type": "Enterprise",
        "season": "Q3",
        "sla_days": 30,
    }

    predictor = ComplianceRiskPredictor()
    result = predictor.predict(sample_application)

    print("Application Profile:")
    print("--------------------")
    print(f"State: {sample_application['state']}")
    print(f"Sector: {sample_application['sector']}")
    print(f"Investment: ₹5 crore")
    print(f"Employees: {sample_application['employees']}")
    print(f"Approvals: {sample_application['approval_count']}")
    print(f"Documents: {sample_application['document_count']} (Missing: {sample_application['missing_document_count']})")
    print(f"Inspection: {'Yes' if sample_application['inspection_required'] else 'No'}")
    print(f"Departments Involved: {sample_application['department_count']}")
    print(f"Previous Queries: {sample_application['previous_queries']}")
    print(f"Stage: {sample_application['project_stage']}")
    print(f"Statutory Target SLA: {sample_application['sla_days']} days")
    print()

    print("Prediction Results:")
    print("-------------------")
    print(f"Delay Probability:\n{int(result['delay_probability'] * 100)}%\n")
    print(f"Predicted Processing Time:\n{result['predicted_processing_days']} days\n")
    print(f"Risk Score:\n{result['risk_score']} / 100\n")
    print(f"Risk Level:\n{result['risk_level']}\n")

    print("Risk Factors:")
    for factor in result["risk_factors"]:
        print(f"- {factor}")
    print()

    print("IMPORTANT:")
    print("Prediction generated using synthetic/demo training data.")
    print("Not an official government prediction.")
    print("========================================")


if __name__ == "__main__":
    run_demo()

"""
Compliance Risk and SLA Delay Inference Service

Provides validated risk scoring, delay probability prediction, and transparent
factor explanations using serialized machine learning pipelines.
"""

import os
import json
import joblib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np

from ml.training.train_models import (
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    train_and_save_models,
)


class ComplianceRiskPredictor:
    """
    Inference service for predicting application delay probability, estimated processing time,
    and composite compliance risk score.
    """

    def __init__(self, models_dir: Optional[str] = None):
        if models_dir is None:
            curr_dir = Path(__file__).resolve().parent
            default_dir = curr_dir.parent / "models"
            self.models_dir = str(default_dir)
        else:
            self.models_dir = models_dir

        self.clf_path = os.path.join(self.models_dir, "delay_classifier.joblib")
        self.reg_path = os.path.join(self.models_dir, "time_regressor.joblib")
        self.meta_path = os.path.join(self.models_dir, "model_metadata.json")

        self.clf = None
        self.reg = None
        self.metadata = {}
        self._load_models()

    def _load_models(self) -> None:
        """Loads serialized models or triggers training if files do not exist."""
        if not os.path.exists(self.clf_path) or not os.path.exists(self.reg_path):
            print(f"[INFO] Serialized models not found in {self.models_dir}. Auto-training from synthetic data...")
            clf, reg, meta = train_and_save_models(models_dir=self.models_dir)
            self.clf = clf
            self.reg = reg
            self.metadata = meta
            return

        self.clf = joblib.load(self.clf_path)
        self.reg = joblib.load(self.reg_path)

        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"is_synthetic": True, "model_version": "0.1.0"}

    def validate_inputs(self, features: Dict[str, Any]) -> None:
        """Validates numerical constraints and logical consistency of input attributes."""
        investment = float(features.get("investment", 0.0))
        if investment < 0:
            raise ValueError(f"Investment amount cannot be negative. Got: {investment}")

        employees = int(features.get("employees", 0))
        if employees < 0:
            raise ValueError(f"Employee count cannot be negative. Got: {employees}")

        approval_count = int(features.get("approval_count", 1))
        if approval_count < 0:
            raise ValueError(f"Approval count cannot be negative. Got: {approval_count}")

        document_count = int(features.get("document_count", 0))
        if document_count < 0:
            raise ValueError(f"Document count cannot be negative. Got: {document_count}")

        missing_document_count = int(features.get("missing_document_count", 0))
        if missing_document_count < 0:
            raise ValueError(f"Missing document count cannot be negative. Got: {missing_document_count}")

        if missing_document_count > document_count:
            raise ValueError(
                f"Missing document count ({missing_document_count}) cannot exceed total document count ({document_count})."
            )

        department_count = int(features.get("department_count", 1))
        if department_count < 0:
            raise ValueError(f"Department count cannot be negative. Got: {department_count}")

        previous_queries = int(features.get("previous_queries", 0))
        if previous_queries < 0:
            raise ValueError(f"Previous queries count cannot be negative. Got: {previous_queries}")

        sla_days = int(features.get("sla_days", 30))
        if sla_days <= 0:
            raise ValueError(f"Statutory SLA days must be strictly positive. Got: {sla_days}")

    def _generate_risk_factors(
        self,
        features: Dict[str, Any],
        delay_prob: float,
        predicted_days: float,
        sla_days: int,
    ) -> List[str]:
        """Generates transparent, human-readable risk factors explaining the prediction."""
        factors: List[str] = []

        missing_docs = int(features.get("missing_document_count", 0))
        if missing_docs > 0:
            factors.append(f"Missing documents detected ({missing_docs} missing) - increases clarification risk and query rounds.")

        insp_req = bool(features.get("inspection_required", False))
        if insp_req:
            factors.append("Mandatory physical on-site inspection required by statutory authorities.")

        dept_count = int(features.get("department_count", 1))
        if dept_count >= 3:
            factors.append(f"Multiple regulatory departments ({dept_count} departments) involved in parallel processing.")

        app_count = int(features.get("approval_count", 1))
        if app_count >= 5:
            factors.append(f"High approval density ({app_count} clearances) increases aggregate workflow complexity.")

        prev_queries = int(features.get("previous_queries", 0))
        if prev_queries >= 2:
            factors.append(f"Multiple previous queries raised ({prev_queries} queries) indicating documentation friction.")

        if delay_prob >= 0.60:
            factors.append(f"Predicted high probability of statutory SLA breach (P(delay) = {delay_prob*100:.1f}%).")

        if predicted_days > sla_days:
            factors.append(f"Estimated timeline ({predicted_days:.1f} days) exceeds statutory SLA target of {sla_days} days.")

        if not factors:
            factors.append("Standard application profile with no elevated risk indicators identified.")

        return factors

    def _calculate_risk_score(
        self,
        delay_prob: float,
        features: Dict[str, Any],
    ) -> Tuple[int, str]:
        """
        Calculates normalized composite risk score (0-100) and categorical risk level.
        Weighted components:
        - Delay probability: 40 pts
        - Missing documents: 20 pts
        - Inspection requirement: 15 pts
        - Department coordination complexity: 15 pts
        - Previous query friction: 10 pts
        """
        missing_docs = int(features.get("missing_document_count", 0))
        insp_req = 1.0 if features.get("inspection_required", False) else 0.0
        dept_count = int(features.get("department_count", 1))
        prev_queries = int(features.get("previous_queries", 0))

        score = (
            (0.40 * delay_prob * 100)
            + (0.20 * min(1.0, missing_docs / 3.0) * 100)
            + (0.15 * insp_req * 100)
            + (0.15 * min(1.0, max(0.0, (dept_count - 1) / 3.0)) * 100)
            + (0.10 * min(1.0, prev_queries / 2.0) * 100)
        )

        norm_score = int(round(min(100.0, max(0.0, score))))

        if norm_score >= 65:
            level = "HIGH"
        elif norm_score >= 35:
            level = "MEDIUM"
        else:
            level = "LOW"

        return norm_score, level

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts delay probability, estimated processing days, composite risk score,
        and human-readable risk factors from enterprise application features.
        """
        self.validate_inputs(features)

        # Prepare single-row DataFrame for inference
        row_dict = {
            "investment": float(features.get("investment", 0.0)),
            "employees": int(features.get("employees", 0)),
            "approval_count": int(features.get("approval_count", 1)),
            "document_count": int(features.get("document_count", 0)),
            "missing_document_count": int(features.get("missing_document_count", 0)),
            "inspection_required": int(bool(features.get("inspection_required", False))),
            "department_count": int(features.get("department_count", 1)),
            "previous_queries": int(features.get("previous_queries", 0)),
            "sla_days": int(features.get("sla_days", 30)),
            "state": str(features.get("state", "Uttar Pradesh")),
            "sector": str(features.get("sector", "Manufacturing")),
            "project_stage": str(features.get("project_stage", "Pre-Operation")),
            "applicant_type": str(features.get("applicant_type", "Enterprise")),
            "season": str(features.get("season", "Q3")),
        }

        X_input = pd.DataFrame([row_dict])

        # Model inferences
        delay_prob = round(float(self.clf.predict_proba(X_input)[0, 1]), 2)
        predicted_days = round(float(self.reg.predict(X_input)[0]), 1)

        sla_days = row_dict["sla_days"]
        risk_score, risk_level = self._calculate_risk_score(delay_prob, features)
        risk_factors = self._generate_risk_factors(features, delay_prob, predicted_days, sla_days)

        return {
            "delay_probability": delay_prob,
            "predicted_processing_days": predicted_days,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "model_type": {
                "delay": "RandomForestClassifier",
                "processing_time": "RandomForestRegressor",
            },
            "is_synthetic_model": True,
        }


# Singleton instance
risk_predictor = ComplianceRiskPredictor()

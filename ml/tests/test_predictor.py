"""
Comprehensive Unit Tests for ML Risk & Delay Prediction Subsystem

Covers dataset validation, reproducible training, classification & regression inference,
input boundary constraints, risk scoring, explainability, and metadata verification.
"""

import os
import json
import pytest
import pandas as pd

from ml.training.train_models import (
    load_and_validate_data,
    train_and_save_models,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_DELAY,
    TARGET_TIME,
)
from ml.inference.predictor import ComplianceRiskPredictor


@pytest.fixture
def predictor():
    """Fixture returning an initialized ComplianceRiskPredictor instance."""
    return ComplianceRiskPredictor()


@pytest.fixture
def sample_valid_features():
    """Valid baseline enterprise feature dictionary."""
    return {
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


# =====================================================================
# TEST 1: Synthetic Dataset Loads Successfully
# =====================================================================
def test_synthetic_dataset_loads():
    csv_path = "ml/data/synthetic_applications.csv"
    assert os.path.exists(csv_path)
    df = pd.read_csv(csv_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


# =====================================================================
# TEST 2: Required Schema Columns Exist
# =====================================================================
def test_required_columns_exist():
    df = load_and_validate_data()
    expected = NUMERICAL_FEATURES + CATEGORICAL_FEATURES + [TARGET_DELAY, TARGET_TIME]
    for col in expected:
        assert col in df.columns


# =====================================================================
# TEST 3: Minimum Row Count Threshold (>= 1000 Rows)
# =====================================================================
def test_dataset_minimum_rows():
    df = load_and_validate_data()
    assert len(df) >= 1000


# =====================================================================
# TEST 4: Reproducible Model Training
# =====================================================================
def test_training_reproducibility():
    _, _, meta1 = train_and_save_models(random_state=42)
    _, _, meta2 = train_and_save_models(random_state=42)
    assert meta1["classifier_metrics"] == meta2["classifier_metrics"]
    assert meta1["regressor_metrics"] == meta2["regressor_metrics"]


# =====================================================================
# TEST 5: Delay Classifier Trains and Evaluates
# =====================================================================
def test_classifier_trains():
    clf, _, meta = train_and_save_models()
    assert clf is not None
    assert meta["classifier_metrics"]["accuracy"] >= 0.75
    assert meta["classifier_metrics"]["roc_auc"] >= 0.80


# =====================================================================
# TEST 6: Processing Time Regressor Trains and Evaluates
# =====================================================================
def test_regressor_trains():
    _, reg, meta = train_and_save_models()
    assert reg is not None
    assert meta["regressor_metrics"]["r2"] >= 0.70
    assert meta["regressor_metrics"]["mae"] < 10.0


# =====================================================================
# TEST 7: Prediction Returns Delay Probability (0.0 to 1.0)
# =====================================================================
def test_prediction_delay_probability(predictor, sample_valid_features):
    result = predictor.predict(sample_valid_features)
    assert "delay_probability" in result
    prob = result["delay_probability"]
    assert isinstance(prob, float)
    assert 0.0 <= prob <= 1.0


# =====================================================================
# TEST 8: Prediction Returns Estimated Processing Days
# =====================================================================
def test_prediction_processing_days(predictor, sample_valid_features):
    result = predictor.predict(sample_valid_features)
    assert "predicted_processing_days" in result
    days = result["predicted_processing_days"]
    assert isinstance(days, (int, float))
    assert days > 0


# =====================================================================
# TEST 9: Risk Score Bounded (0 to 100) and Valid Level
# =====================================================================
def test_risk_score_and_level(predictor, sample_valid_features):
    result = predictor.predict(sample_valid_features)
    assert "risk_score" in result
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert len(result["risk_factors"]) > 0


# =====================================================================
# TEST 10: Negative Numerical Input Validation Rejection
# =====================================================================
def test_invalid_negative_input_rejected(predictor, sample_valid_features):
    bad_features = sample_valid_features.copy()
    bad_features["investment"] = -50000
    with pytest.raises(ValueError, match="Investment amount cannot be negative"):
        predictor.predict(bad_features)

    bad_features2 = sample_valid_features.copy()
    bad_features2["employees"] = -10
    with pytest.raises(ValueError, match="Employee count cannot be negative"):
        predictor.predict(bad_features2)

    bad_features3 = sample_valid_features.copy()
    bad_features3["sla_days"] = 0
    with pytest.raises(ValueError, match="Statutory SLA days must be strictly positive"):
        predictor.predict(bad_features3)


# =====================================================================
# TEST 11: Missing Documents Cannot Exceed Document Count
# =====================================================================
def test_missing_documents_exceeds_total(predictor, sample_valid_features):
    bad_features = sample_valid_features.copy()
    bad_features["document_count"] = 10
    bad_features["missing_document_count"] = 15  # Exceeds total
    with pytest.raises(ValueError, match="cannot exceed total document count"):
        predictor.predict(bad_features)


# =====================================================================
# TEST 12: Deterministic Output for Identical Input
# =====================================================================
def test_deterministic_prediction(predictor, sample_valid_features):
    res1 = predictor.predict(sample_valid_features)
    res2 = predictor.predict(sample_valid_features)

    assert res1["delay_probability"] == res2["delay_probability"]
    assert res1["predicted_processing_days"] == res2["predicted_processing_days"]
    assert res1["risk_score"] == res2["risk_score"]
    assert res1["risk_level"] == res2["risk_level"]
    assert res1["risk_factors"] == res2["risk_factors"]


# =====================================================================
# TEST 13: Auto-Loads or Initializes Models Cleanly
# =====================================================================
def test_model_loading():
    pred = ComplianceRiskPredictor(models_dir="ml/models")
    assert pred.clf is not None
    assert pred.reg is not None


# =====================================================================
# TEST 14: Model Metadata Identifies Synthetic Training Dataset
# =====================================================================
def test_metadata_synthetic_label():
    meta_path = "ml/models/model_metadata.json"
    assert os.path.exists(meta_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["is_synthetic"] is True
    assert meta["dataset_type"] == "SYNTHETIC_DEMO"
    assert "synthetic" in meta["disclaimer"].lower()

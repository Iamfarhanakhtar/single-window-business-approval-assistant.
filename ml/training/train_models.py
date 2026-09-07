"""
Model Training Pipeline for ML Risk & Delay Prediction

Trains a RandomForestClassifier for SLA breach probability and a RandomForestRegressor
for estimated processing days, enforcing zero target leakage and reproducible splits.
"""

import os
import json
import joblib
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Dict, Any

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

NUMERICAL_FEATURES = [
    "investment",
    "employees",
    "approval_count",
    "document_count",
    "missing_document_count",
    "inspection_required",
    "department_count",
    "previous_queries",
    "sla_days",
]

CATEGORICAL_FEATURES = [
    "state",
    "sector",
    "project_stage",
    "applicant_type",
    "season",
]

TARGET_DELAY = "delayed"
TARGET_TIME = "actual_processing_days"


def load_and_validate_data(csv_path: str = "ml/data/synthetic_applications.csv") -> pd.DataFrame:
    """Loads and validates columns in the synthetic applications dataset."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Synthetic dataset not found at: {csv_path}")

    df = pd.read_csv(csv_path)
    required_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES + [TARGET_DELAY, TARGET_TIME]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in dataset: {missing_cols}")

    return df


def build_preprocessor() -> ColumnTransformer:
    """Creates a ColumnTransformer pipeline for numerical and categorical features."""
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ]
    )


def train_and_save_models(
    csv_path: str = "ml/data/synthetic_applications.csv",
    models_dir: str = "ml/models",
    random_state: int = 42,
) -> Tuple[Pipeline, Pipeline, Dict[str, Any]]:
    """
    Trains classification and regression pipelines and saves serialized models & metadata.
    """
    df = load_and_validate_data(csv_path)

    # Feature matrix X (Zero data leakage: target columns strictly excluded)
    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES].copy()
    y_delay = df[TARGET_DELAY].values
    y_time = df[TARGET_TIME].values

    # Train/Test split
    X_train, X_test, y_del_train, y_del_test, y_tim_train, y_tim_test = train_test_split(
        X, y_delay, y_time, test_size=0.20, random_state=random_state, stratify=y_delay
    )

    # 1. Delay Classifier Pipeline
    clf_pipeline = Pipeline([
        ("preprocessor", build_preprocessor()),
        ("classifier", RandomForestClassifier(n_estimators=100, max_depth=8, random_state=random_state)),
    ])
    clf_pipeline.fit(X_train, y_del_train)

    # 2. Processing Time Regressor Pipeline
    reg_pipeline = Pipeline([
        ("preprocessor", build_preprocessor()),
        ("regressor", RandomForestRegressor(n_estimators=100, max_depth=8, random_state=random_state)),
    ])
    reg_pipeline.fit(X_train, y_tim_train)

    # Evaluation on Test Set
    del_preds = clf_pipeline.predict(X_test)
    del_probs = clf_pipeline.predict_proba(X_test)[:, 1]

    tim_preds = reg_pipeline.predict(X_test)

    clf_metrics = {
        "accuracy": round(float(accuracy_score(y_del_test, del_preds)), 4),
        "precision": round(float(precision_score(y_del_test, del_preds)), 4),
        "recall": round(float(recall_score(y_del_test, del_preds)), 4),
        "f1": round(float(f1_score(y_del_test, del_preds)), 4),
        "roc_auc": round(float(roc_auc_score(y_del_test, del_probs)), 4),
    }

    reg_metrics = {
        "mae": round(float(mean_absolute_error(y_tim_test, tim_preds)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_tim_test, tim_preds))), 4),
        "r2": round(float(r2_score(y_tim_test, tim_preds)), 4),
    }

    # Metadata dictionary
    metadata = {
        "model_version": "0.1.0",
        "training_date": datetime.now(timezone.utc).isoformat(),
        "dataset_type": "SYNTHETIC_DEMO",
        "is_synthetic": True,
        "disclaimer": "This dataset is synthetic/demo data created for SIH prototype development. It is not official government historical data and must not be used to make real-world regulatory claims.",
        "random_seed": random_state,
        "dataset_rows": len(df),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "classifier": "RandomForestClassifier",
        "classifier_metrics": clf_metrics,
        "regressor": "RandomForestRegressor",
        "regressor_metrics": reg_metrics,
    }

    # Save to models directory
    out_dir = Path(models_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(clf_pipeline, out_dir / "delay_classifier.joblib")
    joblib.dump(reg_pipeline, out_dir / "time_regressor.joblib")

    with open(out_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("======================================================================")
    print("MODEL TRAINING SUMMARY")
    print("======================================================================")
    print(f"Dataset Rows: {len(df)} (Train: {len(X_train)}, Test: {len(X_test)})")
    print(f"Classifier Metrics: Accuracy={clf_metrics['accuracy']}, F1={clf_metrics['f1']}, ROC-AUC={clf_metrics['roc_auc']}")
    print(f"Regressor Metrics:  MAE={reg_metrics['mae']} days, RMSE={reg_metrics['rmse']} days, R2={reg_metrics['r2']}")
    print(f"Saved models to: {models_dir}/")
    print("======================================================================")

    return clf_pipeline, reg_pipeline, metadata


if __name__ == "__main__":
    train_and_save_models()

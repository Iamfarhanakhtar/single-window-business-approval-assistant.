"""
Model Evaluation and Diagnostic Reporting

Evaluates trained classification and regression pipelines against holdout test data
and outputs detailed performance diagnostics.
"""

import sys
import os
from pathlib import Path

# Ensure project root is on sys.path
curr_dir = Path(__file__).resolve().parent
project_root = curr_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    classification_report,
)

from ml.training.train_models import (
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_DELAY,
    TARGET_TIME,
    load_and_validate_data,
)


def evaluate_models(
    csv_path: str = "ml/data/synthetic_applications.csv",
    models_dir: str = "ml/models",
    random_state: int = 42,
):
    print("======================================================================")
    print("ML RISK & DELAY MODEL EVALUATION REPORT")
    print("======================================================================")
    print("WARNING: Evaluation is based on synthetic/demo data and does not represent")
    print("real government performance.")
    print("======================================================================")
    print()

    clf_path = os.path.join(models_dir, "delay_classifier.joblib")
    reg_path = os.path.join(models_dir, "time_regressor.joblib")

    if not os.path.exists(clf_path) or not os.path.exists(reg_path):
        raise FileNotFoundError(f"Model files not found in {models_dir}. Please run train_models.py first.")

    clf = joblib.load(clf_path)
    reg = joblib.load(reg_path)

    df = load_and_validate_data(csv_path)
    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES].copy()
    y_delay = df[TARGET_DELAY].values
    y_time = df[TARGET_TIME].values

    _, X_test, _, y_del_test, _, y_tim_test = train_test_split(
        X, y_delay, y_time, test_size=0.20, random_state=random_state, stratify=y_delay
    )

    # 1. Classification Evaluation
    del_preds = clf.predict(X_test)
    del_probs = clf.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_del_test, del_preds)
    prec = precision_score(y_del_test, del_preds)
    rec = recall_score(y_del_test, del_preds)
    f1 = f1_score(y_del_test, del_preds)
    roc = roc_auc_score(y_del_test, del_probs)

    print("--- 1. Delay Classifier (RandomForestClassifier) ---")
    print(f"Test Samples Evaluated: {len(y_del_test)}")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc:.4f}")
    print()
    print("Classification Report:")
    print(classification_report(y_del_test, del_preds, target_names=["On-Time (0)", "Delayed (1)"]))
    print()

    # 2. Regression Evaluation
    tim_preds = reg.predict(X_test)
    mae = mean_absolute_error(y_tim_test, tim_preds)
    rmse = np.sqrt(mean_squared_error(y_tim_test, tim_preds))
    r2 = r2_score(y_tim_test, tim_preds)

    print("--- 2. Processing Time Regressor (RandomForestRegressor) ---")
    print(f"Test Samples Evaluated: {len(y_tim_test)}")
    print(f"Mean Absolute Error (MAE): {mae:.4f} days")
    print(f"Root Mean Squared Error (RMSE): {rmse:.4f} days")
    print(f"R-squared (R2 Score): {r2:.4f}")
    print("======================================================================")

    return {
        "classification": {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "roc_auc": roc},
        "regression": {"mae": mae, "rmse": rmse, "r2": r2},
    }


if __name__ == "__main__":
    evaluate_models()

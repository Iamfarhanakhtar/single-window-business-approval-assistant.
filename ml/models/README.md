# ML Model Artifacts & Metadata

## Overview
This directory contains serialized machine learning pipelines trained to predict **statutory SLA breach probabilities** and **estimated clearance processing times** for industrial enterprise applications.

---

> [!CAUTION]
> **Prototype Model Disclaimer**:
> Current models are **trained on synthetic/demo data and are intended ONLY for Smart India Hackathon (SIH 2026) prototype demonstration**.
> - **NOT an Official Government Prediction**: Predictions do not constitute statutory guarantees or official government commitments.
> - **Zero Legal Applicability**: The ML model does not determine which approvals are legally required. Legal applicability is handled exclusively by the Deterministic Rule Engine (`ai/rules/`).

---

## 1. Saved Artifacts

- [`delay_classifier.joblib`](file:///Users/farhan/Desktop/SIH/ml/models/delay_classifier.joblib): `RandomForestClassifier` pipeline predicting binary delay and calibrated delay probability $P(\text{delay})$.
- [`time_regressor.joblib`](file:///Users/farhan/Desktop/SIH/ml/models/time_regressor.joblib): `RandomForestRegressor` pipeline predicting `actual_processing_days`.
- [`model_metadata.json`](file:///Users/farhan/Desktop/SIH/ml/models/model_metadata.json): JSON record of features, model parameters, seed, and evaluation metrics.

---

## 2. Model Regeneration
To retrain and regenerate model binaries:
```bash
python3 ml/training/train_models.py
```

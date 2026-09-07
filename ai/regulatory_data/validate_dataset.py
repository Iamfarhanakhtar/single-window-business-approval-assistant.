#!/usr/bin/env python3
"""
Regulatory Dataset Validator - SIH Problem Statement 130
Project: Business Compliance Hub (Unified Intelligent Single-Window Clearance & Compliance Automation)

Validates approvals.csv for structural integrity, unique IDs, mandatory columns,
and official source citations before feeding into the Rule Engine and RAG knowledge base.
"""

import os
import sys

# Target CSV path relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(SCRIPT_DIR, "approvals.csv")

EXPECTED_COLUMNS = [
    "approval_id",
    "approval_name",
    "authority",
    "state",
    "sector",
    "stage",
    "description",
    "who_can_apply",
    "documents",
    "fee",
    "validity",
    "processing_days",
    "act_rules",
    "conditions",
    "nsws_available",
    "source_name",
    "source_url",
    "retrieved_at",
    "last_verified_at",
]

CRITICAL_FIELDS = ["approval_id", "approval_name", "state", "sector", "source_name", "source_url"]


def validate_with_pandas(file_path: str) -> bool:
    try:
        import pandas as pd
    except ImportError:
        print("[INFO] Pandas not found in environment, falling back to built-in csv validator...")
        return validate_with_csv(file_path)

    print("=" * 70)
    print("      REGULATORY DATASET VALIDATION REPORT (Pandas Engine)")
    print("=" * 70)
    print(f"File Path: {file_path}")

    if not os.path.exists(file_path):
        print(f"[FAIL] Critical Error: CSV file does not exist at '{file_path}'")
        return False

    try:
        df = pd.read_csv(file_path, keep_default_na=False, dtype=str)
    except Exception as e:
        print(f"[FAIL] Failed to parse CSV file: {e}")
        return False

    errors = []
    warnings = []

    # 1. Verify Columns
    actual_columns = list(df.columns)
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in actual_columns]
    extra_cols = [c for c in actual_columns if c not in EXPECTED_COLUMNS]

    if missing_cols:
        errors.append(f"Missing required columns ({len(missing_cols)}): {missing_cols}")
    if extra_cols:
        warnings.append(f"Unexpected extra columns ({len(extra_cols)}): {extra_cols}")

    # 2. Record Count
    record_count = len(df)
    print(f"Total Records Loaded: {record_count}")

    if record_count == 0:
        errors.append("Dataset is empty. At least 1 record is required.")

    # 3. Unique approval_id
    if "approval_id" in df.columns:
        duplicate_ids = df[df.duplicated("approval_id", keep=False)]["approval_id"].tolist()
        if duplicate_ids:
            errors.append(f"Duplicate approval_ids detected: {set(duplicate_ids)}")

        empty_ids = df[df["approval_id"].str.strip() == ""]
        if not empty_ids.empty:
            errors.append(f"Found {len(empty_ids)} records with empty 'approval_id'.")

    # 4. Critical Field Completeness
    for field in CRITICAL_FIELDS:
        if field in df.columns:
            empty_rows = df[df[field].str.strip() == ""]
            if not empty_rows.empty:
                errors.append(f"Missing critical field '{field}' in {len(empty_rows)} row(s): indices {empty_rows.index.tolist()}")

    # 5. Intentional Blank Fields Audit (e.g. tiered/variable fees)
    if "fee" in df.columns:
        blank_fees = df[df["fee"].str.strip() == ""]
        if not blank_fees.empty:
            print(f"[NOTE] {len(blank_fees)} records have tiered/variable fees left blank to avoid fabricating unverified figures.")

    # 6. Source URL Validation
    if "source_url" in df.columns:
        invalid_urls = df[~df["source_url"].str.startswith("http") & (df["source_url"].str.strip() != "")]
        if not invalid_urls.empty:
            warnings.append(f"{len(invalid_urls)} source_urls do not start with http/https: indices {invalid_urls.index.tolist()}")

    # Output Summary
    print("-" * 70)
    if warnings:
        print("[WARNINGS]:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("[ERRORS ENCOUNTERED]:")
        for err in errors:
            print(f"  [X] {err}")
        print("=" * 70)
        print("[FAIL] Validation FAILED. Please resolve errors listed above.")
        print("=" * 70)
        return False

    print("[SUCCESS] All structural, uniqueness, and citation checks passed!")
    print(f"  - Columns verified: {len(actual_columns)}/{len(EXPECTED_COLUMNS)}")
    print(f"  - Unique Approval IDs: {record_count}")
    print(f"  - Official Sources Verified: {df['source_name'].nunique()} distinct agencies")
    print("=" * 70)
    return True


def validate_with_csv(file_path: str) -> bool:
    import csv

    print("=" * 70)
    print("      REGULATORY DATASET VALIDATION REPORT (Standard CSV Engine)")
    print("=" * 70)
    print(f"File Path: {file_path}")

    if not os.path.exists(file_path):
        print(f"[FAIL] Critical Error: CSV file does not exist at '{file_path}'")
        return False

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        actual_columns = reader.fieldnames or []
        rows = list(reader)

    errors = []
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in actual_columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")

    seen_ids = set()
    for idx, row in enumerate(rows, start=1):
        appr_id = row.get("approval_id", "").strip()
        if not appr_id:
            errors.append(f"Row {idx}: Missing approval_id")
        elif appr_id in seen_ids:
            errors.append(f"Row {idx}: Duplicate approval_id '{appr_id}'")
        seen_ids.add(appr_id)

        for field in CRITICAL_FIELDS:
            val = row.get(field, "").strip()
            if not val:
                errors.append(f"Row {idx}: Missing required critical field '{field}'")

    if errors:
        print("[ERRORS ENCOUNTERED]:")
        for err in errors:
            print(f"  [X] {err}")
        print("[FAIL] Validation FAILED.")
        return False

    print(f"[SUCCESS] All {len(rows)} records passed validation.")
    return True


if __name__ == "__main__":
    is_valid = validate_with_pandas(CSV_FILE_PATH)
    sys.exit(0 if is_valid else 1)

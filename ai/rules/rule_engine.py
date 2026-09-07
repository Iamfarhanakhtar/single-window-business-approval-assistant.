"""
Deterministic Regulatory Rule Engine

Evaluates business profiles against the statutory approvals catalog to determine
potential applicability, document requirements, and dependency sequencing without an LLM.
"""

import os
import csv
from typing import Dict, List, Any, Optional
from pathlib import Path

from ai.rules.models import (
    BusinessProfile,
    ApprovalStatus,
    EvaluationResult,
    AnalysisSummary,
)
from ai.rules.rules import (
    evaluate_approval,
    get_required_documents,
    get_detailed_documents,
    resolve_dependencies,
)


class RegulatoryRuleEngine:
    """
    Deterministic, explainable rule engine that evaluates an enterprise profile
    against statutory approval criteria from central and state regulations.
    """

    def __init__(self, csv_path: Optional[str] = None):
        """
        Initializes the rule engine with the regulatory approvals dataset.
        """
        if csv_path is None:
            # Locate approvals.csv relative to this file or current working directory
            curr_dir = Path(__file__).resolve().parent
            default_path = curr_dir.parent / "regulatory_data" / "approvals.csv"
            if default_path.exists():
                self.csv_path = str(default_path)
            else:
                self.csv_path = "ai/regulatory_data/approvals.csv"
        else:
            self.csv_path = csv_path

        self._approvals: List[Dict[str, str]] = []
        self._load_dataset()

    def _load_dataset(self) -> None:
        """Loads and parses the regulatory dataset from CSV."""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Regulatory approvals dataset not found at: {self.csv_path}")

        records = []
        with open(self.csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("approval_id"):
                    records.append({k.strip(): (v.strip() if v else "") for k, v in row.items()})

        if not records:
            raise ValueError(f"No regulatory approval records loaded from: {self.csv_path}")

        self._approvals = records

    @property
    def total_approvals(self) -> int:
        """Returns count of loaded statutory approvals."""
        return len(self._approvals)

    def analyze(self, profile: BusinessProfile) -> AnalysisSummary:
        """
        Analyzes a BusinessProfile against all loaded approvals.
        Returns a structured AnalysisSummary with categorized outcomes,
        deduplicated documents, and dependency execution sequence.
        """
        potentially_applicable: List[EvaluationResult] = []
        partially_matched: List[EvaluationResult] = []
        requires_verification: List[EvaluationResult] = []
        not_matched: List[EvaluationResult] = []

        all_results: List[EvaluationResult] = []

        for row in self._approvals:
            result = evaluate_approval(profile, row)
            all_results.append(result)

            if result.status == ApprovalStatus.POTENTIALLY_APPLICABLE:
                potentially_applicable.append(result)
            elif result.status == ApprovalStatus.PARTIALLY_MATCHED:
                partially_matched.append(result)
            elif result.status == ApprovalStatus.REQUIRES_VERIFICATION:
                requires_verification.append(result)
            else:
                not_matched.append(result)

        # Sort within categories by match score descending
        potentially_applicable.sort(key=lambda x: x.match_score, reverse=True)
        partially_matched.sort(key=lambda x: x.match_score, reverse=True)

        # Aggregate documents
        documents = get_required_documents(all_results)
        detailed_documents = get_detailed_documents(all_results)

        # Resolve dependencies among potentially applicable + partially matched
        candidate_ids = [r.approval_id for r in potentially_applicable + partially_matched]
        dependency_order = resolve_dependencies(candidate_ids)

        return AnalysisSummary(
            business_profile=profile.model_dump(),
            total_approvals_evaluated=len(self._approvals),
            potentially_applicable=potentially_applicable,
            partially_matched=partially_matched,
            requires_verification=requires_verification,
            not_matched=not_matched,
            documents=documents,
            detailed_documents=detailed_documents,
            dependency_order=dependency_order,
        )

    def evaluate_applicability(self, business_attributes: Dict[str, Any]) -> List[str]:
        """
        Legacy dictionary-based compatibility interface.
        Returns list of approval IDs classified as POTENTIALLY_APPLICABLE.
        """
        # Map common dictionary keys to BusinessProfile schema
        state = business_attributes.get("state", "Uttar Pradesh")
        sector = business_attributes.get("sector", "Manufacturing")
        investment = float(business_attributes.get("investment", business_attributes.get("investment_amount", 0.0)))
        employees = int(business_attributes.get("employees", business_attributes.get("employee_count", 0)))
        stage = business_attributes.get("project_stage", business_attributes.get("stage", None))

        profile = BusinessProfile(
            state=state,
            sector=sector,
            investment=investment,
            employees=employees,
            project_stage=stage,
            connected_load_kw=float(business_attributes.get("connected_load_kw", 0.0)),
            has_boiler=bool(business_attributes.get("has_boiler", False)),
            boiler_pressure=float(business_attributes.get("boiler_pressure", 0.0)),
            uses_water=bool(business_attributes.get("uses_water", False)),
            generates_effluent=bool(business_attributes.get("generates_effluent", False)),
            food_business=bool(business_attributes.get("food_business", False)),
        )

        summary = self.analyze(profile)
        return [res.approval_id for res in summary.potentially_applicable]


# Singleton instance
rule_engine = RegulatoryRuleEngine()

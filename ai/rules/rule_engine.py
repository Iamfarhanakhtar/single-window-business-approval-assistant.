"""Deterministic Regulatory Rule Engine Interface for Developer 1"""
from typing import Dict, Any, List

class RegulatoryRuleEngine:
    """
    Evaluates statutory business rules deterministically based on central and state acts.
    """
    def __init__(self):
        pass

    def evaluate_applicability(self, business_attributes: Dict[str, Any]) -> List[str]:
        """Returns list of mandatory approval codes."""
        # Developer 1 can expand this rule matrix
        approvals = []
        if business_attributes.get("employee_count", 0) >= 10:
            approvals.append("FACTORY_LIC")
        if business_attributes.get("investment_amount", 0) > 10000000:
            approvals.append("FIRE_NOC")
        return approvals

rule_engine = RegulatoryRuleEngine()

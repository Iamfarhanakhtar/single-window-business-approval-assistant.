"""
Regulatory Rule Engine CLI Demo

Demonstrates deterministic evaluation of a sample enterprise profile (Food Processing in UP)
without relying on an LLM.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
curr_path = Path(__file__).resolve().parent
project_root = curr_path.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ai.rules.models import BusinessProfile, ApprovalStatus
from ai.rules.rule_engine import RegulatoryRuleEngine


def format_currency_inr(amount: float) -> str:
    """Formats amount in Crore / Lakhs INR."""
    if amount >= 10_000_000:
        cr = amount / 10_000_000
        return f"₹{cr:g} crore"
    elif amount >= 100_000:
        lakh = amount / 100_000
        return f"₹{lakh:g} lakh"
    return f"₹{amount:,.0f}"


def run_demo():
    print("========================================")
    print("BUSINESS COMPLIANCE HUB")
    print("REGULATORY RULE ENGINE")
    print("========================================")
    print()

    # Define sample enterprise profile
    profile = BusinessProfile(
        state="Uttar Pradesh",
        sector="Food Processing",
        investment=50000000.0,  # 5 Crore INR
        employees=80,
        project_stage="Pre-Operation",
        connected_load_kw=75.0,
        has_boiler=True,
        boiler_pressure=2.0,
        uses_water=True,
        generates_effluent=True,
        food_business=True,
    )

    print("Business Profile")
    print("----------------")
    print(f"State: {profile.state}")
    print(f"Sector: {profile.sector}")
    print(f"Investment: {format_currency_inr(profile.investment)}")
    print(f"Employees: {profile.employees}")
    print(f"Stage: {profile.project_stage}")
    print(f"Connected Load: {profile.connected_load_kw} kW")
    print(f"Boiler: {'Yes' if profile.has_boiler else 'No'} (Pressure: {profile.boiler_pressure} kg/cm2)")
    print(f"Water Usage / Effluent: {'Yes' if profile.uses_water else 'No'}")
    print(f"Food Business: {'Yes' if profile.food_business else 'No'}")
    print()

    engine = RegulatoryRuleEngine()
    summary = engine.analyze(profile)

    print("Approval Analysis")
    print("-----------------")
    print()

    counter = 1
    # Print Potentially Applicable
    for res in summary.potentially_applicable:
        print(f"{counter}. [{res.status.value}]")
        print(f"   Approval: {res.approval_name} ({res.approval_id})")
        print(f"   Authority: {res.authority}")
        print(f"   Match Score: {res.match_score:.2f}")
        print("   Reasons:")
        for r in res.reasons:
            print(f"   - {r}")
        if res.documents:
            print(f"   Documents Required: {len(res.documents)} items")
        print()
        counter += 1

    # Print Partially Matched
    for res in summary.partially_matched:
        print(f"{counter}. [{res.status.value}]")
        print(f"   Approval: {res.approval_name} ({res.approval_id})")
        print(f"   Authority: {res.authority}")
        print(f"   Match Score: {res.match_score:.2f}")
        print("   Reasons:")
        for r in res.reasons:
            print(f"   - {r}")
        print()
        counter += 1

    # Print Requires Verification
    for res in summary.requires_verification:
        print(f"{counter}. [{res.status.value}]")
        print(f"   Approval: {res.approval_name} ({res.approval_id})")
        print(f"   Authority: {res.authority}")
        print("   Reasons:")
        for r in res.reasons:
            print(f"   - {r}")
        print()
        counter += 1

    # Print Not Matched
    for res in summary.not_matched:
        print(f"{counter}. [{res.status.value}]")
        print(f"   Approval: {res.approval_name} ({res.approval_id})")
        print(f"   Authority: {res.authority}")
        print("   Reasons:")
        for r in res.reasons:
            print(f"   - {r}")
        print()
        counter += 1

    print("========================================")
    print("SUMMARY")
    print("========================================")
    print(f"Approvals evaluated: {summary.total_approvals_evaluated}")
    print(f"Potentially applicable: {len(summary.potentially_applicable)}")
    print(f"Partially matched: {len(summary.partially_matched)}")
    print(f"Requires verification: {len(summary.requires_verification)}")
    print(f"Not matched: {len(summary.not_matched)}")
    print(f"Documents identified: {len(summary.documents)}")
    if summary.dependency_order:
        print(f"Recommended execution sequence: {' -> '.join(summary.dependency_order)}")
    print("========================================")


if __name__ == "__main__":
    run_demo()

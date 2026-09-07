"""
Unit Tests for Deterministic Regulatory Rule Engine

Covers multi-criteria statutory evaluation, document deduplication,
dependency resolution, input validation, and result determinism.
"""

import pytest
from pydantic import ValidationError

from ai.rules.models import (
    BusinessProfile,
    ApprovalStatus,
    EvaluationResult,
)
from ai.rules.rule_engine import RegulatoryRuleEngine
from ai.rules.rules import (
    get_required_documents,
    resolve_dependencies,
    RULE_DEPENDENCIES,
)


@pytest.fixture
def engine():
    """Fixture initializing RegulatoryRuleEngine."""
    return RegulatoryRuleEngine()


# =====================================================================
# TEST 1: Uttar Pradesh + Manufacturing (Pre-Establishment)
# =====================================================================
def test_up_manufacturing_pre_establishment(engine):
    profile = BusinessProfile(
        state="Uttar Pradesh",
        sector="Manufacturing",
        investment=20000000.0,
        employees=45,
        project_stage="Pre-Establishment",
        connected_load_kw=40.0,
        uses_water=True,
        generates_effluent=True,
        requires_fire_clearance=True,
    )
    summary = engine.analyze(profile)
    applicable_ids = [r.approval_id for r in summary.potentially_applicable]

    # Should match CTE, Fire NOC, and Factory License
    assert "UP_PCB_CTE_001" in applicable_ids
    assert "UP_FIRE_NOC_003" in applicable_ids
    assert "UP_FAC_REG_005" in applicable_ids

    # Should NOT match FSSAI since it's not food business
    not_matched_ids = [r.approval_id for r in summary.not_matched]
    assert "IN_FSSAI_MFG_004" in not_matched_ids


# =====================================================================
# TEST 2: Uttar Pradesh + Food Processing (Pre-Operation)
# =====================================================================
def test_up_food_processing_pre_operation(engine):
    profile = BusinessProfile(
        state="Uttar Pradesh",
        sector="Food Processing",
        investment=50000000.0,
        employees=80,
        project_stage="Pre-Operation",
        connected_load_kw=75.0,
        has_boiler=True,
        boiler_pressure=2.0,
        uses_water=True,
        generates_effluent=True,
        food_business=True,
    )
    summary = engine.analyze(profile)
    applicable_ids = [r.approval_id for r in summary.potentially_applicable]

    assert "IN_FSSAI_MFG_004" in applicable_ids
    assert "UP_PCB_CTO_002" in applicable_ids
    assert "UP_ELEC_CEIG_007" in applicable_ids
    assert "IN_BOILER_REG_008" in applicable_ids
    assert "IN_WEIGHTS_MEAS_009" in applicable_ids


# =====================================================================
# TEST 3: Different State (Jurisdiction Mismatch)
# =====================================================================
def test_different_state_rejection(engine):
    profile = BusinessProfile(
        state="Karnataka",
        sector="Manufacturing",
        investment=10000000.0,
        employees=30,
        project_stage="Pre-Establishment",
    )
    summary = engine.analyze(profile)

    # State-specific UP clearances must NOT match for Karnataka
    not_matched_ids = [r.approval_id for r in summary.not_matched]
    assert "UP_PCB_CTE_001" in not_matched_ids
    assert "UP_FIRE_NOC_003" in not_matched_ids
    assert "UP_FAC_REG_005" in not_matched_ids

    # Mismatch reasons must explicitly mention state difference
    for res in summary.not_matched:
        if res.approval_id == "UP_PCB_CTE_001":
            assert any("State mismatch" in r for r in res.reasons)


# =====================================================================
# TEST 4: Different Sector (Sector Mismatch)
# =====================================================================
def test_different_sector_rejection(engine):
    profile = BusinessProfile(
        state="Uttar Pradesh",
        sector="Information Technology",
        investment=5000000.0,
        employees=25,
        project_stage="Pre-Operation",
    )
    summary = engine.analyze(profile)
    not_matched_ids = [r.approval_id for r in summary.not_matched]

    # Manufacturing-specific clearances should not match IT software service
    assert "UP_PCB_CTE_001" in not_matched_ids
    assert "IN_BOILER_REG_008" in not_matched_ids
    assert "IN_FSSAI_MFG_004" in not_matched_ids


# =====================================================================
# TEST 5: Missing / Incomplete Project Information
# =====================================================================
def test_missing_project_information(engine):
    profile = BusinessProfile(
        state="Uttar Pradesh",
        sector="Manufacturing",
        # Stage is omitted (None), employee count is 0
    )
    summary = engine.analyze(profile)
    
    # Should flag clearances requiring stage/site verification
    assert len(summary.partially_matched) > 0 or len(summary.requires_verification) > 0
    
    # Tree felling without explicit flag must require verification
    verif_ids = [r.approval_id for r in summary.requires_verification]
    assert "UP_TREE_TRANS_010" in verif_ids


# =====================================================================
# TEST 6: High Connected Electrical Load
# =====================================================================
def test_high_connected_electrical_load(engine):
    profile = BusinessProfile(
        state="Uttar Pradesh",
        sector="Manufacturing",
        connected_load_kw=120.0,
        project_stage="Pre-Operation",
    )
    summary = engine.analyze(profile)
    applicable_ids = [r.approval_id for r in summary.potentially_applicable]
    
    assert "UP_ELEC_CEIG_007" in applicable_ids
    elec_res = next(r for r in summary.potentially_applicable if r.approval_id == "UP_ELEC_CEIG_007")
    assert any(">= 50 kW" in r for r in elec_res.reasons)


# =====================================================================
# TEST 7: Boiler-Related Profile Triggering & Rejection
# =====================================================================
def test_boiler_conditions(engine):
    # Profile WITH boiler
    profile_with_boiler = BusinessProfile(
        state="Uttar Pradesh",
        sector="Manufacturing",
        has_boiler=True,
        boiler_pressure=3.5,
        project_stage="Pre-Operation",
    )
    summary1 = engine.analyze(profile_with_boiler)
    app_ids1 = [r.approval_id for r in summary1.potentially_applicable]
    assert "IN_BOILER_REG_008" in app_ids1

    # Profile WITHOUT boiler
    profile_no_boiler = BusinessProfile(
        state="Uttar Pradesh",
        sector="Manufacturing",
        has_boiler=False,
        boiler_pressure=0.0,
        project_stage="Pre-Operation",
    )
    summary2 = engine.analyze(profile_no_boiler)
    not_matched_ids = [r.approval_id for r in summary2.not_matched]
    assert "IN_BOILER_REG_008" in not_matched_ids


# =====================================================================
# TEST 8: Food Business Specific Flag
# =====================================================================
def test_food_business_flag(engine):
    profile_food = BusinessProfile(
        state="Uttar Pradesh",
        sector="Food Processing",
        food_business=True,
        project_stage="Pre-Operation",
    )
    summary = engine.analyze(profile_food)
    app_ids = [r.approval_id for r in summary.potentially_applicable]
    assert "IN_FSSAI_MFG_004" in app_ids
    assert "IN_WEIGHTS_MEAS_009" in app_ids


# =====================================================================
# TEST 9: Empty & Invalid Profile Validation Errors
# =====================================================================
def test_invalid_profile_validation():
    # Negative investment
    with pytest.raises(ValidationError):
        BusinessProfile(state="Uttar Pradesh", sector="Manufacturing", investment=-5000)

    # Negative employees
    with pytest.raises(ValidationError):
        BusinessProfile(state="Uttar Pradesh", sector="Manufacturing", employees=-10)

    # Negative electrical load
    with pytest.raises(ValidationError):
        BusinessProfile(state="Uttar Pradesh", sector="Manufacturing", connected_load_kw=-15.0)

    # Blank state
    with pytest.raises(ValidationError):
        BusinessProfile(state="   ", sector="Manufacturing")

    # Blank sector
    with pytest.raises(ValidationError):
        BusinessProfile(state="Uttar Pradesh", sector="")

    # Invalid project stage
    with pytest.raises(ValidationError):
        BusinessProfile(state="Uttar Pradesh", sector="Manufacturing", project_stage="InvalidStageXYZ")


# =====================================================================
# TEST 10: Document Deduplication
# =====================================================================
def test_document_deduplication(engine):
    profile = BusinessProfile(
        state="Uttar Pradesh",
        sector="Manufacturing",
        investment=50000000.0,
        employees=50,
        project_stage="Pre-Establishment",
        requires_fire_clearance=True,
    )
    summary = engine.analyze(profile)
    
    # Check that documents list has no duplicates (case-insensitive)
    lower_docs = [d.lower() for d in summary.documents]
    assert len(lower_docs) == len(set(lower_docs))
    assert len(summary.documents) > 0


# =====================================================================
# TEST 11: Prerequisite / Dependency Resolution
# =====================================================================
def test_dependency_resolution():
    # When both CTE and CTO are present, CTE must precede CTO
    candidate_ids = ["UP_PCB_CTO_002", "UP_PCB_CTE_001", "UP_FIRE_NOC_003"]
    ordered = resolve_dependencies(candidate_ids)
    
    assert ordered.index("UP_PCB_CTE_001") < ordered.index("UP_PCB_CTO_002")


# =====================================================================
# TEST 12: Determinism (Repeatability Guarantee)
# =====================================================================
def test_determinism(engine):
    profile = BusinessProfile(
        state="Uttar Pradesh",
        sector="Food Processing",
        investment=30000000.0,
        employees=60,
        project_stage="Pre-Operation",
        connected_load_kw=80.0,
        has_boiler=True,
        boiler_pressure=2.0,
        uses_water=True,
        generates_effluent=True,
        food_business=True,
    )

    # Run analysis multiple times
    result1 = engine.analyze(profile)
    result2 = engine.analyze(profile)

    # Assert exact match of outputs
    assert len(result1.potentially_applicable) == len(result2.potentially_applicable)
    for r1, r2 in zip(result1.potentially_applicable, result2.potentially_applicable):
        assert r1.approval_id == r2.approval_id
        assert r1.match_score == r2.match_score
        assert r1.status == r2.status
        assert r1.reasons == r2.reasons

    assert result1.documents == result2.documents
    assert result1.dependency_order == result2.dependency_order

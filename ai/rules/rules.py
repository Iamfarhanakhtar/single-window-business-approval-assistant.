"""
Deterministic Regulatory Rules and Matching Logic

Implements transparent, explainable scoring criteria for statutory approvals,
document aggregation, and dependency resolution.
"""

from typing import Dict, List, Tuple, Any, Optional, Set
from collections import deque
from ai.rules.models import (
    BusinessProfile,
    ApprovalStatus,
    EvaluationResult,
    DocumentItem,
    ProjectStage,
)

# Deterministic scoring weights (Total Max: 100 points)
WEIGHT_STATE = 30
WEIGHT_SECTOR = 30
WEIGHT_STAGE = 20
WEIGHT_CONDITION = 20

# Verified statutory dependencies explicitly supported by approvals.csv
# UP_PCB_CTO_002 requires valid Consent to Establish (UP_PCB_CTE_001) as per who_can_apply criteria.
RULE_DEPENDENCIES: Dict[str, List[str]] = {
    "UP_PCB_CTO_002": ["UP_PCB_CTE_001"],
}


def evaluate_state_match(profile: BusinessProfile, approval_state: str) -> Tuple[float, List[str], bool]:
    """
    Evaluates state jurisdiction match.
    Central approvals apply universally across states.
    """
    reasons = []
    app_state_lower = approval_state.strip().lower()
    prof_state_lower = profile.state.strip().lower()

    if app_state_lower in ("central", "all india", "national"):
        reasons.append(f"Central / National jurisdiction applies to {profile.state}")
        return WEIGHT_STATE, reasons, True

    if prof_state_lower == app_state_lower:
        reasons.append(f"State matches statutory jurisdiction: {approval_state}")
        return WEIGHT_STATE, reasons, True

    reasons.append(f"State mismatch: Approval is specific to '{approval_state}', but profile state is '{profile.state}'")
    return 0.0, reasons, False


def evaluate_sector_match(profile: BusinessProfile, approval_sector: str) -> Tuple[float, List[str], bool]:
    """
    Evaluates industry sector applicability.
    Recognizes sector hierarchy (e.g. Food Processing is an industrial manufacturing subsector).
    """
    reasons = []
    app_sec = approval_sector.strip().lower()
    prof_sec = profile.sector.strip().lower()

    if app_sec in ("general", "all sectors", "all"):
        reasons.append(f"Statutory clearance applies across general industrial sectors")
        return WEIGHT_SECTOR, reasons, True

    if prof_sec == app_sec:
        reasons.append(f"Sector exact match: {profile.sector}")
        return WEIGHT_SECTOR, reasons, True

    # Hierarchy: Food Processing units are classified under Manufacturing
    if prof_sec == "food processing" and app_sec == "manufacturing":
        reasons.append(f"Food Processing is classified as an agro-industrial subsector under Manufacturing")
        return WEIGHT_SECTOR, reasons, True

    # If profile is marked as food_business and approval is Food Processing
    if profile.food_business and app_sec == "food processing":
        reasons.append(f"Enterprise profile indicates active food business / processing operations")
        return WEIGHT_SECTOR, reasons, True

    reasons.append(f"Sector mismatch: Approval applies to '{approval_sector}', but profile sector is '{profile.sector}'")
    return 0.0, reasons, False


def evaluate_stage_match(profile: BusinessProfile, approval_stage: str) -> Tuple[float, List[str], bool]:
    """
    Evaluates project lifecycle stage match.
    """
    reasons = []
    if not profile.project_stage:
        reasons.append("Project stage not specified in profile; needs lifecycle stage verification")
        return WEIGHT_STAGE * 0.5, reasons, True  # Neutral partial credit

    prof_stage_lower = profile.project_stage.strip().lower()
    app_stage_lower = approval_stage.strip().lower()

    if prof_stage_lower == app_stage_lower:
        reasons.append(f"Project stage exact match: {approval_stage}")
        return WEIGHT_STAGE, reasons, True

    # Pre-Establishment is an antecedent requirement for Pre-Operation units
    if prof_stage_lower == "pre-operation" and app_stage_lower == "pre-establishment":
        reasons.append(f"Antecedent stage: '{approval_stage}' clearance typically required prior to '{profile.project_stage}'")
        return WEIGHT_STAGE * 0.5, reasons, True

    reasons.append(f"Stage difference: Approval applies to '{approval_stage}', current stage is '{profile.project_stage}'")
    return 0.0, reasons, False


def evaluate_explicit_conditions(
    profile: BusinessProfile,
    approval_id: str,
    approval_row: Dict[str, str]
) -> Tuple[float, List[str], Optional[bool]]:
    """
    Evaluates domain-specific statutory conditions present in approvals.csv.
    Returns (score, reasons, hard_mismatch_flag).
    hard_mismatch_flag = True if condition explicitly disqualifies the approval.
    """
    reasons = []
    score = 0.0

    # 1. UP_PCB_CTE_001 (Consent to Establish)
    if approval_id == "UP_PCB_CTE_001":
        if profile.uses_water or profile.generates_effluent or profile.generates_hazardous_waste:
            score = WEIGHT_CONDITION
            reasons.append("Profile indicates trade effluent, water consumption, or industrial emissions requiring CTE")
        elif profile.sector.lower() in ("manufacturing", "food processing"):
            score = WEIGHT_CONDITION * 0.75
            reasons.append("Industrial manufacturing unit typically requires CTE clearance under Water/Air Acts")
        else:
            score = WEIGHT_CONDITION * 0.5
            reasons.append("Requires verification of environmental pollution category (Red/Orange/Green)")
        return score, reasons, None

    # 2. UP_PCB_CTO_002 (Consent to Operate)
    elif approval_id == "UP_PCB_CTO_002":
        if profile.project_stage and profile.project_stage.lower() == "pre-operation":
            score = WEIGHT_CONDITION
            reasons.append("Pre-Operation stage requires operational consent prior to commercial production")
        else:
            score = WEIGHT_CONDITION * 0.5
            reasons.append("Requires verification of plant construction completion status")
        return score, reasons, None

    # 3. UP_FIRE_NOC_003 (Fire Safety NOC)
    elif approval_id == "UP_FIRE_NOC_003":
        if profile.requires_fire_clearance is True:
            score = WEIGHT_CONDITION
            reasons.append("Profile explicitly flags requirement for fire safety NOC")
        elif profile.investment >= 10_000_000 or profile.employees >= 50 or profile.generates_hazardous_waste:
            score = WEIGHT_CONDITION
            reasons.append("Scale of investment / workforce / industrial risk triggers Fire Safety NOC requirement")
        elif profile.requires_fire_clearance is False:
            score = 0.0
            reasons.append("Fire safety clearance explicitly marked as not required")
            return score, reasons, True  # Hard mismatch
        else:
            score = WEIGHT_CONDITION * 0.5
            reasons.append("Requires verification of physical built-up area and hazardous material storage thresholds")
        return score, reasons, None

    # 4. IN_FSSAI_MFG_004 (FSSAI Food License)
    elif approval_id == "IN_FSSAI_MFG_004":
        if profile.food_business or profile.sector.lower() == "food processing":
            score = WEIGHT_CONDITION
            reasons.append("Food Business Operator (FBO) profile directly triggers mandatory FSSAI food licensing")
            return score, reasons, None
        else:
            reasons.append("Non-food enterprise profile; FSSAI food processing license not applicable")
            return 0.0, reasons, True  # Hard mismatch

    # 5. UP_FAC_REG_005 (Factory License)
    elif approval_id == "UP_FAC_REG_005":
        if profile.employees >= 10 and profile.connected_load_kw > 0:
            score = WEIGHT_CONDITION
            reasons.append(f"Workforce of {profile.employees} (>= 10 with power) triggers statutory Factory Act registration")
        elif profile.employees >= 20:
            score = WEIGHT_CONDITION
            reasons.append(f"Workforce of {profile.employees} (>= 20) triggers statutory Factory Act registration")
        elif 0 < profile.employees < 10:
            score = WEIGHT_CONDITION * 0.25
            reasons.append(f"Workforce count ({profile.employees}) is below 10 threshold; factory license may not trigger unless expansion planned")
        else:
            score = WEIGHT_CONDITION * 0.5
            reasons.append("Workforce count not specified; requires verification against Factory Act thresholds")
        return score, reasons, None

    # 6. UP_LAB_REG_006 (Contract Labour Registration)
    elif approval_id == "UP_LAB_REG_006":
        if profile.contract_workers_count >= 20:
            score = WEIGHT_CONDITION
            reasons.append(f"Engaging {profile.contract_workers_count} contract workers (>= 20) triggers mandatory principal employer registration")
        elif profile.employees >= 20:
            score = WEIGHT_CONDITION * 0.75
            reasons.append(f"Total workforce of {profile.employees} (>= 20); applicable if 20 or more are contract labourers")
        else:
            score = WEIGHT_CONDITION * 0.25
            reasons.append("Contract worker count below 20 threshold or not indicated in profile")
        return score, reasons, None

    # 7. UP_ELEC_CEIG_007 (Electrical Safety CEIG)
    elif approval_id == "UP_ELEC_CEIG_007":
        if profile.connected_load_kw >= 50:
            score = WEIGHT_CONDITION
            reasons.append(f"Connected electrical load of {profile.connected_load_kw} kW (>= 50 kW) triggers CEIG safety inspection")
        elif profile.connected_load_kw > 0:
            score = WEIGHT_CONDITION * 0.5
            reasons.append(f"Connected load is {profile.connected_load_kw} kW (< 50 kW); CEIG required only if installing HT transformer/DG set")
        else:
            score = WEIGHT_CONDITION * 0.5
            reasons.append("Connected electrical load unspecified; requires verification")
        return score, reasons, None

    # 8. IN_BOILER_REG_008 (Boiler Registration)
    elif approval_id == "IN_BOILER_REG_008":
        if profile.has_boiler or profile.boiler_pressure > 1.0:
            score = WEIGHT_CONDITION
            reasons.append(f"Industrial steam boiler present (pressure: {profile.boiler_pressure} kg/cm2) triggering Boilers Act inspection")
            return score, reasons, None
        else:
            reasons.append("No industrial steam boiler indicated in business profile")
            return 0.0, reasons, True  # Hard mismatch

    # 9. IN_WEIGHTS_MEAS_009 (Legal Metrology Pre-Packaged)
    elif approval_id == "IN_WEIGHTS_MEAS_009":
        if profile.food_business or profile.sector.lower() == "food processing":
            score = WEIGHT_CONDITION
            reasons.append("Food manufacturing / consumer goods packaging requires Legal Metrology pre-packed registration")
        else:
            score = WEIGHT_CONDITION * 0.5
            reasons.append("Requires verification if industrial products are packaged in pre-determined retail quantities")
        return score, reasons, None

    # 10. UP_TREE_TRANS_010 (Tree Felling Permission)
    elif approval_id == "UP_TREE_TRANS_010":
        if profile.tree_felling_required is True:
            score = WEIGHT_CONDITION
            reasons.append("Site development explicitly requires clearing protected tree species")
            return score, reasons, None
        elif profile.tree_felling_required is False:
            reasons.append("No tree felling required on industrial plot")
            return 0.0, reasons, True  # Hard mismatch
        else:
            # Default for land/tree clearance: cannot decide without site inspection
            score = WEIGHT_CONDITION * 0.5
            reasons.append("Requires verification of physical plot site conditions and presence of protected trees")
            return score, reasons, None

    # Fallback for generic / extensible approvals
    score = WEIGHT_CONDITION * 0.5
    reasons.append("Standard statutory parameters evaluated")
    return score, reasons, None


def evaluate_approval(
    profile: BusinessProfile,
    approval_row: Dict[str, str]
) -> EvaluationResult:
    """
    Deterministically evaluates a single approval against the business profile.
    Produces a transparent match score and structured reasons.
    """
    approval_id = approval_row.get("approval_id", "").strip()
    approval_name = approval_row.get("approval_name", "").strip()
    authority = approval_row.get("authority", "").strip()
    state = approval_row.get("state", "").strip()
    sector = approval_row.get("sector", "").strip()
    stage = approval_row.get("stage", "").strip()
    source_url = approval_row.get("source_url", "").strip()
    statutory_act = approval_row.get("act_rules", "").strip()
    
    raw_days = approval_row.get("processing_days", "").strip()
    processing_days = int(raw_days) if raw_days.isdigit() else None

    # 1. State evaluation
    state_score, state_reasons, state_matched = evaluate_state_match(profile, state)

    # 2. Sector evaluation
    sector_score, sector_reasons, sector_matched = evaluate_sector_match(profile, sector)

    # 3. Stage evaluation
    stage_score, stage_reasons, _ = evaluate_stage_match(profile, stage)

    # 4. Explicit condition evaluation
    cond_score, cond_reasons, hard_mismatch = evaluate_explicit_conditions(profile, approval_id, approval_row)

    total_score = state_score + sector_score + stage_score + cond_score
    normalized_score = round(total_score / 100.0, 2)

    all_reasons = state_reasons + sector_reasons + stage_reasons + cond_reasons

    # Extract required documents
    docs_raw = approval_row.get("documents", "")
    documents = [d.strip() for d in docs_raw.split(";") if d.strip()] if docs_raw else []

    # Deterministic Status Decision Logic
    requires_verif = False

    if hard_mismatch is True or not state_matched or not sector_matched:
        status = ApprovalStatus.NOT_MATCHED
    elif approval_id == "UP_TREE_TRANS_010" and profile.tree_felling_required is None:
        status = ApprovalStatus.REQUIRES_VERIFICATION
        requires_verif = True
    elif normalized_score >= 0.70:
        status = ApprovalStatus.POTENTIALLY_APPLICABLE
    elif normalized_score >= 0.40:
        status = ApprovalStatus.PARTIALLY_MATCHED
        requires_verif = True
    else:
        status = ApprovalStatus.NOT_MATCHED

    return EvaluationResult(
        approval_id=approval_id,
        approval_name=approval_name,
        authority=authority,
        status=status,
        match_score=normalized_score,
        reasons=all_reasons,
        documents=documents,
        source_url=source_url,
        requires_verification=requires_verif or (status == ApprovalStatus.REQUIRES_VERIFICATION),
        statutory_act=statutory_act,
        processing_days=processing_days,
    )


def get_required_documents(results: List[EvaluationResult]) -> List[str]:
    """
    Extracts and deduplicates documents required by applicable/matched approvals.
    Preserves first-seen order.
    """
    seen: Set[str] = set()
    deduped: List[str] = []

    for res in results:
        if res.status in (ApprovalStatus.POTENTIALLY_APPLICABLE, ApprovalStatus.PARTIALLY_MATCHED):
            for doc in res.documents:
                clean_doc = doc.strip()
                if clean_doc and clean_doc.lower() not in seen:
                    seen.add(clean_doc.lower())
                    deduped.append(clean_doc)
    return deduped


def get_detailed_documents(results: List[EvaluationResult]) -> List[DocumentItem]:
    """
    Returns document items tracking their source statutory approval.
    """
    detailed: List[DocumentItem] = []
    for res in results:
        if res.status in (ApprovalStatus.POTENTIALLY_APPLICABLE, ApprovalStatus.PARTIALLY_MATCHED):
            for doc in res.documents:
                clean_doc = doc.strip()
                if clean_doc:
                    detailed.append(
                        DocumentItem(
                            name=clean_doc,
                            source_approval_id=res.approval_id,
                            source_approval_name=res.approval_name,
                        )
                    )
    return detailed


def resolve_dependencies(applicable_approval_ids: List[str]) -> List[str]:
    """
    Resolves statutory prerequisite relationships into a topological execution order.
    Safely handles circular dependencies and missing prerequisites.
    """
    app_set = set(applicable_approval_ids)
    in_degree: Dict[str, int] = {aid: 0 for aid in app_set}
    graph: Dict[str, List[str]] = {aid: [] for aid in app_set}

    for target_id, prereqs in RULE_DEPENDENCIES.items():
        if target_id in app_set:
            for prereq in prereqs:
                if prereq in app_set:
                    graph[prereq].append(target_id)
                    in_degree[target_id] += 1

    # Kahn's Algorithm for Topological Sort
    queue = deque([aid for aid, deg in in_degree.items() if deg == 0])
    ordered: List[str] = []

    while queue:
        current = queue.popleft()
        ordered.append(current)
        for neighbor in graph.get(current, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # In case of cycle or orphaned nodes, append remaining
    for aid in applicable_approval_ids:
        if aid not in ordered:
            ordered.append(aid)

    return ordered

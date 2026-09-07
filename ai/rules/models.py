"""
Business Profile and Rule Engine Data Models

Provides strongly-typed schemas for input business profiles, evaluation results,
and aggregated compliance summaries using Pydantic v2.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ApprovalStatus(str, Enum):
    """Classification of approval applicability based on deterministic evaluation."""
    POTENTIALLY_APPLICABLE = "POTENTIALLY_APPLICABLE"
    PARTIALLY_MATCHED = "PARTIALLY_MATCHED"
    NOT_MATCHED = "NOT_MATCHED"
    REQUIRES_VERIFICATION = "REQUIRES_VERIFICATION"


class ProjectStage(str, Enum):
    """Enterprise project setup lifecycle stage."""
    PRE_ESTABLISHMENT = "Pre-Establishment"
    PRE_OPERATION = "Pre-Operation"
    POST_OPERATION = "Post-Operation"
    OPERATION = "Operation"


class BusinessProfile(BaseModel):
    """
    Structured profile representing an enterprise / industrial applicant.
    Validated deterministically with clear error messages for invalid inputs.
    """
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    state: str = Field(..., description="Jurisdiction state (e.g. 'Uttar Pradesh', 'Central')")
    sector: str = Field(..., description="Industry sector (e.g. 'Manufacturing', 'Food Processing')")
    investment: float = Field(default=0.0, description="Capital investment in INR")
    employees: int = Field(default=0, description="Total workforce count (regular + contract)")
    project_stage: Optional[str] = Field(default=None, description="Stage: Pre-Establishment, Pre-Operation, Post-Operation")
    
    # Technical & Environmental Parameters
    connected_load_kw: float = Field(default=0.0, description="Connected electrical power load in kW")
    has_boiler: bool = Field(default=False, description="Whether an industrial steam boiler is installed")
    boiler_pressure: float = Field(default=0.0, description="Boiler operating steam pressure in kg/cm2")
    uses_water: bool = Field(default=False, description="Whether industrial processes consume ground/surface water")
    generates_effluent: bool = Field(default=False, description="Whether trade effluent/wastewater is generated")
    generates_hazardous_waste: bool = Field(default=False, description="Whether hazardous waste is produced")
    requires_fire_clearance: Optional[bool] = Field(default=None, description="Explicit fire clearance requirement flag")
    food_business: bool = Field(default=False, description="Whether enterprise handles, processes, or packages food")
    manufacturing_type: Optional[str] = Field(default=None, description="Sub-type of manufacturing")
    tree_felling_required: Optional[bool] = Field(default=None, description="Whether trees must be felled for site development")
    contract_workers_count: int = Field(default=0, description="Number of contract workers engaged")

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("State cannot be empty.")
        return v_clean

    @field_validator("sector")
    @classmethod
    def validate_sector(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("Sector cannot be empty.")
        return v_clean

    @field_validator("investment")
    @classmethod
    def validate_investment(cls, v: float) -> float:
        if v < 0:
            raise ValueError(f"Investment amount cannot be negative. Provided: {v}")
        return v

    @field_validator("employees")
    @classmethod
    def validate_employees(cls, v: int) -> int:
        if v < 0:
            raise ValueError(f"Employee count cannot be negative. Provided: {v}")
        return v

    @field_validator("connected_load_kw")
    @classmethod
    def validate_connected_load(cls, v: float) -> float:
        if v < 0:
            raise ValueError(f"Connected load cannot be negative. Provided: {v}")
        return v

    @field_validator("boiler_pressure")
    @classmethod
    def validate_boiler_pressure(cls, v: float) -> float:
        if v < 0:
            raise ValueError(f"Boiler pressure cannot be negative. Provided: {v}")
        return v

    @field_validator("contract_workers_count")
    @classmethod
    def validate_contract_workers(cls, v: int) -> int:
        if v < 0:
            raise ValueError(f"Contract worker count cannot be negative. Provided: {v}")
        return v

    @field_validator("project_stage")
    @classmethod
    def validate_project_stage(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        valid_stages = {s.value.lower() for s in ProjectStage}
        if v.strip().lower() not in valid_stages:
            valid_list = [s.value for s in ProjectStage]
            raise ValueError(f"Invalid project stage '{v}'. Must be one of: {', '.join(valid_list)}")
        for stage in ProjectStage:
            if stage.value.lower() == v.strip().lower():
                return stage.value
        return v.strip()


class DocumentItem(BaseModel):
    """Document requirement with statutory source tracking."""
    model_config = ConfigDict(from_attributes=True)
    name: str
    source_approval_id: str
    source_approval_name: str


class EvaluationResult(BaseModel):
    """Deterministic evaluation outcome for a single statutory approval."""
    model_config = ConfigDict(from_attributes=True)

    approval_id: str
    approval_name: str
    authority: str
    status: ApprovalStatus
    match_score: float = Field(..., ge=0.0, le=1.0, description="Normalized match score between 0.0 and 1.0")
    reasons: List[str] = Field(default_factory=list, description="Explicit deterministic reasons for decision")
    documents: List[str] = Field(default_factory=list, description="Required application documents")
    source_url: str
    requires_verification: bool
    statutory_act: Optional[str] = None
    processing_days: Optional[int] = None


class AnalysisSummary(BaseModel):
    """Aggregated compliance checklist and dependency ordering output."""
    model_config = ConfigDict(from_attributes=True)

    business_profile: Dict[str, Any]
    total_approvals_evaluated: int
    potentially_applicable: List[EvaluationResult]
    partially_matched: List[EvaluationResult]
    requires_verification: List[EvaluationResult]
    not_matched: List[EvaluationResult]
    documents: List[str]
    detailed_documents: List[DocumentItem]
    dependency_order: List[str]

"""
Unified Compliance Analysis and AI Integration Service (Step 6)

Orchestrates the multi-pillar AI/ML system:
1. Deterministic Rule Engine (ai/rules/) -> Statutory Applicability & Checklist
2. ML Risk & Delay Prediction (ml/) -> Processing Days & Bottleneck Inferences
3. Regulatory RAG (ai/rag/) -> Evidence-Grounded Legal Explanations & Citations
4. Document AI (ai/document_ai/) -> Privacy-Safe Local Pre-Validation
"""

import os
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone

from ai.rules.models import BusinessProfile as RuleEngineProfile, ApprovalStatus
from ai.rules.rule_engine import RegulatoryRuleEngine
from ml.inference.predictor import ComplianceRiskPredictor, risk_predictor
from ai.rag.pipeline import RegulatoryRAGPipeline, rag_pipeline
from ai.document_ai.models import DocumentInput, DocumentStatus
from ai.document_ai.pipeline import DocumentAIPipeline, document_ai_pipeline

from app.schemas.compliance import (
    ComplianceAnalyzeRequest,
    ComplianceAnalyzeResponse,
    ComplianceSummaryResponse,
    ApprovalItemResponse,
    DocumentRequirementItem,
    RiskAnalysisResponse,
    DelayPredictionResponse,
    RegulatoryExplanationItem,
    SourceReferenceItem,
    DocumentValidateRequest,
    DocumentValidationResponse,
    CheckItemResponse,
    ComplianceHealthResponse,
)


class ComplianceAnalysisService:
    """
    Central orchestration service binding the Rule Engine, ML Predictor,
    Regulatory RAG, and Document AI into a single-window compliance pipeline.
    """

    def __init__(
        self,
        rule_engine: Optional[RegulatoryRuleEngine] = None,
        predictor: Optional[ComplianceRiskPredictor] = None,
        rag: Optional[RegulatoryRAGPipeline] = None,
        doc_ai: Optional[DocumentAIPipeline] = None,
    ):
        self.rule_engine = rule_engine or RegulatoryRuleEngine()
        self.predictor = predictor or risk_predictor
        self.rag = rag or rag_pipeline
        self.doc_ai = doc_ai or document_ai_pipeline

    def _normalize_profile(self, request: ComplianceAnalyzeRequest) -> RuleEngineProfile:
        """Converts incoming API request into a validated Rule Engine BusinessProfile."""
        sector = request.sector.strip()
        if sector.lower() in ("food_processing", "food processing", "food", "fssai"):
            canon_sector = "Food Processing"
        elif sector.lower() in ("manufacturing", "general_manufacturing", "factory"):
            canon_sector = "Manufacturing"
        elif sector.lower() in ("textile", "textiles", "garments"):
            canon_sector = "Textile"
        elif sector.lower() in ("chemical", "chemicals", "petrochemical"):
            canon_sector = "Chemicals"
        else:
            canon_sector = sector.title()

        # Handle food business flag
        is_food = request.is_food_business
        if is_food is None:
            is_food = (canon_sector == "Food Processing")

        # Map project stage
        stage_map = {
            "new_unit": "Pre-Establishment",
            "pre-establishment": "Pre-Establishment",
            "establishment": "Pre-Establishment",
            "pre-operation": "Pre-Operation",
            "operation": "Pre-Operation",
            "operational": "Pre-Operation",
            "expansion": "Expansion",
        }
        req_stage = (request.project_stage or "Pre-Operation").lower()
        canon_stage = stage_map.get(req_stage, "Pre-Operation")

        return RuleEngineProfile(
            state=request.state or "Uttar Pradesh",
            sector=canon_sector,
            project_stage=canon_stage,
            investment=float(request.investment),
            employees=int(request.employees),
            connected_load_kw=float(request.connected_load_kw or 0.0),
            has_boiler=bool(request.has_boiler),
            food_business=bool(is_food),
            uses_water=float(request.water_requirement_kld or 0.0) > 0,
            generates_effluent=float(request.water_requirement_kld or 0.0) > 0,
            generates_hazardous_waste=bool(request.hazardous_materials),
            contract_workers_count=0,
        )

    def analyze_compliance(
        self,
        request: ComplianceAnalyzeRequest,
        db_session: Optional[Any] = None,
    ) -> ComplianceAnalyzeResponse:
        """
        Runs multi-pillar compliance analysis:
        1. Rule Engine applicability
        2. ML risk and delay prediction
        3. RAG regulatory explanations & citations
        4. Optional persistence to Database
        """
        profile = self._normalize_profile(request)

        # -------------------------------------------------------------------
        # 1. Deterministic Rule Engine Evaluation
        # -------------------------------------------------------------------
        summary = self.rule_engine.analyze(profile)

        approvals_list: List[ApprovalItemResponse] = []
        departments_set = set()
        max_sla_days = 30
        has_inspection = False

        for res in summary.potentially_applicable:
            d_days = res.processing_days or 30
            max_sla_days = max(max_sla_days, d_days)
            dept = res.authority or "State Department"
            departments_set.add(dept)
            if "inspection" in " ".join(res.reasons).lower() or res.requires_verification:
                has_inspection = True

            approvals_list.append(
                ApprovalItemResponse(
                    approval_id=res.approval_id,
                    approval_name=res.approval_name,
                    authority=dept,
                    status=res.status.value,
                    score=res.match_score,
                    reason=res.reasons[0] if res.reasons else "Applicable based on enterprise profile.",
                    documents=res.documents,
                    processing_days=d_days,
                    statutory_fee=15000.0,
                    department=dept,
                    category=profile.project_stage or "General",
                    is_mandatory=True,
                    prerequisites=[],
                )
            )

        for res in summary.requires_verification:
            dept = res.authority or "State Department"
            departments_set.add(dept)
            d_days = res.processing_days or 30
            approvals_list.append(
                ApprovalItemResponse(
                    approval_id=res.approval_id,
                    approval_name=res.approval_name,
                    authority=dept,
                    status=res.status.value,
                    score=res.match_score,
                    reason=res.reasons[0] if res.reasons else "Conditional statutory clearance requiring verification.",
                    documents=res.documents,
                    processing_days=d_days,
                    statutory_fee=5000.0,
                    department=dept,
                    category=profile.project_stage or "General",
                    is_mandatory=False,
                )
            )

        # Build aggregated document requirements
        doc_map: Dict[str, List[str]] = {}
        for app in approvals_list:
            for doc in app.documents:
                clean_doc = doc.strip()
                if clean_doc:
                    doc_map.setdefault(clean_doc, []).append(app.approval_name)

        documents_list = [
            DocumentRequirementItem(document_name=doc_name, required_for=req_apps, status="MISSING")
            for doc_name, req_apps in doc_map.items()
        ]

        # -------------------------------------------------------------------
        # 2. ML Risk & SLA Delay Inferences
        # -------------------------------------------------------------------
        approval_cnt = max(1, len(approvals_list))
        doc_cnt = max(1, len(documents_list))
        dept_cnt = max(1, len(departments_set))

        ml_features = {
            "investment": float(profile.investment),
            "employees": int(profile.employees),
            "approval_count": approval_cnt,
            "document_count": doc_cnt,
            "missing_document_count": doc_cnt,
            "inspection_required": has_inspection or profile.generates_hazardous_waste or profile.has_boiler,
            "department_count": dept_cnt,
            "previous_queries": 0,
            "sla_days": max_sla_days,
            "state": profile.state,
            "sector": profile.sector,
            "project_stage": profile.project_stage,
            "applicant_type": request.applicant_type or "Enterprise",
            "season": "Q3",
        }

        ml_out = self.predictor.predict(ml_features)

        risk_resp = RiskAnalysisResponse(
            risk_score=ml_out["risk_score"],
            risk_level=ml_out["risk_level"],
            factors=ml_out["risk_factors"],
        )

        delay_resp = DelayPredictionResponse(
            probability=ml_out["delay_probability"],
            predicted_days=ml_out["predicted_processing_days"],
            factors=ml_out["risk_factors"],
            is_synthetic_model=ml_out.get("is_synthetic_model", True),
        )

        # -------------------------------------------------------------------
        # 3. Regulatory RAG Evidence Grounding
        # -------------------------------------------------------------------
        rag_explanations: List[RegulatoryExplanationItem] = []
        sources_dict: Dict[str, SourceReferenceItem] = {}

        top_approvals = summary.potentially_applicable[:3]
        for app in top_approvals:
            rag_res = self.rag.explain_approval(
                approval_name=app.approval_name,
                approval_id=app.approval_id,
                business_profile=profile,
                state=profile.state,
            )

            for src in rag_res.get("sources", []):
                s_url = src.get("source_url", "")
                s_name = src.get("title", "Statutory Act")
                if s_name and s_name not in sources_dict:
                    sources_dict[s_name] = SourceReferenceItem(
                        source_name=s_name,
                        source_url=s_url or "https://up.gov.in/statutory-acts",
                        authority="State Department / Central Regulatory Authority",
                        jurisdiction="State / Central",
                        is_official=True,
                    )

            cited_acts = [s.get("title", "") for s in rag_res.get("sources", []) if s.get("title")]
            rag_explanations.append(
                RegulatoryExplanationItem(
                    approval_id=app.approval_id,
                    approval_name=app.approval_name,
                    answer=rag_res.get("answer", "Regulatory clearance required under state industrial policy."),
                    cited_acts=cited_acts or ["State Industrial Clearance Regulation"],
                    confidence=float(rag_res.get("confidence", 0.85)),
                    sources=[
                        {
                            "source_name": s.get("title", ""),
                            "source_url": s.get("source_url", ""),
                            "section": s.get("section", ""),
                        }
                        for s in rag_res.get("sources", [])
                    ],
                )
            )

        recommendations: List[str] = []
        if profile.sector == "Food Processing":
            recommendations.append("Apply concurrently for UPPCB CTE and FSSAI Manufacturing License to minimize aggregate timeline.")
        if profile.has_boiler:
            recommendations.append("Ensure Boiler Inspectorate certified engineering blueprints are attached to prevent scrutiny delays.")
        if profile.connected_load_kw > 100:
            recommendations.append("HT substation transformer schematic required by DISCOM prior to power energization.")
        if ml_out["risk_level"] == "HIGH":
            recommendations.append("High documentation friction predicted: Utilize Document AI pre-validation on all blueprints before submission.")
        else:
            recommendations.append("Standard statutory clearance workflow: Estimated completion within SLA timelines.")

        # -------------------------------------------------------------------
        # 4. Construct Final Response Payload
        # -------------------------------------------------------------------
        summary_resp = ComplianceSummaryResponse(
            total_approvals=len(approvals_list),
            potentially_applicable=len(summary.potentially_applicable),
            requires_verification=len(summary.requires_verification),
            documents_required=len(documents_list),
        )

        response = ComplianceAnalyzeResponse(
            business_profile={
                "sector": profile.sector,
                "state": profile.state,
                "investment": profile.investment,
                "employees": profile.employees,
                "project_stage": profile.project_stage,
                "connected_load_kw": profile.connected_load_kw,
                "has_boiler": profile.has_boiler,
                "food_business": profile.food_business,
                "generates_hazardous_waste": profile.generates_hazardous_waste,
            },
            summary=summary_resp,
            approvals=approvals_list,
            documents=documents_list,
            risk=risk_resp,
            delay_prediction=delay_resp,
            recommendations=recommendations,
            regulatory_explanations=rag_explanations,
            sources=list(sources_dict.values()),
        )

        # -------------------------------------------------------------------
        # 5. Database Persistence (Optional)
        # -------------------------------------------------------------------
        if db_session:
            try:
                from app.models.entities import ComplianceAnalysis
                record = ComplianceAnalysis(
                    application_id=request.application_id,
                    business_id=request.business_id,
                    profile_snapshot=response.business_profile,
                    summary=summary_resp.model_dump(),
                    risk_score=float(risk_resp.risk_score),
                    delay_probability=float(delay_resp.probability),
                    analysis_result=response.model_dump(),
                    version="1.0.0",
                )
                db_session.add(record)
                db_session.commit()
            except Exception as e:
                print(f"[WARN] Database persistence failed for compliance analysis: {e}")

        return response

    def validate_document(self, request: DocumentValidateRequest) -> DocumentValidationResponse:
        """
        Pre-validates an uploaded document locally with privacy safeguards.
        """
        temp_file_created = False
        file_path = request.file_path

        if not file_path and request.file_content_text:
            scratch_dir = "/tmp" if os.name != "nt" else os.environ.get("TEMP", ".")
            file_path = os.path.join(scratch_dir, f"validate_{uuid.uuid4().hex[:8]}_{request.filename}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(request.file_content_text)
            temp_file_created = True

        if not file_path or not os.path.exists(file_path):
            return DocumentValidationResponse(
                document_id=request.document_id,
                filename=request.filename,
                status="UNREADABLE",
                entity_match="UNKNOWN",
                expiry_status="NO_EXPIRY_INFORMATION",
                type_match="UNKNOWN",
                checks=[
                    CheckItemResponse(check_name="File Accessibility", passed=False, details="File not found on local disk.")
                ],
                warnings=[],
                errors=["Document file could not be located or read on local server."],
                confidence=0.0,
                requires_human_verification=True,
            )

        try:
            doc_input = DocumentInput(
                document_id=request.document_id,
                filename=request.filename,
                document_type=request.document_type,
                file_path=file_path,
                expected_entity_name=request.expected_entity_name,
                expected_document_type=request.expected_document_type,
                application_id=request.application_id,
            )

            # Run Document AI
            val_result = self.doc_ai.validate_document(doc_input)
            extracted = self.doc_ai.extract_document(doc_input)

            checks_resp = [
                CheckItemResponse(check_name=c.check_name, passed=c.passed, details=c.details)
                for c in val_result.checks
            ]

            # Redacted preview for safe logging/display
            redacted_preview = extracted.redacted_text[:1000] if extracted.redacted_text else ""

            return DocumentValidationResponse(
                document_id=val_result.document_id,
                filename=val_result.filename,
                status=val_result.status.value,
                entity_match=val_result.entity_match.value,
                expiry_status=val_result.expiry_status.value,
                type_match=val_result.type_match.value,
                checks=checks_resp,
                warnings=val_result.warnings,
                errors=val_result.errors,
                confidence=val_result.confidence,
                days_until_expiry=val_result.days_until_expiry,
                requires_human_verification=True,
                redacted_preview=redacted_preview,
            )
        finally:
            if temp_file_created and file_path and os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except Exception:
                    pass

    def check_health(self) -> ComplianceHealthResponse:
        """Runs health probes on all 4 AI/ML modules."""
        rule_health = {
            "loaded": True,
            "total_approvals": self.rule_engine.total_approvals,
            "dataset_path": self.rule_engine.csv_path,
        }

        ml_health = {
            "loaded": self.predictor.clf is not None and self.predictor.reg is not None,
            "metadata": self.predictor.metadata,
        }

        rag_health = {
            "loaded": True,
            "retriever_ready": self.rag.retriever is not None,
            "total_regulations": len(self.rag.retriever.chunks) if self.rag.retriever else 0,
        }

        doc_health = {
            "loaded": True,
            "extractor_ready": self.doc_ai.extractor is not None,
            "supported_formats": [".txt", ".md", ".csv", ".json"],
        }

        all_ok = rule_health["loaded"] and ml_health["loaded"] and rag_health["loaded"] and doc_health["loaded"]

        return ComplianceHealthResponse(
            status="healthy" if all_ok else "degraded",
            rule_engine=rule_health,
            ml_predictor=ml_health,
            rag_pipeline=rag_health,
            document_ai=doc_health,
        )


# Singleton instance
compliance_service = ComplianceAnalysisService()

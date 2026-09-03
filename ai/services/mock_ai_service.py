"""Mock AI & ML Implementation for Foundation Testing (Synthetic Rule & Heuristic Engine)"""
from typing import List
from ai.services.ai_service_interface import AIServiceInterface
from app.schemas.domain import (
    AnalyzeBusinessRequest,
    AnalyzeBusinessResponse,
    ApplicableApprovalItem,
    PredictDelayRequest,
    PredictDelayResponse,
    PredictClarificationRequest,
    PredictClarificationResponse,
    ValidateDocRequest,
    ValidateDocResponse,
    AskRAGRequest,
    AskRAGResponse
)

class MockAIService(AIServiceInterface):
    """
    Simulates RAG, rule engine, and ML predictions with deterministic heuristics
    for development, testing, and UI integration.
    """

    def analyze_business(self, request: AnalyzeBusinessRequest) -> AnalyzeBusinessResponse:
        sector_lower = request.sector.lower()
        state = request.location
        investment = request.investment
        employees = request.employees

        approvals: List[ApplicableApprovalItem] = []
        docs: List[str] = ["Certificate of Incorporation / PAN", "Authorized Signatory ID", "Land Ownership / Lease Deed"]
        incentives: List[str] = []

        # Deterministic Rules
        # 1. Fire NOC
        if investment > 10000000 or employees > 20 or "food" in sector_lower or "chemical" in sector_lower:
            approvals.append(ApplicableApprovalItem(
                code="FIRE_NOC",
                name="Fire Safety NOC (Form-B)",
                department="State Fire Prevention Service",
                category="Safety",
                sla_days=15,
                fee=5000.0,
                mandatory=True,
                prerequisites=[]
            ))
            docs.append("Building Layout Plan & Fire Safety Evacuation Map")

        # 2. PCB Consent (CTE)
        if "food" in sector_lower or "chemical" in sector_lower or "textile" in sector_lower or "manufacturing" in sector_lower:
            approvals.append(ApplicableApprovalItem(
                code="PCB_CTE",
                name="Consent to Establish (CTE - Orange Category)",
                department="State Pollution Control Board",
                category="Environmental",
                sla_days=30,
                fee=25000.0,
                mandatory=True,
                prerequisites=[]
            ))
            docs.extend(["Effluent Treatment Plant (ETP) Scheme", "Water Balance Diagram"])

        # 3. FSSAI License
        if "food" in sector_lower or "beverage" in sector_lower:
            approvals.append(ApplicableApprovalItem(
                code="FSSAI_MFG",
                name="FSSAI Central/State Food Manufacturing License",
                department="Food Safety and Standards Authority",
                category="Operational",
                sla_days=21,
                fee=7500.0,
                mandatory=True,
                prerequisites=["PCB_CTE"]
            ))
            docs.extend(["FSMS Plan / Food Safety Blueprint", "Water Potability Test Report"])

        # 4. Factories Act License
        if employees >= 10:
            approvals.append(ApplicableApprovalItem(
                code="FACTORY_LIC",
                name="Factory Registration & Plan Approval",
                department="Directorate of Factories & Boilers",
                category="Labor & Operational",
                sla_days=20,
                fee=10000.0,
                mandatory=True,
                prerequisites=["FIRE_NOC"]
            ))
            docs.append("Machinery Layout & Power Load Sanction Letter")

        # 5. Incentives
        if investment >= 50000000:
            incentives.append("UP Industrial Investment & Employment Promotion Policy (25% Capital Subsidy)")
            incentives.append("PM Formalisation of Micro food processing Enterprises Scheme (PMFME)")

        # Risk & Delay Estimation
        risk_score = 0.22
        delay_prob = 0.35
        if len(approvals) >= 4:
            risk_score = 0.38
            delay_prob = 0.42

        return AnalyzeBusinessResponse(
            applicable_approvals=approvals,
            required_documents=list(set(docs)),
            risk_score=risk_score,
            delay_probability=delay_prob,
            predicted_processing_days=38,
            eligible_incentives=incentives,
            explanation=f"Based on sector '{request.sector}', {employees} workers, and ₹{investment/10000000:.2f} Cr investment in {state}, statutory rules mandate {len(approvals)} core departmental clearances. Parallel processing can compress total timeline from 86 to 38 calendar days."
        )

    def predict_delay(self, request: PredictDelayRequest) -> PredictDelayResponse:
        expected_days = 6
        delay_probability = 0.28
        factors = []

        if request.has_hazardous:
            delay_probability += 0.35
            expected_days += 12
            factors.append("Hazardous material clearance requires inter-agency expert committee review")
        
        if request.document_count < 4:
            delay_probability += 0.25
            expected_days += 7
            factors.append("Incomplete initial document bundle increases query generation probability")

        return PredictDelayResponse(
            delay_probability=min(delay_probability, 0.95),
            expected_delay_days=expected_days,
            risk_factors=factors or ["Standard inter-departmental inspection coordination overhead"],
            recommendation="Pre-validate Water Balance Diagram and Fire Egress schematics prior to final submission to eliminate 85% of standard queries."
        )

    def predict_clarification(self, request: PredictClarificationRequest) -> PredictClarificationResponse:
        prob = 0.15
        deficiencies = []
        if request.missing_doc_types:
            prob = 0.75
            deficiencies = [f"Missing required statutory document: {doc}" for doc in request.missing_doc_types]

        return PredictClarificationResponse(
            clarification_probability=prob,
            common_deficiencies=deficiencies or ["Resolution/validity period of uploaded PDF certificate"],
            guidance="Ensure all uploaded structural blueprints include the licensed structural engineer's digital signature and seal."
        )

    def validate_document(self, request: ValidateDocRequest) -> ValidateDocResponse:
        doc_type = request.document_type
        return ValidateDocResponse(
            status="VALID",
            confidence_score=0.96,
            extracted_fields={
                "detected_type": doc_type,
                "file_name": request.file_name,
                "format_check": "PDF-A compliant",
                "signature_detected": True
            },
            issues_detected=[],
            recommendation="Document meets all formatting and statutory checklist requirements."
        )

    def ask_regulatory_rag(self, request: AskRAGRequest) -> AskRAGResponse:
        return AskRAGResponse(
            answer=f"Under the relevant state single-window regulations for '{request.sector or 'Industrial Units'}', industrial units with capital investment over ₹5 Cr are entitled to deemed approval provisions if no objection is raised within 30 days of complete application receipt.",
            cited_acts=["Uttar Pradesh Industrial Peace Act", "Water (Prevention and Control of Pollution) Act 1974 Sec 25", "Factories Act 1948 Sec 6"],
            confidence=0.92,
            relevant_sections=["Section 25 (Consent to Establish)", "Section 6 (Approval, licensing and registration of factories)"]
        )

mock_ai_service = MockAIService()

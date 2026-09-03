"""Database Seeding Script for SIH Problem Statement 130 (Synthetic Demo Data)"""
from datetime import datetime, timedelta, timezone
from app.database.connection import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.entities import (
    UserRoleEnum, ApplicationStatusEnum, ApprovalStatusEnum, InspectionStatusEnum,
    QueryStatusEnum, DocValidationStatusEnum,
    Role, User, Business, BusinessProfile, Department, Approval, ApprovalRequirement,
    Application, ApplicationApproval, Document, DocumentValidation, Inspection,
    InspectionReport, QueryRecord, SLARecord, Notification, Renewal, Incentive
)

def seed_database():
    """Initializes schema and populates with realistic synthetic demo dataset."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Role).first():
            print("Database already contains data. Skipping seed.")
            return

        print("Seeding database with synthetic Gov-Tech demonstration records...")

        now = datetime.now(timezone.utc)

        # 1. Create Roles
        role_map = {}
        for role_name in [r.value for r in UserRoleEnum]:
            role_obj = Role(
                name=role_name,
                description=f"Standard system role for {role_name.replace('_', ' ').title()}"
            )
            db.add(role_obj)
            db.flush()
            role_map[role_name] = role_obj.id

        # 2. Create Departments
        dept_uppcb = Department(
            code="UPPCB",
            name="Uttar Pradesh Pollution Control Board",
            state="Uttar Pradesh",
            description="Statutory authority for industrial environmental consents (Air/Water Acts)",
            contact_email="consent.uppcb@gov.in",
            sla_default_days=30
        )
        dept_fire = Department(
            code="FIRE_DEPT",
            name="State Fire Prevention & Emergency Services",
            state="Uttar Pradesh",
            description="Fire safety compliance and structural NOC issuance",
            contact_email="firenoc.up@gov.in",
            sla_default_days=15
        )
        dept_fssai = Department(
            code="FSSAI",
            name="Food Safety & Standards Authority of India",
            state="Central / UP State",
            description="Food manufacturing and hygiene safety licensing",
            contact_email="licensing.fssai@gov.in",
            sla_default_days=21
        )
        dept_factories = Department(
            code="FACTORIES_DEPT",
            name="Directorate of Factories & Boilers",
            state="Uttar Pradesh",
            description="Factory registration, worker safety, and building plan clearance",
            contact_email="factories.inspector@gov.in",
            sla_default_days=20
        )
        db.add_all([dept_uppcb, dept_fire, dept_fssai, dept_factories])
        db.flush()

        # 3. Create Users
        default_pwd = get_password_hash("password123")

        user_entrepreneur = User(
            email="entrepreneur@abcfoods.com",
            hashed_password=default_pwd,
            full_name="Rajesh Sharma",
            phone_number="+91-9876543210",
            role=UserRoleEnum.ENTREPRENEUR.value,
            role_id=role_map[UserRoleEnum.ENTREPRENEUR.value]
        )
        user_officer_uppcb = User(
            email="officer.uppcb@gov.in",
            hashed_password=default_pwd,
            full_name="Dr. Alok Verma",
            phone_number="+91-9811223344",
            role=UserRoleEnum.DEPARTMENT_OFFICER.value,
            role_id=role_map[UserRoleEnum.DEPARTMENT_OFFICER.value],
            department_id=dept_uppcb.id
        )
        user_officer_fire = User(
            email="officer.fire@gov.in",
            hashed_password=default_pwd,
            full_name="Capt. Vikram Singh",
            phone_number="+91-9822334455",
            role=UserRoleEnum.DEPARTMENT_OFFICER.value,
            role_id=role_map[UserRoleEnum.DEPARTMENT_OFFICER.value],
            department_id=dept_fire.id
        )
        user_gov_monitor = User(
            email="collector.ghaziabad@gov.in",
            hashed_password=default_pwd,
            full_name="IAS S. K. Awasthi (District Magistrate / Nodal Officer)",
            phone_number="+91-9833445566",
            role=UserRoleEnum.GOVERNMENT_OFFICER.value,
            role_id=role_map[UserRoleEnum.GOVERNMENT_OFFICER.value]
        )
        user_admin = User(
            email="admin@gov.in",
            hashed_password=default_pwd,
            full_name="Chief System Administrator",
            phone_number="+91-9899887766",
            role=UserRoleEnum.ADMINISTRATOR.value,
            role_id=role_map[UserRoleEnum.ADMINISTRATOR.value]
        )
        db.add_all([user_entrepreneur, user_officer_uppcb, user_officer_fire, user_gov_monitor, user_admin])
        db.flush()

        # 4. Create Approvals & Requirements
        appr_fire = Approval(
            department_id=dept_fire.id,
            code="FIRE_NOC",
            name="Fire Safety No Objection Certificate (Form-B)",
            category="Safety",
            description="Mandatory clearance for commercial & manufacturing units",
            sla_days=15,
            validity_years=3,
            statutory_fee=5000.0,
            requires_inspection=True
        )
        appr_pcb = Approval(
            department_id=dept_uppcb.id,
            code="PCB_CTE",
            name="Consent to Establish (Orange Category - Food Industry)",
            category="Environmental",
            description="Pollution control clearance under Water & Air Acts",
            sla_days=30,
            validity_years=5,
            statutory_fee=25000.0,
            requires_inspection=True
        )
        appr_fssai = Approval(
            department_id=dept_fssai.id,
            code="FSSAI_MFG",
            name="FSSAI State Manufacturing License",
            category="Operational",
            description="Statutory food safety manufacturing compliance",
            sla_days=21,
            validity_years=5,
            statutory_fee=7500.0,
            requires_inspection=False
        )
        appr_factory = Approval(
            department_id=dept_factories.id,
            code="FACTORY_LIC",
            name="Factory License & Structural Registration",
            category="Labor & Safety",
            description="Factories Act 1948 Section 6 clearance",
            sla_days=20,
            validity_years=1,
            statutory_fee=10000.0,
            requires_inspection=True
        )
        db.add_all([appr_fire, appr_pcb, appr_fssai, appr_factory])
        db.flush()

        # Requirements
        req1 = ApprovalRequirement(
            approval_id=appr_fire.id,
            document_type="Building Layout & Evacuation Plan",
            is_mandatory=True,
            description="Certified structural blueprint indicating emergency exits and hydrant placement"
        )
        req2 = ApprovalRequirement(
            approval_id=appr_pcb.id,
            document_type="Effluent Treatment Plant (ETP) Scheme",
            is_mandatory=True,
            description="Detailed wastewater treatment and water balance calculation"
        )
        req3 = ApprovalRequirement(
            approval_id=appr_fssai.id,
            document_type="FSMS Blueprint & Potability Report",
            is_mandatory=True,
            description="Food Safety Management System layout and certified laboratory water analysis"
        )
        db.add_all([req1, req2, req3])
        db.flush()

        # 5. Create Business (Fictional Demo Entity: ABC Foods Pvt Ltd)
        business = Business(
            user_id=user_entrepreneur.id,
            legal_name="ABC Foods Private Limited",
            trade_name="ABC Organics",
            registration_type="Private Limited Company",
            pan_number="AAACA1234F",
            gstin="09AAACA1234F1Z5"
        )
        db.add(business)
        db.flush()

        business_profile = BusinessProfile(
            business_id=business.id,
            sector="Food Processing",
            sub_sector="Organic Grain & Snack Processing",
            state="Uttar Pradesh",
            district="Ghaziabad",
            address="Plot No. 42-B, Sahibabad Industrial Area, Site IV",
            pincode="201010",
            investment_amount=50000000.0,  # ₹5 Crore
            employee_count=80,
            built_up_area_sqm=3200.0,
            power_requirement_kw=150.0,
            water_requirement_kld=25.0,
            hazardous_materials=False,
            details={"cold_storage_facility": True, "boiler_installed": False}
        )
        db.add(business_profile)
        db.flush()

        # 6. Create Application (Under Review with Parallel Approvals)
        application = Application(
            application_number="APP-2026-UP-0042",
            business_id=business.id,
            status=ApplicationStatusEnum.UNDER_REVIEW.value,
            submission_date=now - timedelta(days=12),
            estimated_completion_date=now + timedelta(days=18),
            overall_risk_score=0.22
        )
        db.add(application)
        db.flush()

        # Parallel Department Approvals
        app_appr_fire = ApplicationApproval(
            application_id=application.id,
            approval_id=appr_fire.id,
            status=ApprovalStatusEnum.APPROVED.value,
            assigned_officer_id=user_officer_fire.id,
            sla_target_date=now + timedelta(days=3),
            decision_date=now - timedelta(days=2),
            decision_remarks="Site inspection verified. All hydrant points and fire barriers fully compliant.",
            certificate_number="UP-FIRE-2026-9812",
            certificate_url="/certificates/FIRE-NOC-9812.pdf"
        )
        app_appr_pcb = ApplicationApproval(
            application_id=application.id,
            approval_id=appr_pcb.id,
            status=ApprovalStatusEnum.IN_REVIEW.value,
            assigned_officer_id=user_officer_uppcb.id,
            sla_target_date=now + timedelta(days=18)
        )
        app_appr_fssai = ApplicationApproval(
            application_id=application.id,
            approval_id=appr_fssai.id,
            status=ApprovalStatusEnum.PENDING.value,
            sla_target_date=now + timedelta(days=9)
        )
        app_appr_factory = ApplicationApproval(
            application_id=application.id,
            approval_id=appr_factory.id,
            status=ApprovalStatusEnum.IN_REVIEW.value,
            sla_target_date=now + timedelta(days=8)
        )
        db.add_all([app_appr_fire, app_appr_pcb, app_appr_fssai, app_appr_factory])
        db.flush()

        # 7. Documents & Pre-Validation
        doc1 = Document(
            business_id=business.id,
            application_id=application.id,
            document_type="Certificate of Incorporation",
            file_name="COI_ABC_Foods.pdf",
            file_path="/uploads/docs/coi_abc_foods.pdf",
            file_size_bytes=1048576,
            mime_type="application/pdf",
            is_verified=True,
            is_reusable=True
        )
        doc2 = Document(
            business_id=business.id,
            application_id=application.id,
            document_type="Building Layout & Evacuation Plan",
            file_name="Fire_Layout_Signed.pdf",
            file_path="/uploads/docs/fire_layout_signed.pdf",
            file_size_bytes=2457600,
            mime_type="application/pdf",
            is_verified=True,
            is_reusable=False
        )
        db.add_all([doc1, doc2])
        db.flush()

        doc_val = DocumentValidation(
            document_id=doc2.id,
            status=DocValidationStatusEnum.VALID.value,
            validation_score=0.98,
            extracted_metadata={"architect_license": "UP-ARCH-4412", "evacuation_routes": 4},
            issues_detected=[]
        )
        db.add(doc_val)
        db.flush()

        # 8. Scheduled Joint Inspection
        inspection = Inspection(
            application_id=application.id,
            department_id=dept_uppcb.id,
            inspector_id=user_officer_uppcb.id,
            scheduled_date=now + timedelta(days=4),
            status=InspectionStatusEnum.SCHEDULED.value,
            remarks="Joint site inspection for ETP effluent discharge pipeline and greenbelt audit."
        )
        db.add(inspection)
        db.flush()

        # 9. Query & Resolution Record
        query = QueryRecord(
            application_id=application.id,
            raised_by_id=user_officer_uppcb.id,
            department_code="UPPCB",
            query_text="Clarify daily industrial water consumption and recycle ratio for grain cleaning.",
            response_text="Clarification submitted: Daily intake is 25 KLD with 15 KLD recycled through tertiary RO plant.",
            status=QueryStatusEnum.RESOLVED.value,
            raised_at=now - timedelta(days=7),
            responded_at=now - timedelta(days=5)
        )
        db.add(query)
        db.flush()

        # 10. SLA Records
        sla_pcb = SLARecord(
            application_id=application.id,
            department_code="UPPCB",
            target_days=30,
            start_date=now - timedelta(days=12),
            due_date=now + timedelta(days=18),
            is_breached=False
        )
        db.add(sla_pcb)
        db.flush()

        # 11. Incentives (State Policy Schemes)
        incentive1 = Incentive(
            scheme_name="Uttar Pradesh Industrial Investment & Employment Promotion Policy",
            authority="UP Invest",
            eligible_sectors=["Food Processing", "Textiles", "Electronics"],
            min_investment=50000000.0,
            max_subsidy_amount=25000000.0,
            subsidy_percentage=25.0,
            description="25% Capital Investment Subsidy on plant and machinery for MSMEs in Western & Eastern UP.",
            portal_link="https://niveshmitra.up.nic.in"
        )
        incentive2 = Incentive(
            scheme_name="PM Formalisation of Micro Food Processing Enterprises (PMFME)",
            authority="Ministry of Food Processing Industries (MoFPI)",
            eligible_sectors=["Food Processing"],
            min_investment=1000000.0,
            max_subsidy_amount=10000000.0,
            subsidy_percentage=35.0,
            description="Credit-linked capital subsidy for technology upgrade and quality certification.",
            portal_link="https://pmfme.mofpi.gov.in"
        )
        db.add_all([incentive1, incentive2])
        db.flush()

        # 12. System Notifications
        notif = Notification(
            user_id=user_entrepreneur.id,
            title="Fire NOC Issued Successfully",
            message="Your Fire Safety NOC (Form-B) has been granted by the State Fire Prevention Service.",
            notification_type="INFO",
            is_read=False
        )
        db.add(notif)

        db.commit()
        print("Database successfully seeded with synthetic demo dataset for 'ABC Foods Pvt Ltd'.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

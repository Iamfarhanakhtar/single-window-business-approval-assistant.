"""Applications & Parallel Approval Workflow API Endpoints"""
from typing import List
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.entities import (
    Application, ApplicationApproval, Business, Approval, User,
    ApplicationStatusEnum, ApprovalStatusEnum, SLARecord
)
from app.schemas.domain import (
    ApplicationCreate, ApplicationResponse, ApplicationUpdateStatus
)
from app.auth.dependencies import get_current_user
from app.workflow.state_machine import WorkflowEngine

router = APIRouter(prefix="/applications", tags=["Applications & Workflow"])

@router.get("", response_model=List[ApplicationResponse])
def list_applications(
    status_filter: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Application)
    if current_user.role == "entrepreneur":
        biz_ids = [b.id for b in db.query(Business).filter(Business.user_id == current_user.id).all()]
        query = query.filter(Application.business_id.in_(biz_ids))
    elif current_user.role == "department_officer" and current_user.department_id:
        # Filter applications that contain approvals for this department
        query = query.join(ApplicationApproval).join(Approval).filter(Approval.department_id == current_user.department_id)

    if status_filter:
        query = query.filter(Application.status == status_filter)
    
    return query.order_by(Application.created_at.desc()).all()

@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    app_in: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    biz = db.query(Business).filter(Business.id == app_in.business_id).first()
    if not biz or (current_user.role == "entrepreneur" and biz.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to create application for this business")

    app_count = db.query(Application).count() + 1
    app_number = f"APP-2026-IN-{app_count:04d}"

    new_app = Application(
        application_number=app_number,
        business_id=biz.id,
        status=ApplicationStatusEnum.DRAFT.value,
        overall_risk_score=0.15
    )
    db.add(new_app)
    db.flush()

    for appr_id in app_in.approval_ids:
        approval = db.query(Approval).filter(Approval.id == appr_id).first()
        if approval:
            target_date = datetime.now(timezone.utc) + timedelta(days=approval.sla_days)
            app_approval = ApplicationApproval(
                application_id=new_app.id,
                approval_id=approval.id,
                status=ApprovalStatusEnum.PENDING.value,
                sla_target_date=target_date
            )
            db.add(app_approval)

    db.commit()
    db.refresh(new_app)
    return new_app

@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app_obj = db.query(Application).filter(Application.id == application_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj

@router.post("/{application_id}/submit", response_model=ApplicationResponse)
def submit_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app_obj = db.query(Application).filter(Application.id == application_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    WorkflowEngine.validate_transition(app_obj.status, ApplicationStatusEnum.SUBMITTED.value)
    
    app_obj.status = ApplicationStatusEnum.SUBMITTED.value
    app_obj.submission_date = datetime.now(timezone.utc)
    app_obj.estimated_completion_date = datetime.now(timezone.utc) + timedelta(days=30)
    
    # Automatically move to UNDER_REVIEW and initialize SLA timers for parallel approvals
    app_obj.status = ApplicationStatusEnum.UNDER_REVIEW.value
    for aa in app_obj.application_approvals:
        aa.status = ApprovalStatusEnum.IN_REVIEW.value
        sla_rec = SLARecord(
            application_id=app_obj.id,
            department_code=aa.approval.department.code if aa.approval and aa.approval.department else "GEN",
            target_days=aa.approval.sla_days if aa.approval else 15,
            start_date=datetime.now(timezone.utc),
            due_date=datetime.now(timezone.utc) + timedelta(days=aa.approval.sla_days if aa.approval else 15),
            is_breached=False
        )
        db.add(sla_rec)

    db.commit()
    db.refresh(app_obj)
    return app_obj

@router.patch("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: str,
    status_update: ApplicationUpdateStatus,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app_obj = db.query(Application).filter(Application.id == application_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    WorkflowEngine.validate_transition(app_obj.status, status_update.status)
    app_obj.status = status_update.status
    db.commit()
    db.refresh(app_obj)
    return app_obj

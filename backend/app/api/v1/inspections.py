"""Inspections & Site Visit Management API Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.entities import Inspection, InspectionReport, Application, User, InspectionStatusEnum
from app.schemas.domain import InspectionCreate, InspectionResponse, InspectionReportCreate
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/inspections", tags=["Inspections"])

@router.get("", response_model=List[InspectionResponse])
def list_inspections(
    application_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Inspection)
    if application_id:
        query = query.filter(Inspection.application_id == application_id)
    return query.all()

@router.post("", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
def schedule_inspection(
    insp_in: InspectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_insp = Inspection(
        application_id=insp_in.application_id,
        department_id=insp_in.department_id,
        inspector_id=current_user.id,
        scheduled_date=insp_in.scheduled_date,
        status=InspectionStatusEnum.SCHEDULED.value,
        remarks=insp_in.remarks
    )
    db.add(new_insp)
    db.commit()
    db.refresh(new_insp)
    return new_insp

@router.post("/{inspection_id}/report", status_code=status.HTTP_201_CREATED)
def submit_inspection_report(
    inspection_id: str,
    report_in: InspectionReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    report = InspectionReport(
        inspection_id=insp.id,
        findings=report_in.findings,
        is_compliant=report_in.is_compliant,
        checklist_results=report_in.checklist_results,
        geo_latitude=report_in.geo_latitude,
        geo_longitude=report_in.geo_longitude
    )
    insp.status = InspectionStatusEnum.COMPLETED.value
    db.add(report)
    db.commit()
    return {"message": "Inspection report submitted successfully", "report_id": report.id}

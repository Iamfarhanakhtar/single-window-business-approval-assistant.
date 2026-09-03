"""Approvals and Regulatory Catalog API Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.entities import Approval, Department
from app.schemas.domain import ApprovalResponse, DepartmentResponse

router = APIRouter(prefix="/approvals", tags=["Approvals & Catalog"])

@router.get("", response_model=List[ApprovalResponse])
def list_approvals(department_code: str = None, category: str = None, db: Session = Depends(get_db)):
    query = db.query(Approval).filter(Approval.is_active == True)
    if department_code:
        dept = db.query(Department).filter(Department.code == department_code).first()
        if dept:
            query = query.filter(Approval.department_id == dept.id)
    if category:
        query = query.filter(Approval.category == category)
    return query.all()

@router.get("/departments", response_model=List[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).filter(Department.is_active == True).all()

@router.get("/{approval_id}", response_model=ApprovalResponse)
def get_approval_detail(approval_id: str, db: Session = Depends(get_db)):
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval

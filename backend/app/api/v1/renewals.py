"""Renewals and Incentives API Endpoints"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.entities import Renewal, Incentive, Business, User
from app.schemas.domain import RenewalResponse, IncentiveResponse
from app.auth.dependencies import get_current_user

router = APIRouter(tags=["Renewals & Incentives"])

@router.get("/renewals", response_model=List[RenewalResponse])
def list_renewals(
    business_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Renewal)
    if business_id:
        query = query.filter(Renewal.business_id == business_id)
    elif current_user.role == "entrepreneur":
        biz_ids = [b.id for b in db.query(Business).filter(Business.user_id == current_user.id).all()]
        query = query.filter(Renewal.business_id.in_(biz_ids))
    return query.all()

@router.get("/incentives", response_model=List[IncentiveResponse])
def list_incentives(sector: str = None, db: Session = Depends(get_db)):
    query = db.query(Incentive)
    return query.all()

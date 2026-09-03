"""Business Profile API Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.entities import Business, BusinessProfile, User
from app.schemas.domain import BusinessCreate, BusinessResponse, BusinessProfileCreate
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/businesses", tags=["Businesses"])

@router.get("", response_model=List[BusinessResponse])
def get_user_businesses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role in ["government_officer", "administrator"]:
        return db.query(Business).all()
    return db.query(Business).filter(Business.user_id == current_user.id).all()

@router.post("", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
def create_business(biz_in: BusinessCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_biz = Business(
        user_id=current_user.id,
        legal_name=biz_in.legal_name,
        trade_name=biz_in.trade_name,
        registration_type=biz_in.registration_type,
        pan_number=biz_in.pan_number,
        gstin=biz_in.gstin
    )
    db.add(new_biz)
    db.flush()

    if biz_in.profile:
        prof = biz_in.profile
        new_prof = BusinessProfile(
            business_id=new_biz.id,
            sector=prof.sector,
            sub_sector=prof.sub_sector,
            state=prof.state,
            district=prof.district,
            address=prof.address,
            pincode=prof.pincode,
            investment_amount=prof.investment_amount,
            employee_count=prof.employee_count,
            built_up_area_sqm=prof.built_up_area_sqm,
            power_requirement_kw=prof.power_requirement_kw,
            water_requirement_kld=prof.water_requirement_kld,
            hazardous_materials=prof.hazardous_materials,
            details=prof.details
        )
        db.add(new_prof)

    db.commit()
    db.refresh(new_biz)
    return new_biz

@router.get("/{business_id}", response_model=BusinessResponse)
def get_business(business_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    biz = db.query(Business).filter(Business.id == business_id).first()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
    if current_user.role == "entrepreneur" and biz.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this business")
    return biz

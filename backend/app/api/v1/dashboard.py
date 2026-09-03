"""Dashboard Summary and Metrics API Endpoints"""
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.entities import Application, Department, Inspection, QueryRecord, Business, User
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard Summary"])

@router.get("/summary")
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    if current_user.role == "entrepreneur":
        businesses = db.query(Business).filter(Business.user_id == current_user.id).all()
        biz_ids = [b.id for b in businesses]
        applications = db.query(Application).filter(Application.business_id.in_(biz_ids)).all()
        
        return {
            "total_businesses": len(businesses),
            "total_applications": len(applications),
            "pending_approvals": len([a for a in applications if a.status in ["UNDER_REVIEW", "SUBMITTED"]]),
            "approved_applications": len([a for a in applications if a.status == "APPROVED"]),
            "action_required_queries": db.query(QueryRecord).filter(
                QueryRecord.application_id.in_([a.id for a in applications]),
                QueryRecord.status == "OPEN"
            ).count()
        }
    
    # Government / Officer overview
    return {
        "total_applications": db.query(Application).count(),
        "under_review": db.query(Application).filter(Application.status == "UNDER_REVIEW").count(),
        "scheduled_inspections": db.query(Inspection).filter(Inspection.status == "SCHEDULED").count(),
        "open_queries": db.query(QueryRecord).filter(QueryRecord.status == "OPEN").count(),
        "sla_compliance_rate": 94.2,
        "avg_clearance_days": 21.4
    }

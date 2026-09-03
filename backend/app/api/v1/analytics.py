"""Government Analytics & SLA Monitoring API Endpoints"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.entities import Department, SLARecord, Application
from app.auth.dependencies import require_role

router = APIRouter(prefix="/analytics", tags=["Government Analytics"])

@router.get("/overview")
def get_analytics_overview(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    return {
        "monthly_applications": [
            {"month": "Jan", "count": 42},
            {"month": "Feb", "count": 58},
            {"month": "Mar", "count": 65},
            {"month": "Apr", "count": 78},
            {"month": "May", "count": 92},
            {"month": "Jun", "count": 110}
        ],
        "department_clearance_efficiency": [
            {"department": "UPPCB", "avg_days": 24, "sla_target": 30, "compliance": 92.5},
            {"department": "FIRE_DEPT", "avg_days": 11, "sla_target": 15, "compliance": 96.0},
            {"department": "FSSAI", "avg_days": 18, "sla_target": 21, "compliance": 91.2},
            {"department": "FACTORIES_DEPT", "avg_days": 16, "sla_target": 20, "compliance": 94.8}
        ],
        "bottlenecks": [
            {"factor": "Missing ETP schematics in initial submission", "affected_percentage": 34},
            {"factor": "Delayed joint site inspection slot booking", "affected_percentage": 22},
            {"factor": "Structural stability certificate resubmissions", "affected_percentage": 14}
        ]
    }

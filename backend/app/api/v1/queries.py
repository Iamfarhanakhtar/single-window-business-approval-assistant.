"""Department Queries & Clarification API Endpoints"""
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.entities import QueryRecord, Application, User, QueryStatusEnum
from app.schemas.domain import QueryCreate, QueryRespond, QueryResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/queries", tags=["Queries & Clarifications"])

@router.get("", response_model=List[QueryResponse])
def list_queries(
    application_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(QueryRecord)
    if application_id:
        query = query.filter(QueryRecord.application_id == application_id)
    return query.order_by(QueryRecord.raised_at.desc()).all()

@router.post("", response_model=QueryResponse, status_code=status.HTTP_201_CREATED)
def raise_query(
    query_in: QueryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    app_obj = db.query(Application).filter(Application.id == query_in.application_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")

    new_query = QueryRecord(
        application_id=query_in.application_id,
        raised_by_id=current_user.id,
        department_code=query_in.department_code,
        query_text=query_in.query_text,
        status=QueryStatusEnum.OPEN.value
    )
    db.add(new_query)
    db.commit()
    db.refresh(new_query)
    return new_query

@router.post("/{query_id}/respond", response_model=QueryResponse)
def respond_to_query(
    query_id: str,
    resp_in: QueryRespond,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q_obj = db.query(QueryRecord).filter(QueryRecord.id == query_id).first()
    if not q_obj:
        raise HTTPException(status_code=404, detail="Query not found")

    q_obj.response_text = resp_in.response_text
    q_obj.status = QueryStatusEnum.RESOLVED.value
    q_obj.responded_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(q_obj)
    return q_obj

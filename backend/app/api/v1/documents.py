"""Document Management & Validation API Endpoints"""
import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.entities import Document, DocumentValidation, DocValidationStatusEnum, User, Business
from app.schemas.domain import DocumentResponse
from app.auth.dependencies import get_current_user
from app.core.config import settings
from ai.services.mock_ai_service import mock_ai_service
from app.schemas.domain import ValidateDocRequest

from app.schemas.compliance import DocumentValidateRequest, DocumentValidationResponse
from app.services.compliance_analysis_service import compliance_service

router = APIRouter(prefix="/documents", tags=["Documents & Pre-Validation"])

@router.get("", response_model=List[DocumentResponse])
def list_documents(
    business_id: str = None,
    application_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Document)
    if business_id:
        query = query.filter(Document.business_id == business_id)
    if application_id:
        query = query.filter(Document.application_id == application_id)
    return query.all()

@router.post("/validate", response_model=DocumentValidationResponse)
def validate_document_endpoint(request: DocumentValidateRequest):
    """
    POST /api/v1/documents/validate
    Pre-validates document formatting, entity matching, expiry dates, and category.
    """
    try:
        return compliance_service.validate_document(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document AI validation error: {str(e)}"
        )

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    business_id: str = Form(...),
    document_type: str = Form(...),
    application_id: str = Form(None),
    is_reusable: bool = Form(True),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify business ownership
    biz = db.query(Business).filter(Business.id == business_id).first()
    if not biz or (current_user.role == "entrepreneur" and biz.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized for this business")

    file_ext = os.path.splitext(file.filename)[1]
    safe_filename = f"{business_id}_{document_type.replace(' ', '_')}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    new_doc = Document(
        business_id=business_id,
        application_id=application_id,
        document_type=document_type,
        file_name=file.filename,
        file_path=file_path,
        file_size_bytes=file_size,
        mime_type=file.content_type or "application/octet-stream",
        is_verified=False,
        is_reusable=is_reusable
    )
    db.add(new_doc)
    db.flush()

    # Pre-validate with real Document AI pipeline
    val_res = compliance_service.validate_document(DocumentValidateRequest(
        document_id=new_doc.id,
        filename=file.filename,
        document_type=document_type,
        file_path=file_path,
        expected_entity_name=biz.legal_name,
        expected_document_type=document_type,
        application_id=application_id,
    ))

    val_record = DocumentValidation(
        document_id=new_doc.id,
        status=val_res.status,
        validation_score=val_res.confidence,
        extracted_metadata={"days_until_expiry": val_res.days_until_expiry, "entity_match": val_res.entity_match},
        issues_detected=val_res.warnings + val_res.errors
    )
    db.add(val_record)

    db.commit()
    db.refresh(new_doc)
    return new_doc


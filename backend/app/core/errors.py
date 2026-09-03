"""Standardized Error Responses and Exceptions"""
from fastapi import HTTPException, status

class EntityNotFoundError(HTTPException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} with ID '{entity_id}' not found."
        )

class UnauthorizedAccessError(HTTPException):
    def __init__(self, detail: str = "Insufficient permissions for this resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class InvalidStateTransitionError(HTTPException):
    def __init__(self, current_state: str, attempted_state: str, reason: str = ""):
        message = f"Cannot transition application from '{current_state}' to '{attempted_state}'."
        if reason:
            message += f" Reason: {reason}"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

class DocumentValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

"""Application Workflow State Machine & Parallel Approval Coordinator"""
from typing import Set, Dict, List
from app.models.entities import ApplicationStatusEnum, ApprovalStatusEnum
from app.core.errors import InvalidStateTransitionError

# Valid state transitions for master Application
ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
    ApplicationStatusEnum.DRAFT.value: {
        ApplicationStatusEnum.DOCUMENT_CHECK.value
    },
    ApplicationStatusEnum.DOCUMENT_CHECK.value: {
        ApplicationStatusEnum.READY_FOR_SUBMISSION.value,
        ApplicationStatusEnum.DRAFT.value
    },
    ApplicationStatusEnum.READY_FOR_SUBMISSION.value: {
        ApplicationStatusEnum.SUBMITTED.value,
        ApplicationStatusEnum.DRAFT.value
    },
    ApplicationStatusEnum.SUBMITTED.value: {
        ApplicationStatusEnum.UNDER_REVIEW.value
    },
    ApplicationStatusEnum.UNDER_REVIEW.value: {
        ApplicationStatusEnum.INSPECTION_REQUIRED.value,
        ApplicationStatusEnum.QUERY_RAISED.value,
        ApplicationStatusEnum.APPROVED.value,
        ApplicationStatusEnum.REJECTED.value
    },
    ApplicationStatusEnum.INSPECTION_REQUIRED.value: {
        ApplicationStatusEnum.INSPECTION_SCHEDULED.value
    },
    ApplicationStatusEnum.INSPECTION_SCHEDULED.value: {
        ApplicationStatusEnum.INSPECTION_COMPLETED.value
    },
    ApplicationStatusEnum.INSPECTION_COMPLETED.value: {
        ApplicationStatusEnum.UNDER_REVIEW.value,
        ApplicationStatusEnum.QUERY_RAISED.value,
        ApplicationStatusEnum.APPROVED.value,
        ApplicationStatusEnum.REJECTED.value
    },
    ApplicationStatusEnum.QUERY_RAISED.value: {
        ApplicationStatusEnum.RESUBMITTED.value
    },
    ApplicationStatusEnum.RESUBMITTED.value: {
        ApplicationStatusEnum.UNDER_REVIEW.value
    },
    ApplicationStatusEnum.APPROVED.value: {
        ApplicationStatusEnum.RENEWAL_MONITORING.value
    },
    ApplicationStatusEnum.REJECTED.value: set(),
    ApplicationStatusEnum.RENEWAL_MONITORING.value: set(),
}

class WorkflowEngine:
    @staticmethod
    def validate_transition(current_state: str, new_state: str) -> bool:
        """Ensures the application lifecycle respects the statutory state graph."""
        allowed = ALLOWED_TRANSITIONS.get(current_state, set())
        if new_state not in allowed:
            raise InvalidStateTransitionError(
                current_state=current_state,
                attempted_state=new_state,
                reason=f"Permitted next states from {current_state} are {list(allowed)}"
            )
        return True

    @staticmethod
    def aggregate_parallel_approvals(approval_statuses: List[str]) -> str:
        """
        Derives the overarching Application Status from parallel departmental approvals:
        - If any rejected -> REJECTED
        - If all approved -> APPROVED
        - If any query raised -> QUERY_RAISED
        - If any inspection scheduled -> INSPECTION_SCHEDULED
        - Else -> UNDER_REVIEW
        """
        if not approval_statuses:
            return ApplicationStatusEnum.UNDER_REVIEW.value

        if all(s == ApprovalStatusEnum.APPROVED.value for s in approval_statuses):
            return ApplicationStatusEnum.APPROVED.value

        if any(s == ApprovalStatusEnum.REJECTED.value for s in approval_statuses):
            return ApplicationStatusEnum.REJECTED.value

        if any(s == ApprovalStatusEnum.QUERY_RAISED.value for s in approval_statuses):
            return ApplicationStatusEnum.QUERY_RAISED.value

        if any(s == ApprovalStatusEnum.INSPECTION_SCHEDULED.value for s in approval_statuses):
            return ApplicationStatusEnum.INSPECTION_SCHEDULED.value

        return ApplicationStatusEnum.UNDER_REVIEW.value

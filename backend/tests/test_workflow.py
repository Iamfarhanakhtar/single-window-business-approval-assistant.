"""Workflow State Machine Unit Tests"""
import pytest
from app.workflow.state_machine import WorkflowEngine
from app.models.entities import ApplicationStatusEnum, ApprovalStatusEnum
from app.core.errors import InvalidStateTransitionError

def test_valid_state_transitions():
    assert WorkflowEngine.validate_transition(
        ApplicationStatusEnum.DRAFT.value,
        ApplicationStatusEnum.DOCUMENT_CHECK.value
    ) is True

    assert WorkflowEngine.validate_transition(
        ApplicationStatusEnum.READY_FOR_SUBMISSION.value,
        ApplicationStatusEnum.SUBMITTED.value
    ) is True

def test_invalid_state_transition():
    with pytest.raises(InvalidStateTransitionError):
        # Cannot jump from DRAFT directly to APPROVED
        WorkflowEngine.validate_transition(
            ApplicationStatusEnum.DRAFT.value,
            ApplicationStatusEnum.APPROVED.value
        )

def test_parallel_approval_aggregation():
    # If all approved -> overall application approved
    res = WorkflowEngine.aggregate_parallel_approvals([
        ApprovalStatusEnum.APPROVED.value,
        ApprovalStatusEnum.APPROVED.value
    ])
    assert res == ApplicationStatusEnum.APPROVED.value

    # If any rejected -> overall application rejected
    res = WorkflowEngine.aggregate_parallel_approvals([
        ApprovalStatusEnum.APPROVED.value,
        ApprovalStatusEnum.REJECTED.value
    ])
    assert res == ApplicationStatusEnum.REJECTED.value

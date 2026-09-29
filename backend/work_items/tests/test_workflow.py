import pytest

from work_items.domain.workflow import (
    ALLOWED_TRANSITIONS,
    TransitionError,
    WorkItemStatus,
    transition,
)

VALID_TRANSITIONS = [
    (WorkItemStatus.RECEIVED, WorkItemStatus.ANALYSING),
    (WorkItemStatus.ANALYSING, WorkItemStatus.READY_FOR_REVIEW),
    (WorkItemStatus.ANALYSING, WorkItemStatus.FAILED),
    (WorkItemStatus.READY_FOR_REVIEW, WorkItemStatus.COMPLETED),
    (WorkItemStatus.FAILED, WorkItemStatus.ANALYSING),
]

INVALID_TRANSITIONS = [
    (WorkItemStatus.COMPLETED, WorkItemStatus.ANALYSING),
    (WorkItemStatus.COMPLETED, WorkItemStatus.RECEIVED),
    (WorkItemStatus.RECEIVED, WorkItemStatus.COMPLETED),
    (WorkItemStatus.RECEIVED, WorkItemStatus.READY_FOR_REVIEW),
    (WorkItemStatus.FAILED, WorkItemStatus.COMPLETED),
    (WorkItemStatus.READY_FOR_REVIEW, WorkItemStatus.ANALYSING),
]


@pytest.mark.parametrize("current_status,new_status", VALID_TRANSITIONS)
def test_valid_transitions(current_status, new_status):
    assert transition(current_status, new_status) == new_status


@pytest.mark.parametrize("current_status,new_status", INVALID_TRANSITIONS)
def test_invalid_transitions_raise(current_status, new_status):
    with pytest.raises(TransitionError):
        transition(current_status, new_status)


def test_completed_is_terminal():
    assert ALLOWED_TRANSITIONS[WorkItemStatus.COMPLETED] == []

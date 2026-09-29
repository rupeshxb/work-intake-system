# Pure domain logic: work item status enum, allowed state transitions, and transition enforcement. No Django imports.
from enum import Enum


class WorkItemStatus(Enum):
    RECEIVED = "RECEIVED"
    ANALYSING = "ANALYSING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


ALLOWED_TRANSITIONS = {
    WorkItemStatus.RECEIVED: [WorkItemStatus.ANALYSING],
    WorkItemStatus.ANALYSING: [WorkItemStatus.READY_FOR_REVIEW, WorkItemStatus.FAILED],
    WorkItemStatus.READY_FOR_REVIEW: [WorkItemStatus.COMPLETED],
    WorkItemStatus.COMPLETED: [],
    WorkItemStatus.FAILED: [WorkItemStatus.ANALYSING],
}


class TransitionError(Exception):
    pass


def transition(current_status: WorkItemStatus, new_status: WorkItemStatus) -> WorkItemStatus:
    if new_status not in ALLOWED_TRANSITIONS[current_status]:
        raise TransitionError(
            f"Cannot transition from {current_status.name} to {new_status.name}"
        )
    return new_status

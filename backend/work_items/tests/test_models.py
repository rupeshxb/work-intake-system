# Tests for WorkItem and AnalysisAttempt models including the unique constraint.
import pytest
from django.db import IntegrityError

from work_items.models import AnalysisAttempt, WorkItem


@pytest.mark.django_db
def test_work_item_default_status():
    item = WorkItem.objects.create(
        external_id="ext-1",
        title="Title",
        description="Description",
    )
    assert item.status == "RECEIVED"


@pytest.mark.django_db
def test_external_id_unique_constraint():
    WorkItem.objects.create(
        external_id="ext-dup",
        title="Title",
        description="Description",
    )
    with pytest.raises(IntegrityError):
        WorkItem.objects.create(
            external_id="ext-dup",
            title="Title 2",
            description="Description 2",
        )


@pytest.mark.django_db
def test_analysis_attempt_linked_to_work_item():
    item = WorkItem.objects.create(
        external_id="ext-2",
        title="Title",
        description="Description",
    )
    attempt = AnalysisAttempt.objects.create(
        work_item=item,
        attempt_number=1,
        status="SUCCESS",
    )
    assert attempt.work_item == item

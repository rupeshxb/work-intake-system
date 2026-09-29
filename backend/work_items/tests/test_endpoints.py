# Tests for the list/detail/analyse/retry/status endpoints, including pagination and filtering.
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from work_items.models import WorkItem


@pytest.fixture
def received_work_item():
    return WorkItem.objects.create(
        external_id="TEST-001",
        title="Title",
        description="Description",
        status="RECEIVED",
    )


@pytest.mark.django_db
def test_get_work_items_list_returns_200(received_work_item):
    client = APIClient()
    response = client.get(reverse("work-item-list-create"))
    assert response.status_code == 200
    assert "results" in response.data


@pytest.mark.django_db
def test_filter_by_status(received_work_item):
    WorkItem.objects.create(
        external_id="TEST-002", title="Title", description="Description", status="FAILED"
    )
    client = APIClient()
    response = client.get(reverse("work-item-list-create"), {"status": "FAILED"})
    assert response.status_code == 200
    statuses = {item["status"] for item in response.data["results"]}
    assert statuses == {"FAILED"}


@pytest.mark.django_db
def test_get_work_item_detail_returns_200(received_work_item):
    client = APIClient()
    response = client.get(reverse("work-item-detail", args=[received_work_item.id]))
    assert response.status_code == 200
    assert response.data["externalId"] == "TEST-001"


@pytest.mark.django_db
def test_get_nonexistent_work_item_returns_404():
    client = APIClient()
    response = client.get("/api/work-items/not-a-uuid/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_analyse_endpoint_triggers_analysis(received_work_item, settings):
    settings.LLM_PROVIDER = "mock"
    client = APIClient()
    response = client.post(reverse("work-item-analyse", args=[received_work_item.id]))
    assert response.status_code == 200
    assert response.data["status"] == "READY_FOR_REVIEW"


@pytest.mark.django_db
def test_analyse_already_analysing_returns_409(received_work_item):
    received_work_item.status = "ANALYSING"
    received_work_item.save(update_fields=["status"])

    client = APIClient()
    response = client.post(reverse("work-item-analyse", args=[received_work_item.id]))
    assert response.status_code == 409


@pytest.mark.django_db
def test_retry_non_failed_item_returns_409(received_work_item):
    client = APIClient()
    response = client.post(reverse("work-item-retry", args=[received_work_item.id]))
    assert response.status_code == 409


@pytest.mark.django_db
def test_retry_failed_item_succeeds(received_work_item, settings):
    settings.LLM_PROVIDER = "mock"
    received_work_item.status = "FAILED"
    received_work_item.save(update_fields=["status"])

    client = APIClient()
    response = client.post(reverse("work-item-retry", args=[received_work_item.id]))
    assert response.status_code == 200
    assert response.data["status"] == "READY_FOR_REVIEW"


@pytest.mark.django_db
def test_patch_status_to_completed(received_work_item):
    received_work_item.status = "READY_FOR_REVIEW"
    received_work_item.save(update_fields=["status"])

    client = APIClient()
    response = client.patch(
        reverse("work-item-status", args=[received_work_item.id]),
        {"status": "COMPLETED"},
        format="json",
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_patch_status_to_analysing_returns_400(received_work_item):
    client = APIClient()
    response = client.patch(
        reverse("work-item-status", args=[received_work_item.id]),
        {"status": "ANALYSING"},
        format="json",
    )
    assert response.status_code == 400

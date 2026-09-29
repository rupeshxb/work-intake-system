# Tests for the intake endpoint including idempotency and concurrent duplicate handling.
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from work_items.models import WorkItem


@pytest.mark.django_db
def test_create_work_item_returns_201():
    client = APIClient()
    response = client.post(
        reverse("work-item-list-create"),
        {"externalId": "ext-1", "title": "Title", "description": "Description"},
        format="json",
    )
    assert response.status_code == 201
    assert response.data["externalId"] == "ext-1"


@pytest.mark.django_db
def test_duplicate_external_id_returns_200():
    client = APIClient()
    payload = {"externalId": "ext-dup", "title": "Title", "description": "Description"}

    first = client.post(reverse("work-item-list-create"), payload, format="json")
    assert first.status_code == 201

    second = client.post(reverse("work-item-list-create"), payload, format="json")
    assert second.status_code == 200

    assert WorkItem.objects.filter(external_id="ext-dup").count() == 1


@pytest.mark.django_db
def test_duplicate_with_different_payload_returns_409():
    client = APIClient()
    client.post(
        reverse("work-item-list-create"),
        {"externalId": "ext-conflict", "title": "Title", "description": "Description"},
        format="json",
    )

    response = client.post(
        reverse("work-item-list-create"),
        {"externalId": "ext-conflict", "title": "Different Title", "description": "Description"},
        format="json",
    )
    assert response.status_code == 409


@pytest.mark.django_db
def test_missing_required_fields_returns_400():
    client = APIClient()
    response = client.post(
        reverse("work-item-list-create"),
        {"externalId": "ext-missing-title", "description": "Description"},
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_allowed_actions_for_received_status():
    client = APIClient()
    response = client.post(
        reverse("work-item-list-create"),
        {"externalId": "ext-actions", "title": "Title", "description": "Description"},
        format="json",
    )
    assert "analyse" in response.data["allowedActions"]


@pytest.mark.django_db(transaction=True)
def test_concurrent_duplicate_external_id_creates_one_row():
    """
    Ten threads POST the same externalId simultaneously.
    Only one WorkItem should be created in the database.
    """
    import threading
    from django.db import connection

    client = APIClient()
    results = []
    errors = []

    def post_work_item():
        try:
            response = client.post(
                reverse("work-item-list-create"),
                {
                    "externalId": "CONCURRENT-001",
                    "title": "Concurrent Test",
                    "description": "Testing concurrent duplicate handling",
                },
                format="json",
            )
            results.append(response.status_code)
        except Exception as e:
            errors.append(str(e))
        finally:
            connection.close()

    threads = [threading.Thread(target=post_work_item) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Threads raised errors: {errors}"
    assert WorkItem.objects.filter(external_id="CONCURRENT-001").count() == 1
    assert results.count(201) == 1
    assert results.count(200) == 9

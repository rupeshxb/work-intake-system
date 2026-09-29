# Tests for the analysis service covering success, failure modes, and attempt recording.
import pytest

from work_items.ai.providers import MockProvider
from work_items.models import AnalysisAttempt, WorkItem
from work_items.services.analysis import AnalysisService


@pytest.fixture
def received_work_item():
    return WorkItem.objects.create(
        external_id="TEST-001",
        title="Title",
        description="Description",
        status="RECEIVED",
    )


@pytest.mark.django_db
def test_successful_analysis_moves_to_ready_for_review(received_work_item):
    result = AnalysisService.run(received_work_item.id, provider=MockProvider(mode="success"))
    assert result.status == "READY_FOR_REVIEW"
    assert result.analysis is not None


@pytest.mark.django_db
def test_timeout_moves_to_failed(received_work_item):
    result = AnalysisService.run(received_work_item.id, provider=MockProvider(mode="timeout"))
    assert result.status == "FAILED"
    assert "timeout" in result.failure_reason.lower()


@pytest.mark.django_db
def test_malformed_response_moves_to_failed(received_work_item):
    result = AnalysisService.run(received_work_item.id, provider=MockProvider(mode="malformed"))
    assert result.status == "FAILED"
    assert result.analysis is None


@pytest.mark.django_db
def test_invalid_enum_moves_to_failed(received_work_item):
    result = AnalysisService.run(received_work_item.id, provider=MockProvider(mode="invalid_enum"))
    assert result.status == "FAILED"
    assert result.analysis is None


@pytest.mark.django_db
def test_analysis_attempt_is_recorded(received_work_item):
    AnalysisService.run(received_work_item.id, provider=MockProvider(mode="success"))
    assert AnalysisAttempt.objects.filter(
        work_item=received_work_item, status="SUCCESS"
    ).count() == 1


@pytest.mark.django_db
def test_failed_attempt_is_recorded(received_work_item):
    AnalysisService.run(received_work_item.id, provider=MockProvider(mode="exception"))
    assert AnalysisAttempt.objects.filter(
        work_item=received_work_item, status="FAILED"
    ).count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("mode", ["timeout", "malformed", "invalid_enum", "exception"])
def test_analysis_never_corrupts_work_item_on_failure(received_work_item, mode):
    result = AnalysisService.run(received_work_item.id, provider=MockProvider(mode=mode))
    assert result.analysis is None

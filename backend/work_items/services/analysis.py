# Analysis service: moves a work item through ANALYSING via LLM call, outside any open transaction.
import json
import time

from django.conf import settings
from django.db.models import F
from django.utils import timezone

from work_items.ai.providers import GeminiProvider, GroqProvider, MockProvider
from work_items.ai.schema import AnalysisResult
from work_items.domain.workflow import TransitionError
from work_items.models import AnalysisAttempt, WorkItem


class AnalysisService:
    @staticmethod
    def run(work_item_id, provider=None) -> WorkItem:
        work_item = WorkItem.objects.get(pk=work_item_id)

        updated = WorkItem.objects.filter(
            pk=work_item_id, status__in=["RECEIVED", "FAILED"]
        ).update(status="ANALYSING", analysis_started_at=timezone.now(), version=F("version") + 1)

        if updated == 0:
            raise TransitionError("Work item is not in an analysable state")

        work_item.refresh_from_db()

        if provider is None:
            if settings.LLM_PROVIDER == "gemini":
                provider = GeminiProvider()
            elif settings.LLM_PROVIDER == "groq":
                provider = GroqProvider()
            else:
                provider = MockProvider(mode="success")

        attempt_number = work_item.attempts.count() + 1
        start_time = time.time()
        raw = None

        try:
            raw = provider.analyse(work_item.title, work_item.description)
            result = AnalysisResult(**raw).model_dump()
            elapsed_ms = int((time.time() - start_time) * 1000)

            work_item.status = "READY_FOR_REVIEW"
            work_item.analysis = result
            work_item.failure_reason = None
            work_item.save(update_fields=["status", "analysis", "failure_reason", "updated_at"])

            AnalysisAttempt.objects.create(
                work_item=work_item,
                attempt_number=attempt_number,
                status="SUCCESS",
                raw_response=json.dumps(raw),
                latency_ms=elapsed_ms,
            )
        except Exception as exc:
            elapsed_ms = int((time.time() - start_time) * 1000)

            work_item.status = "FAILED"
            work_item.failure_reason = str(exc)
            work_item.save(update_fields=["status", "failure_reason", "updated_at"])

            AnalysisAttempt.objects.create(
                work_item=work_item,
                attempt_number=attempt_number,
                status="FAILED",
                error=str(exc),
                raw_response=str(raw) if raw is not None else None,
                latency_ms=elapsed_ms,
            )

        work_item.refresh_from_db()
        return work_item

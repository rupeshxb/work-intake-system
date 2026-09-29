# Database models: WorkItem (the main record) and AnalysisAttempt (one row per LLM call).
import uuid

from django.db import models


class WorkItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=500)
    description = models.TextField()
    status = models.CharField(max_length=50, default="RECEIVED")
    analysis = models.JSONField(null=True, blank=True)
    failure_reason = models.TextField(null=True, blank=True)
    analysis_started_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["external_id"]),
        ]

    def __str__(self):
        return f"{self.external_id} ({self.status})"


class AnalysisAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name="attempts")
    attempt_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20)
    raw_response = models.TextField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["attempt_number"]

    def __str__(self):
        return f"Attempt {self.attempt_number} for {self.work_item.external_id}"

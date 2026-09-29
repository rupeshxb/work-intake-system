# DRF serializers: validates incoming work item payloads and shapes outgoing responses including allowedActions.
from rest_framework import serializers

from work_items.domain.workflow import WorkItemStatus

ALLOWED_ACTIONS_BY_STATUS = {
    WorkItemStatus.RECEIVED.value: ["analyse"],
    WorkItemStatus.ANALYSING.value: [],
    WorkItemStatus.READY_FOR_REVIEW.value: ["complete"],
    WorkItemStatus.FAILED.value: ["retry"],
    WorkItemStatus.COMPLETED.value: [],
}


class WorkItemCreateSerializer(serializers.Serializer):
    externalId = serializers.CharField(required=True, allow_blank=False, source="external_id")
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)

    def validate_externalId(self, value):
        if not value.strip():
            raise serializers.ValidationError("externalId must not be blank")
        return value


class WorkItemResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    externalId = serializers.CharField(source="external_id")
    title = serializers.CharField()
    description = serializers.CharField()
    status = serializers.CharField()
    analysis = serializers.JSONField()
    failureReason = serializers.CharField(source="failure_reason")
    allowedActions = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")

    def get_allowedActions(self, obj):
        return ALLOWED_ACTIONS_BY_STATUS.get(obj.status, [])

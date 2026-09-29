# Intake service: orchestrates work item creation with idempotency and duplicate detection.
from django.db import IntegrityError, transaction

from work_items.models import WorkItem


class ConflictError(Exception):
    pass


class IntakeService:
    @staticmethod
    def create_or_get(validated_data) -> tuple[WorkItem, bool]:
        external_id = validated_data["external_id"]
        title = validated_data["title"]
        description = validated_data["description"]

        try:
            with transaction.atomic():
                item = WorkItem.objects.create(
                    external_id=external_id,
                    title=title,
                    description=description,
                )
            return item, True
        except IntegrityError:
            existing_item = WorkItem.objects.get(external_id=external_id)
            if existing_item.title != title or existing_item.description != description:
                raise ConflictError(
                    "Work item with this externalId already exists with different payload"
                )
            return existing_item, False

# API views: thin HTTP layer that delegates to services and returns serialized responses.
from rest_framework.response import Response
from rest_framework.views import APIView

from work_items.api.serializers import WorkItemCreateSerializer, WorkItemResponseSerializer
from work_items.services.intake import ConflictError, IntakeService


class WorkItemListCreateView(APIView):
    def post(self, request):
        serializer = WorkItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            item, created = IntakeService.create_or_get(serializer.validated_data)
        except ConflictError as exc:
            return Response(
                {"error": "conflict", "detail": str(exc)},
                status=409,
            )

        response_serializer = WorkItemResponseSerializer(item)
        return Response(response_serializer.data, status=201 if created else 200)

# API views: thin HTTP layer that delegates to services and returns serialized responses.
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from work_items.api.serializers import WorkItemCreateSerializer, WorkItemResponseSerializer
from work_items.domain.workflow import TransitionError, WorkItemStatus, transition
from work_items.models import WorkItem
from work_items.services.analysis import AnalysisService
from work_items.services.intake import ConflictError, IntakeService


class WorkItemPagination(PageNumberPagination):
    page_size = 20


class WorkItemListCreateView(APIView):
    def get(self, request):
        queryset = WorkItem.objects.all()
        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        paginator = WorkItemPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = WorkItemResponseSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

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


class WorkItemDetailView(APIView):
    def get(self, request, pk):
        try:
            item = WorkItem.objects.get(pk=pk)
        except WorkItem.DoesNotExist:
            return Response({"error": "not_found", "detail": "Work item not found"}, status=404)

        serializer = WorkItemResponseSerializer(item)
        return Response(serializer.data, status=200)


class WorkItemAnalyseView(APIView):
    def post(self, request, pk):
        try:
            item = AnalysisService.run(pk)
        except WorkItem.DoesNotExist:
            return Response({"error": "not_found", "detail": "Work item not found"}, status=404)
        except TransitionError as exc:
            return Response({"error": "conflict", "detail": str(exc)}, status=409)

        serializer = WorkItemResponseSerializer(item)
        return Response(serializer.data, status=200)


class WorkItemRetryView(APIView):
    def post(self, request, pk):
        try:
            item = WorkItem.objects.get(pk=pk)
        except WorkItem.DoesNotExist:
            return Response({"error": "not_found", "detail": "Work item not found"}, status=404)

        if item.status != "FAILED":
            return Response(
                {"error": "conflict", "detail": "Only failed work items can be retried"},
                status=409,
            )

        item = AnalysisService.run(pk)
        serializer = WorkItemResponseSerializer(item)
        return Response(serializer.data, status=200)


class WorkItemStatusView(APIView):
    def patch(self, request, pk):
        target_status = request.data.get("status")
        if target_status != "COMPLETED":
            return Response(
                {
                    "error": "invalid_transition",
                    "detail": "Only COMPLETED is allowed via this endpoint",
                },
                status=400,
            )

        try:
            item = WorkItem.objects.get(pk=pk)
        except WorkItem.DoesNotExist:
            return Response({"error": "not_found", "detail": "Work item not found"}, status=404)

        try:
            new_status = transition(WorkItemStatus(item.status), WorkItemStatus(target_status))
        except TransitionError as exc:
            return Response({"error": "conflict", "detail": str(exc)}, status=409)

        item.status = new_status.value
        item.save(update_fields=["status", "updated_at"])

        serializer = WorkItemResponseSerializer(item)
        return Response(serializer.data, status=200)

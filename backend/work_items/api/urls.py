# URL routing for the work_items API endpoints.
from django.urls import path

from work_items.api.views import (
    WorkItemAnalyseView,
    WorkItemDetailView,
    WorkItemListCreateView,
    WorkItemRetryView,
    WorkItemStatusView,
)

urlpatterns = [
    path("work-items/", WorkItemListCreateView.as_view(), name="work-item-list-create"),
    path("work-items/<uuid:pk>/", WorkItemDetailView.as_view(), name="work-item-detail"),
    path("work-items/<uuid:pk>/analyse/", WorkItemAnalyseView.as_view(), name="work-item-analyse"),
    path("work-items/<uuid:pk>/retry/", WorkItemRetryView.as_view(), name="work-item-retry"),
    path("work-items/<uuid:pk>/status/", WorkItemStatusView.as_view(), name="work-item-status"),
]

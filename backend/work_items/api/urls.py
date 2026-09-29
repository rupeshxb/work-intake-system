# URL routing for the work_items API endpoints.
from django.urls import path

from work_items.api.views import WorkItemListCreateView

urlpatterns = [
    path("work-items/", WorkItemListCreateView.as_view(), name="work-item-list-create"),
]

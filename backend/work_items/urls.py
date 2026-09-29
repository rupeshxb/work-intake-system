# Root URL configuration for the work_items app, includes health check and API routes.
from django.urls import include, path

from work_items.views import health

urlpatterns = [
    path("health/", health, name="health"),
    path("", include("work_items.api.urls")),
]

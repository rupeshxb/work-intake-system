from django.urls import path

from work_items.views import health

urlpatterns = [
    path("health/", health, name="health"),
]

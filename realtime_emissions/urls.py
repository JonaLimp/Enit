from django.urls import path
from realtime_emissions import views

urlpatterns = [
    path(
        "dashboard/<str:region_code>/",
        views.realtime_emissions_dashboard,
        name="emissions_dashboard",
    ),
]

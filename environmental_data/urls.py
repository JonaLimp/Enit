from django.urls import path
from environmental_data import views

urlpatterns = [
    path(
        "dashboard/<str:region_code>/",
        views.realtime_emissions_dashboard,
        name="emissions_dashboard",
    ),
]

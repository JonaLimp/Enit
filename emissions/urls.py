from django.urls import path
from emissions import views

urlpatterns = [
    path(
        "dashboard/<str:region_code>/",
        views.emissions_dashboard,
        name="emissions_dashboard",
    ),
]

from django.urls import path
from environmental_data import views

urlpatterns = [
    path(
        "dashboard/<str:region_code>/",
        views.realtime_emissions_dashboard,
        name="emissions_dashboard",
    ),
    path(
        "api/historical-data/",
        views.HistoricalDataView.as_view(),
        name="historical-data",
    ),
    path(
        "api/historical-data/<str:region_code>/",
        views.HistoricalDataView.as_view(),
        name="historical-data-region",
    ),
]

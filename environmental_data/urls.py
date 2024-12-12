from django.urls import path
from environmental_data import views

urlpatterns = [
    path(
        "dashboard/<str:country_code>/",
        views.realtime_emissions_dashboard,
        name="emissions_dashboard",
    ),
    path(
        "api/historical-data/",
        views.HistoricalDataView.as_view(),
        name="historical-data",
    ),
    path(
        "api/historical-data/<str:country_code>/",
        views.HistoricalDataView.as_view(),
        name="historical-data-country",
    ),
    path("api/countries/", views.CountryListView.as_view(), name="country-list"),
    path("api/sectors/", views.SectorListView.as_view(), name="sector-list"),
    path("api/substances/", views.SubstanceListView.as_view(), name="substance-list"),
]

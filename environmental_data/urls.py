from django.urls import path
from environmental_data import views

urlpatterns = [
    path(
        "dashboard/<str:country_code>/",
        views.realtime_emissions_dashboard,
        name="emissions_dashboard",
    ),
    path(
        "api/country-totals/",
        views.CountryTotalDataView.as_view(),
        name="country-totals",
    ),
    path("api/countries/", views.CountryListView.as_view(), name="country-list"),
    path("api/sectors/", views.SectorListView.as_view(), name="sector-list"),
    path("api/substances/", views.SubstanceListView.as_view(), name="substance-list"),
    path(
        "api/historical-environmental-data/",
        views.FilteredEnvironmentalDataView.as_view(),
        name="historical-environmental-data",
    ),
]

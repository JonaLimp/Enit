from django.shortcuts import render
from django.views import View
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework.generics import ListAPIView
from .filters import HistoricalDataFilter
from environmental_data.serializer import HistoricalEnvironmentalRecordSerializer
from rest_framework.exceptions import NotFound

from .models import (
    HistoricalEnvironmentalRecord,
    RealtimeEnvironmentalRecord,
    Country,
    Sector,
    Substance,
)


def realtime_emissions_dashboard(
    request: HttpRequest, region_code: str
) -> HttpResponse:
    """
    Displays a dashboard for the given region code with the last 24 hours of
    emissions data.

    Retrieves the region object for the given region code from the database.
    Retrieves the last 24 hours of emissions data for the given region from the database.
    Renders the emissions/dashboard.html template with the region and emissions data.

    Args:
        request (HttpRequest): The request object
        region_code (str): The region code (e.g. 'DE' for Germany)

    Returns:
        HttpResponse: A rendered HTML template with the emissions data for the
        given region
    """

    region = Country.objects.get(code=region_code)

    emissions_data = RealtimeEnvironmentalRecord.objects.filter(region=region).order_by(
        "-timestamp"
    )[:24]

    return render(
        request,
        "realtime_emissions/dashboard.html",
        {"region": region, "emissions_data": emissions_data},
    )


class CountryListView(View):
    """
    View to fetch all unique regions.
    """

    def get(self, request, *args, **kwargs):
        countries = Country.objects.values("name").distinct()
        return JsonResponse(list(countries), safe=False)


class SectorListView(View):
    """
    View to fetch all unique sectors.
    """

    def get(self, request, *args, **kwargs):
        sectors = Sector.objects.values("name").distinct()
        return JsonResponse(list(sectors), safe=False)


class SubstanceListView(View):
    """
    View to fetch all unique substances.
    """

    def get(self, request, *args, **kwargs):
        substances = Substance.objects.values("name").distinct()
        return JsonResponse(list(substances), safe=False)


class FilteredEnvironmentalDataView(ListAPIView):
    """
    Fetch historical environmental data with support for filtering by
    country, sector, substance, and year range. Defaults to the
    most recent year if no range is provided.
    """

    queryset = HistoricalEnvironmentalRecord.objects.all()
    serializer_class = HistoricalEnvironmentalRecordSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = HistoricalDataFilter

    def list(self, request, *args, **kwargs):
        """
        Overrides the list method to group data by country and their
        respective sectors. Includes an "All" value for the total of
        all sectors per country.
        """

        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {"error": "No data found for the provided filters."}, status=404
            )

        response_data = {}
        for record in queryset:
            country_name = record.country.name
            sector_name = record.sector.name
            year = record.year
            value = record.value

            if country_name not in response_data:
                response_data[country_name] = {}

            if sector_name not in response_data[country_name]:
                response_data[country_name][sector_name] = {}

            response_data[country_name][sector_name][year] = value

        return Response(response_data)

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_data = self.request.query_params

        country_names = filter_data.get("country", "").split(",")
        sectors = filter_data.get("sector", "").split(",")
        start_year = filter_data.get("start_year")
        end_year = filter_data.get("end_year")

        if country_names and country_names != [""]:
            queryset = queryset.filter(country__name__in=country_names)

        sectors = [sector.strip() for sector in sectors if sector.strip()]
        if sectors:
            queryset = queryset.filter(sector__name__in=sectors)

        if start_year and end_year:
            queryset = queryset.filter(year__gte=start_year, year__lte=end_year)

        if not queryset.exists():
            raise NotFound("No data found for the provided filters.")

        return queryset


class CountryTotalDataView(FilteredEnvironmentalDataView):
    """
    Fetch total values grouped by country and year.
    """

    def list(self, request, *args, **kwargs):
        """
        Overrides the list method to group data by country and their respective sectors.
        Includes an "All" value for the total of all sectors per country.
        """

        queryset = self.get_queryset()

        if not queryset.exists():
            return Response(
                {"error": "No data found for the provided filters."}, status=404
            )

        response_data = {}
        for record in queryset:
            country_name = record.country.name
            year = record.year
            value = record.value

            if country_name not in response_data:
                response_data[country_name] = {}

            if "Total" not in response_data[country_name]:
                response_data[country_name]["Total"] = {}

            if year not in response_data[country_name]["Total"]:
                response_data[country_name]["Total"][year] = 0

            response_data[country_name]["Total"][year] += value

        return Response(response_data)

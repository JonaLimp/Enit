from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response as RestResponse
from rest_framework import status
from rest_framework.renderers import JSONRenderer

from environmental_data.serializer import HistoricalEnvironmentalRecordSerializer
from .models import HistoricalEnvironmentalRecord, RealtimeEnvironmentalRecord, Region


from django.http import HttpRequest, HttpResponse


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

    region = Region.objects.get(code=region_code)

    emissions_data = RealtimeEnvironmentalRecord.objects.filter(region=region).order_by(
        "-timestamp"
    )[:24]

    return render(
        request,
        "realtime_emissions/dashboard.html",
        {"region": region, "emissions_data": emissions_data},
    )


class HistoricalDataView(APIView):
    """
    View to handle GET requests for environmental
    data for a specific region or all regions.
    """

    renderer_classes = [JSONRenderer]

    def get(self, request, region_code=None):
        if region_code:
            # Filter data based on the provided region_code
            records = HistoricalEnvironmentalRecord.objects.filter(
                region__code=region_code
            )
        else:
            # If no region_code is provided, return all data
            records = HistoricalEnvironmentalRecord.objects.all()

        # Serialize the data
        serializer = HistoricalEnvironmentalRecordSerializer(records, many=True)

        # Return the data in JSON format
        return RestResponse(serializer.data, status=status.HTTP_200_OK)

from django.shortcuts import render
from .models import EmissionRecord, Region


from django.http import HttpRequest, HttpResponse


def emissions_dashboard(request: HttpRequest, region_code: str) -> HttpResponse:
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

    emissions_data = EmissionRecord.objects.filter(region=region).order_by(
        "-timestamp"
    )[:24]

    return render(
        request,
        "emissions/dashboard.html",
        {"region": region, "emissions_data": emissions_data},
    )

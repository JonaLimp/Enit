from datetime import datetime, timedelta
import os
from venv import logger
import requests
from .models import (
    Country,
    Sector,
    Substance,
    RealtimeEnvironmentalRecord,
)
from django.utils import timezone
from datetime import timezone as tz
from celery import shared_task


from typing import Optional


@shared_task
def fetch_realtime_carbon_data(country_code: str) -> None:
    """
    Fetch the latest carbon intensity for a given country code from the
    ElectricityMap API and stores it in the database.

    Args:
        country_code (str): The country code to fetch data for.

    Returns:
        None
    """
    api_key: Optional[str] = os.getenv("ELECTRICITY_MAP_API_KEY")
    headers: dict = {"Authorization": f"Bearer {api_key}"}
    url: str = (
        "https://api.electricitymap.org/"
        f"v3/carbon-intensity/latest?zone={country_code}"
    )

    response: requests.Response = requests.get(url, headers=headers)
    data: dict = response.json()

    if response.status_code == 200 and "carbonIntensity" in data:

        country, _ = Country.objects.get_or_create(
            code=country_code, defaults={"name": data.get("zoneName", country_code)}
        )
        substance, _ = Substance.objects.get_or_create(name="CO2")
        sector, _ = Sector.objects.get_or_create(name="Total Emissions")
        RealtimeEnvironmentalRecord.objects.create(
            country=country,
            substance=substance,
            sector=sector,
            value=data["carbonIntensity"],
            timestamp=timezone.now(),
        )
        print(
            f"Fetched data for country \
                {country_code}: {response.status_code}"
        )
    else:
        print(
            f"Failed to fetch data for country \
                {country_code}: {response.status_code}"
        )


def fetch_recent_carbon_data(
    country_code: str, time_range_hours: int = 24, time_step: str = "hour"
) -> None:
    """
    Fetches historical carbon intensity data for the given country.

    :param country_code: Country code (e.g., 'DE' for Germany).
    :param time_range_hours: The number of hours back
    from the current time to fetch data. Defaults to 24.
    :param time_step: The granularity of the data ('hour', 'minute', 'day').
    Defaults to 'hour'.
    """

    api_key = os.getenv("ELECTRICITY_MAP_API_KEY")

    headers = {"Authorization": f"Bearer {api_key}"}

    now = datetime.now()

    from_timestamp = int((now - timedelta(hours=time_range_hours)).timestamp())

    to_timestamp = int(now.timestamp())

    url = f"https://api.electricitymap.org/v3/carbon-intensity/\
        history?zone={country_code}&from={from_timestamp}&to={to_timestamp}\
            &time_step={time_step}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        country, _ = Country.objects.get_or_create(
            code=country_code, defaults={"name": data.get("zoneName", country_code)}
        )

        substance, _ = Substance.objects.get_or_create(name="CO2")
        sector, _ = Sector.objects.get_or_create(name="Total Emissions")

        for entry in data["data"]:
            if entry["timestamp"] is None:
                logger.warning("Received None timestamp from the API. Skipping entry.")
                continue

            timestamp = datetime.fromtimestamp(entry["timestamp"], tz=tz.utc)

            carbon_intensity = entry["carbonIntensity"]

            if not RealtimeEnvironmentalRecord.objects.filter(
                country=country, timestamp=timestamp
            ).exists():
                RealtimeEnvironmentalRecord.objects.create(
                    country=country,
                    substance=substance,
                    value=carbon_intensity,
                    timestamp=timestamp,
                    sector=sector,
                )

        print(
            f"Historical data fetched and saved for country \
                {country_code} from {time_range_hours} hours ago"
        )
    else:
        print(
            f"Failed to fetch historical data for country \
                {country_code}: {response.status_code}"
        )

from datetime import datetime, timedelta
import os
from venv import logger
import requests
from .models import Region, EmissionRecord
from django.utils import timezone
from datetime import timezone as tz
from celery import shared_task


@shared_task
def fetch_emissions_data(region_code: str) -> None:
    api_key: str = os.getenv("ELECTRICITY_MAP_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}
    url = (
        "https://api.electricitymap.org/"
        f"v3/carbon-intensity/latest?zone={region_code}"
    )

    response = requests.get(url, headers=headers)
    data = response.json()

    if response.status_code == 200 and "carbonIntensity" in data:

        region, _ = Region.objects.get_or_create(
            code=region_code, defaults={"name": data.get("zoneName", region_code)}
        )
        EmissionRecord.objects.create(
            region=region,
            carbon_intensity=data["carbonIntensity"],
            timestamp=timezone.now(),
        )
        print(
            f"Fetched data for region \
                {region_code}: {response.status_code}"
        )
    else:
        print(
            f"Failed to fetch data for region \
                {region_code}: {response.status_code}"
        )


def fetch_historical_data(region_code, time_range_hours=24, time_step="hour"):
    """
    Fetches historical carbon intensity data for the given region.

    :param region_code: Region code (e.g., 'DE' for Germany).
    :param time_range_hours: The number of hours back
    from the current time to fetch data.
    :param time_step: The granularity of the data ('hour', 'minute', 'day').
    """

    api_key = os.getenv("ELECTRICITY_MAP_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}

    now = datetime.now()
    to_timestamp = int(now.timestamp())
    from_timestamp = int((now - timedelta(hours=time_range_hours)).timestamp())

    url = f"https://api.electricitymap.org/v3/carbon-intensity/\
        history?zone={region_code}&from={from_timestamp}&to={to_timestamp}\
            &time_step={time_step}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        region, _ = Region.objects.get_or_create(
            code=region_code, defaults={"name": data.get("zoneName", region_code)}
        )

        for entry in data["data"]:
            if entry["timestamp"] is None:
                logger.warning("Received None timestamp from the API. Skipping entry.")
                continue

            timestamp = datetime.fromtimestamp(entry["timestamp"], tz=tz.utc)
            carbon_intensity = entry["carbonIntensity"]

            if not EmissionRecord.objects.filter(
                region=region, timestamp=timestamp
            ).exists():
                EmissionRecord.objects.create(
                    region=region,
                    carbon_intensity=carbon_intensity,
                    timestamp=timestamp,
                )

        print(
            f"Historical data fetched and saved for region \
                {region_code} from {time_range_hours} hours ago"
        )
    else:
        print(
            f"Failed to fetch historical data for region \
                {region_code}: {response.status_code}"
        )

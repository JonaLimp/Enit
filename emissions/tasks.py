import os
import requests
from .models import Region, EmissionRecord
from django.utils import timezone


def fetch_emissions_data(region_code: str) -> None:
    api_key: str = os.getenv("ELECTRICITY_MAP_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}
    url = (
        "https://api.electricitymap.org/"
        f"v3/carbon-intensity/latest?zone={region_code}"
    )

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        if "carbonIntensity" in data:
            region, _ = Region.objects.get_or_create(
                code=region_code, defaults={"name": data.get("zoneName", region_code)}
            )
            EmissionRecord.objects.create(
                region=region,
                carbon_intensity=data["carbonIntensity"],
                timestamp=timezone.now(),
            )
    else:
        print(
            f"Failed to fetch data for region \
                {region_code}: {response.status_code}"
        )

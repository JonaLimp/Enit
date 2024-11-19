import os
import requests


def test():
    return ""


def fetch_emissions_data(region_code: str):
    api_key: str = os.getenv("ELECTRICITY_MAP_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}
    url = (
        "https://api.electricitymap.org/"
        f"v3/carbon-intensity/latest?zone={region_code}"
    )

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Failed to fetch data: {response.status_code}")

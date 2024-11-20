import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone

from emissions.models import EmissionRecord, Region
from emissions.tasks import fetch_emissions_data, fetch_historical_data

from datetime import timezone as tz


class EmissionsDataTestCase(TestCase):
    @patch("requests.get")
    def test_fetch_emissions_data_success(self, mock_get):

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "carbonIntensity": 100,
            "datetime": "2024-11-15T12:00:00Z",
        }

        mock_get.return_value = mock_response

        region_code = "DE"

        fetch_emissions_data(region_code)

        emission_record = EmissionRecord.objects.first()
        self.assertIsNotNone(emission_record)
        self.assertEqual(emission_record.carbon_intensity, 100)

    @patch("requests.get")
    def test_fetch_emissions_data_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500  # Internal Server Error

        mock_get.return_value = mock_response

        region_code = "DE"

        fetch_emissions_data(region_code)

        mock_get.assert_called_once_with(
            "https://api.electricitymap.org/v3/"
            f"carbon-intensity/latest?zone={region_code}",
            headers={"Authorization": f"Bearer {os.getenv('ELECTRICITY_MAP_API_KEY')}"},
        )

    @patch("requests.get")
    def test_fetch_emissions_data_empty_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_get.return_value = mock_response

        region_code = "DE"

        fetch_emissions_data(region_code)

        self.assertEqual(EmissionRecord.objects.count(), 0)


class TestFetchHistoricalData(TestCase):
    @patch("emissions.tasks.requests.get")
    def test_fetch_historical_data_success(self, mock_get):
        mock_response_data = {
            "data": [
                {
                    "timestamp": (timezone.now() - timedelta(hours=1)).timestamp(),
                    "carbonIntensity": 200,
                },
                {"timestamp": timezone.now().timestamp(), "carbonIntensity": 180},
            ],
            "zoneName": "Germany",
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response_data

        region_code = "DE"
        fetch_historical_data(region_code, time_range_hours=2, time_step="hour")

        region = Region.objects.get(code=region_code)
        self.assertEqual(region.name, "Germany")

        records = EmissionRecord.objects.filter(region=region)
        self.assertEqual(records.count(), 2)

        first_record = records.first()
        self.assertEqual(first_record.carbon_intensity, 180)
        self.assertEqual(
            first_record.timestamp,
            datetime.fromtimestamp(
                mock_response_data["data"][1]["timestamp"], tz=tz.utc
            ),
        )

        last_record = records.last()
        self.assertEqual(last_record.carbon_intensity, 200)
        self.assertEqual(
            last_record.timestamp,
            datetime.fromtimestamp(
                mock_response_data["data"][0]["timestamp"], tz=tz.utc
            ),
        )

        self.assertEqual(records.count(), 2)

    @patch("emissions.tasks.requests.get")
    def test_fetch_historical_data_api_failure(self, mock_get):
        mock_get.return_value.status_code = 500  # Internal Server Error

        region_code = "DE"
        fetch_historical_data(region_code, time_range_hours=2, time_step="hour")

        records = EmissionRecord.objects.filter(region__code=region_code)
        self.assertEqual(records.count(), 0)

    @patch("emissions.tasks.requests.get")
    def test_fetch_historical_data_empty_response(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": [], "zoneName": "Germany"}

        region_code = "DE"
        fetch_historical_data(region_code, time_range_hours=2, time_step="hour")

        records = EmissionRecord.objects.filter(region__code=region_code)
        self.assertEqual(records.count(), 0)

import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone

from environmental_data.models import (
    HistoricalEnvironmentalRecord,
    RealtimeEnvironmentalRecord,
    Region,
)
from environmental_data.tasks import (
    fetch_realtime_carbon_data,
    fetch_recent_carbon_data,
)

from datetime import timezone as tz


class RealtimeCarbonDataTestCase(TestCase):
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

        fetch_realtime_carbon_data(region_code)

        emission_record = RealtimeEnvironmentalRecord.objects.first()
        self.assertIsNotNone(emission_record)
        self.assertEqual(emission_record.value, 100)

    @patch("requests.get")
    def test_fetch_carbon_data_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500  # Internal Server Error

        mock_get.return_value = mock_response

        region_code = "DE"

        fetch_realtime_carbon_data(region_code)

        mock_get.assert_called_once_with(
            "https://api.electricitymap.org/v3/"
            f"carbon-intensity/latest?zone={region_code}",
            headers={"Authorization": f"Bearer {os.getenv('ELECTRICITY_MAP_API_KEY')}"},
        )

    @patch("requests.get")
    def test_fetch_carbon_data_empty_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_get.return_value = mock_response

        region_code = "DE"

        fetch_realtime_carbon_data(region_code)

        self.assertEqual(RealtimeEnvironmentalRecord.objects.count(), 0)


class TestFetchRecentCarbonlData(TestCase):
    @patch("requests.get")
    def test_fetch_recent_carbon_data_success(self, mock_get):
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
        fetch_recent_carbon_data(region_code, time_range_hours=2, time_step="hour")

        region = Region.objects.get(code=region_code)
        self.assertEqual(region.name, "Germany")

        records = HistoricalEnvironmentalRecord.objects.filter(region=region)
        self.assertEqual(records.count(), 2)

        first_record = records.first()
        self.assertEqual(first_record.value, 180)
        self.assertEqual(
            first_record.timestamp,
            datetime.fromtimestamp(
                mock_response_data["data"][1]["timestamp"], tz=tz.utc
            ),
        )

        last_record = records.last()
        self.assertEqual(last_record.value, 200)
        self.assertEqual(
            last_record.timestamp,
            datetime.fromtimestamp(
                mock_response_data["data"][0]["timestamp"], tz=tz.utc
            ),
        )

        self.assertEqual(records.count(), 2)

    @patch("requests.get")
    def test_fetch_recent_carbon_data_api_failure(self, mock_get):
        mock_get.return_value.status_code = 500  # Internal Server Error

        region_code = "DE"
        fetch_recent_carbon_data(region_code, time_range_hours=2, time_step="hour")

        records = HistoricalEnvironmentalRecord.objects.filter(region__code=region_code)
        self.assertEqual(records.count(), 0)

    @patch("requests.get")
    def test_fetch_recent_carbon_data_empty_response(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": [], "zoneName": "Germany"}

        region_code = "DE"
        fetch_recent_carbon_data(region_code, time_range_hours=2, time_step="hour")

        records = HistoricalEnvironmentalRecord.objects.filter(region__code=region_code)
        self.assertEqual(records.count(), 0)

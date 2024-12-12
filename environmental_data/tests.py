import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone

# from environmental_data.management.commands import import_emissions_data

from environmental_data.models import (
    HistoricalEnvironmentalRecord,
    RealtimeEnvironmentalRecord,
    Country,
    Sector,
    Substance,
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

        country_code = "DE"

        fetch_realtime_carbon_data(country_code)

        emission_record = RealtimeEnvironmentalRecord.objects.first()
        self.assertIsNotNone(emission_record)
        self.assertEqual(emission_record.value, 100)

    @patch("requests.get")
    def test_fetch_carbon_data_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500  # Internal Server Error

        mock_get.return_value = mock_response

        country_code = "DE"

        fetch_realtime_carbon_data(country_code)

        mock_get.assert_called_once_with(
            "https://api.electricitymap.org/v3/"
            f"carbon-intensity/latest?zone={country_code}",
            headers={"Authorization": f"Bearer {os.getenv('ELECTRICITY_MAP_API_KEY')}"},
        )

    @patch("requests.get")
    def test_fetch_carbon_data_empty_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mock_get.return_value = mock_response

        country_code = "DE"

        fetch_realtime_carbon_data(country_code)

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

        country_code = "DE"
        fetch_recent_carbon_data(country_code, time_range_hours=2, time_step="hour")

        country = Country.objects.get(code=country_code)
        self.assertEqual(country.name, "Germany")

        records = RealtimeEnvironmentalRecord.objects.filter(country=country)
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

        country_code = "DE"
        fetch_recent_carbon_data(country_code, time_range_hours=2, time_step="hour")

        records = HistoricalEnvironmentalRecord.objects.filter(
            country__code=country_code
        )
        self.assertEqual(records.count(), 0)

    @patch("requests.get")
    def test_fetch_recent_carbon_data_empty_response(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": [], "zoneName": "Germany"}

        country_code = "DE"
        fetch_recent_carbon_data(country_code, time_range_hours=2, time_step="hour")

        records = HistoricalEnvironmentalRecord.objects.filter(
            country__code=country_code
        )
        self.assertEqual(records.count(), 0)


class HistoricalRecordFilterTests(TestCase):
    def setUp(self):
        # Create Countries
        self.country1 = Country.objects.create(name="Germany", code="DE")
        self.country2 = Country.objects.create(name="France", code="FR")

        # Create Sectors
        self.sector1 = Sector.objects.create(name="Energy")
        self.sector2 = Sector.objects.create(name="Transport")

        # Create Substances
        self.substance1 = Substance.objects.create(name="CO2")
        self.substance2 = Substance.objects.create(name="Methane")

        # Create Historical Records
        HistoricalEnvironmentalRecord.objects.create(
            country=self.country1,
            sector=self.sector1,
            substance=self.substance1,
            year=1990,
            value=100.0,
        )
        HistoricalEnvironmentalRecord.objects.create(
            country=self.country1,
            sector=self.sector2,
            substance=self.substance2,
            year=2000,
            value=150.0,
        )
        HistoricalEnvironmentalRecord.objects.create(
            country=self.country2,
            sector=self.sector1,
            substance=self.substance1,
            year=1985,
            value=200.0,
        )

    def test_filter_by_country_code(self):
        response = self.client.get(
            "/environmental_data/api/historical-data/", {"country": "DE"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)  # Two records for country DE
        self.assertTrue(all(record["country"]["code"] == "DE" for record in data))

    def test_filter_by_sector(self):
        response = self.client.get(
            "/environmental_data/api/historical-data/", {"sector": "Energy"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)  # Two records for the Energy sector
        self.assertTrue(all(record["sector"]["name"] == "Energy" for record in data))

    def test_filter_by_year_range(self):
        response = self.client.get(
            "/environmental_data/api/historical-data/",
            {"start_year": 1980, "end_year": 1995},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)  # Two records between 1980 and 1995
        self.assertTrue(all(1980 <= record["year"] <= 1995 for record in data))

    def test_combined_filters(self):
        response = self.client.get(
            "/environmental_data/api/historical-data/",
            {
                "country_code": "DE",
                "sector": "Transport",
                "start_year": 1990,
                "end_year": 2010,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)  # One record matching all criteria
        self.assertEqual(data[0]["country"]["code"], "DE")
        self.assertEqual(data[0]["sector"]["name"], "Transport")
        self.assertEqual(data[0]["year"], 2000)

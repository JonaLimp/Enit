import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone

from environmental_data.models import (
    RealtimeEnvironmentalRecord,
)
from environmental_data.tasks import (
    fetch_realtime_carbon_data,
    fetch_recent_carbon_data,
)


from environmental_data.models import (
    HistoricalEnvironmentalRecord,
    Country,
    Sector,
    Substance,
)
from environmental_data.views import CountryTotalDataView
from rest_framework.test import APIRequestFactory


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


class FilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up test data
        cls.germany = Country.objects.create(name="Germany", code="DE")
        cls.france = Country.objects.create(name="France", code="FR")

        cls.energy = Sector.objects.create(name="Energy")
        cls.transport = Sector.objects.create(name="Transport")

        cls.co2 = Substance.objects.create(name="CO2")

        HistoricalEnvironmentalRecord.objects.create(
            country=cls.germany,
            sector=cls.energy,
            substance=cls.co2,
            value=229639.50,
            year=2020,
        )
        HistoricalEnvironmentalRecord.objects.create(
            country=cls.germany,
            sector=cls.transport,
            substance=cls.co2,
            value=144180.14,
            year=2021,
        )
        HistoricalEnvironmentalRecord.objects.create(
            country=cls.france,
            sector=cls.energy,
            substance=cls.co2,
            value=38285.24,
            year=2020,
        )

    def test_filter_by_country(self):
        factory = APIRequestFactory()
        request = factory.get(
            "/environmental-data/api/total-environmental-data/", {"country": "Germany"}
        )

        view = CountryTotalDataView.as_view()

        response = view(request)

        self.assertEqual(response.status_code, 200)

        data = response.data

        self.assertIn("Germany", data)
        self.assertEqual(len(data["Germany"]["Total"]), 2)

    def test_filter_by_country_and_sector(self):
        factory = APIRequestFactory()
        request = factory.get(
            "/environmental-data/api/total-environmental-data/",
            {"country": "Germany", "sector": "Energy"},
        )
        view = CountryTotalDataView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn("Germany", data)
        self.assertEqual(len(data["Germany"]), 1)

    def test_filter_by_multiple_countries(self):
        factory = APIRequestFactory()
        request = factory.get(
            "/environmental-data/api/total-environmental-data/",
            {"country": "Germany,France"},
        )
        view = CountryTotalDataView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn("Germany", data)
        self.assertIn("France", data)

    def test_filter_by_year_range(self):
        factory = APIRequestFactory()
        request = factory.get(
            "/environmental-data/api/total-environmental-data/",
            {"country": "Germany", "start_year": 2020, "end_year": 2021},
        )
        view = CountryTotalDataView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn("Germany", data)
        self.assertEqual(len(data["Germany"]["Total"]), 2)

    def test_filter_by_all_parameters(self):
        factory = APIRequestFactory()
        request = factory.get(
            "/environmental-data/api/total-environmental-data/",
            {
                "country": "France",
                "sector": "Energy",
                "start_year": 2020,
                "end_year": 2020,
            },
        )
        view = CountryTotalDataView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn("France", data)
        self.assertEqual(len(data["France"]["Total"]), 1)

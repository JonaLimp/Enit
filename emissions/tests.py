import os
from unittest.mock import patch, MagicMock
from django.test import TestCase

from emissions.models import EmissionRecord
from emissions.tasks import fetch_emissions_data


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
        # Create a mock response object for failure
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
        # Create a mock response object with an empty body
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        # Mock the requests.get call to return the empty response
        mock_get.return_value = mock_response

        region_code = "DE"

        # Call the function
        fetch_emissions_data(region_code)

        # Ensure no emission record was created
        self.assertEqual(EmissionRecord.objects.count(), 0)

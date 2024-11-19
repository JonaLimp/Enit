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

        region_code = "EU"

        fetch_emissions_data(region_code)

        mock_get.assert_called_once_with(
            "https://api.electricitymap.org/"
            "v3/carbon-intensity/latest?zone={region_code}",
            headers={"Authorization": f"Bearer {os.getenv('ELECTRICITY_MAP_API_KEY')}"},
        )

        emission_record = EmissionRecord.objects.first()
        self.assertIsNotNone(emission_record)
        self.assertEqual(emission_record.carbon_intensity, 100)

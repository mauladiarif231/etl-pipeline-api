import pytest
import os
import sys
from unittest.mock import patch, Mock
import requests

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from integrations.geocode_util import get_structured_address, GeocodingError

class TestGeocodeUtil:
    
    @patch.dict(os.environ, {'LOCATIONIQ_API_KEY': 'pk.2293b5f90b2057ebe343c0e11f2f222b'})
    @patch('integrations.geocode_util.requests.get')
    @patch('integrations.geocode_util.time.sleep')
    def test_successful_geocoding(self, mock_sleep, mock_get):
        """Test successful geocoding with multiple results"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {
                'display_name': 'Bahnhofquai, City, Altstadt, Zurich, District Zurich, Zurich, 8001, Switzerland',
                'lat': '47.3768866',
                'lon': '8.5418596'
            },
            {
                'display_name': 'Bahnhofquai, Lindenhof, Altstadt, Zurich, District Zurich, Zurich, 8001, Switzerland',
                'lat': '47.3758222',
                'lon': '8.5419804'
            }
        ]
        mock_get.return_value = mock_response
        
        results = get_structured_address("Bahnhofquai 8")
        
        assert len(results) == 2
        assert results[0]['full_address'] == 'Bahnhofquai, City, Altstadt, Zurich, District Zurich, Zurich, 8001, Switzerland'
        assert results[0]['latitude'] == '47.3768866'
        assert results[0]['longitude'] == '8.5418596'
        
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert 'us1.locationiq.com' in args[0]
        assert kwargs['params']['q'] == 'Bahnhofquai 8'
        assert kwargs['params']['key'] == 'pk.2293b5f90b2057ebe343c0e11f2f222b'
    
    def test_empty_address(self):
        """Test error handling for empty address"""
        with pytest.raises(GeocodingError, match="Address cannot be empty"):
            get_structured_address("")
        with pytest.raises(GeocodingError, match="Address cannot be empty"):
            get_structured_address("   ")
        with pytest.raises(GeocodingError, match="Address cannot be empty"):
            get_structured_address(None)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self):
        """Test error handling when API key is missing"""
        with pytest.raises(GeocodingError, match="LOCATIONIQ_API_KEY not found"):
            get_structured_address("Test Address")
    
    @patch.dict(os.environ, {'LOCATIONIQ_API_KEY': 'test_api_key'})
    @patch('integrations.geocode_util.requests.get')
    @patch('integrations.geocode_util.time.sleep')
    def test_no_results(self, mock_sleep, mock_get):
        """Test handling when API returns no results"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        with pytest.raises(GeocodingError, match="No geocoding results found"):
            get_structured_address("Invalid Address")
    
    @patch.dict(os.environ, {'LOCATIONIQ_API_KEY': 'test_api_key'})
    @patch('integrations.geocode_util.requests.get')
    @patch('integrations.geocode_util.time.sleep')
    def test_api_error(self, mock_sleep, mock_get):
        """Test handling of API errors"""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        with pytest.raises(GeocodingError, match="API request failed"):
            get_structured_address("Test Address")
    
    @patch.dict(os.environ, {'LOCATIONIQ_API_KEY': 'test_api_key'})
    @patch('integrations.geocode_util.requests.get')
    @patch('integrations.geocode_util.time.sleep')
    def test_invalid_json_response(self, mock_sleep, mock_get):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        with pytest.raises(GeocodingError, match="Invalid JSON response"):
            get_structured_address("Test Address")
    
    @patch.dict(os.environ, {'LOCATIONIQ_API_KEY': 'test_api_key'})
    @patch('integrations.geocode_util.requests.get')
    @patch('integrations.geocode_util.time.sleep')
    def test_missing_coordinates(self, mock_sleep, mock_get):
        """Test handling when coordinates are missing from response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {
                'display_name': 'Test Address',
                'lat': '',
                'lon': '8.5417'
            }
        ]
        mock_get.return_value = mock_response
        
        with pytest.raises(GeocodingError, match="No valid coordinates returned"):
            get_structured_address("Test Address")
    
    @patch.dict(os.environ, {'LOCATIONIQ_API_KEY': 'test_api_key'})
    @patch('integrations.geocode_util.requests.get')
    @patch('integrations.geocode_util.time.sleep')
    def test_http_error(self, mock_sleep, mock_get):
        """Test handling of HTTP errors"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with pytest.raises(GeocodingError, match="API request failed"):
            get_structured_address("Test Address")
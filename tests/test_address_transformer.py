import pytest
import sys
import os
from unittest.mock import patch, Mock

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from transformers.address_transformer import AddressTransformer
from integrations.geocode_util import GeocodingError

class TestAddressTransformer:
    
    @patch('transformers.address_transformer.get_structured_address')
    def test_successful_transformation(self, mock_geocode):
        """Test successful address transformation"""
        mock_geocode.return_value = [
            {
                'full_address': 'Bahnhofquai, City, Altstadt, Zurich, District Zurich, Zurich, 8001, Switzerland',
                'latitude': '47.3768866',
                'longitude': '8.5418596'
            },
            {
                'full_address': 'Bahnhofquai, Lindenhof, Altstadt, Zurich, District Zurich, Zurich, 8001, Switzerland',
                'latitude': '47.3758222',
                'longitude': '8.5419804'
            }
        ]
        
        input_data = [
            {
                "publication_media": "Neue Zürcher Zeitung",
                "project_title": "Test Project",
                "date_scraped": "15/03/2024 14:23:45",
                "project_address": "Bahnhofquai 8"
            }
        ]
        
        transformer = AddressTransformer()
        results = list(transformer.transform(iter(input_data)))
        
        assert len(results) == 1
        result = results[0]
        
        assert result["publication_media"] == "Neue Zürcher Zeitung"
        assert result["project_title"] == "Test Project"
        assert result["project_address"] == "Bahnhofquai 8"
        
        assert len(result["geocoded_addresses"]) >= 1  # Allow multiple results
        assert result["geocoded_addresses"][0]["full_address"] == "Bahnhofquai, City, Altstadt, Zurich, District Zurich, Zurich, 8001, Switzerland"
        assert result["full_address"] == "Bahnhofquai, City, Altstadt, Zurich, District Zurich, Zurich, 8001, Switzerland"
        assert result["latitude"] == "47.3768866"
        assert result["longitude"] == "8.5418596"
        assert result["geocoding_status"] == "success"
        
        mock_geocode.assert_called_once_with("Bahnhofquai 8")
    
    @patch('transformers.address_transformer.get_structured_address')
    def test_multiple_records_transformation(self, mock_geocode):
        """Test transformation of multiple records"""
        def mock_geocode_side_effect(address):
            if address == "Bahnhofquai 8":
                return [
                    {
                        'full_address': 'Bahnhofquai, City, Altstadt, Zurich, District Zurich, Zurich, 8001, Switzerland',
                        'latitude': '47.3768866',
                        'longitude': '8.5418596'
                    }
                ]
            elif address == "Via San Gottardo 39":
                return [
                    {
                        'full_address': 'Via San Gottardo 39, 6900 Lugano, Switzerland',
                        'latitude': '46.0037',
                        'longitude': '8.9511'
                    },
                    {
                        'full_address': 'Via San Gottardo 39, Bellinzona, Switzerland',
                        'latitude': '46.192',
                        'longitude': '9.024'
                    }
                ]
        
        mock_geocode.side_effect = mock_geocode_side_effect
        
        input_data = [
            {
                "publication_media": "Neue Zürcher Zeitung",
                "project_address": "Bahnhofquai 8"
            },
            {
                "publication_media": "Tages-Anzeiger",
                "project_address": "Via San Gottardo 39"
            }
        ]
        
        transformer = AddressTransformer()
        results = list(transformer.transform(iter(input_data)))
        
        assert len(results) == 2
        
        assert results[0]["project_address"] == "Bahnhofquai 8"
        assert results[0]["latitude"] == "47.3768866"
        assert results[0]["geocoding_status"] == "success"
        assert len(results[0]["geocoded_addresses"]) >= 1
        
        assert results[1]["project_address"] == "Via San Gottardo 39"
        assert results[1]["latitude"] == "46.0037"
        assert results[1]["geocoding_status"] == "success"
        assert len(results[1]["geocoded_addresses"]) >= 1
        assert any(addr["full_address"] == "Via San Gottardo 39, Bellinzona, Switzerland" for addr in results[1]["geocoded_addresses"])
    
    def test_empty_address_handling(self):
        """Test handling of records with empty addresses"""
        input_data = [
            {
                "publication_media": "Test Media",
                "project_address": ""
            },
            {
                "publication_media": "Test Media 2",
                "project_address": "   "
            },
            {
                "publication_media": "Test Media 3"
            }
        ]
        
        transformer = AddressTransformer()
        results = list(transformer.transform(iter(input_data)))
        
        assert len(results) == 3
        
        for result in results:
            assert result["geocoded_addresses"] == []
            assert result["full_address"] == ""
            assert result["latitude"] == ""
            assert result["longitude"] == ""
            assert result["geocoding_status"] == "no_address"
    
    @patch('transformers.address_transformer.get_structured_address')
    def test_geocoding_error_handling(self, mock_geocode):
        """Test handling of geocoding errors"""
        mock_geocode.side_effect = GeocodingError("No results found")
        
        input_data = [
            {
                "publication_media": "Test Media",
                "project_address": "Invalid Address"
            }
        ]
        
        transformer = AddressTransformer()
        results = list(transformer.transform(iter(input_data)))
        
        assert len(results) == 1
        result = results[0]
        
        assert result["project_address"] == "Invalid Address"
        assert result["geocoded_addresses"] == []
        assert result["full_address"] == "Invalid Address"
        assert result["latitude"] == ""
        assert result["longitude"] == ""
        assert result["geocoding_status"] == "failed"
        assert result["geocoding_error"] == "No results found"
    
    @patch('transformers.address_transformer.get_structured_address')
    def test_unexpected_error_handling(self, mock_geocode):
        """Test handling of unexpected errors during geocoding"""
        mock_geocode.side_effect = Exception("Unexpected error")
        
        input_data = [
            {
                "publication_media": "Test Media",
                "project_address": "Test Address"
            }
        ]
        
        transformer = AddressTransformer()
        results = list(transformer.transform(iter(input_data)))
        
        assert len(results) == 1
        result = results[0]
        
        assert result["project_address"] == "Test Address"
        assert result["geocoded_addresses"] == []
        assert result["full_address"] == "Test Address"
        assert result["latitude"] == ""
        assert result["longitude"] == ""
        assert result["geocoding_status"] == "error"
        assert result["geocoding_error"] == "Unexpected error"
    
    def test_non_dict_record_handling(self):
        """Test handling of non-dictionary records"""
        input_data = [
            {"publication_media": "Valid Record", "project_address": "Test"},
            "invalid_string_record",
            {"publication_media": "Another Valid Record", "project_address": "Test2"}
        ]
        
        transformer = AddressTransformer()
        results = list(transformer.transform(iter(input_data)))
        
        assert len(results) == 2
        assert results[0]["publication_media"] == "Valid Record"
        assert results[1]["publication_media"] == "Another Valid Record"
    
    @patch('transformers.address_transformer.get_structured_address')
    def test_mixed_success_and_failure(self, mock_geocode):
        """Test handling of mixed success and failure cases"""
        def mock_geocode_side_effect(address):
            if address == "Good Address":
                return [
                    {
                        'full_address': 'Good Address, City, Country',
                        'latitude': '47.0000',
                        'longitude': '8.0000'
                    }
                ]
            else:
                raise GeocodingError("Bad address")
        
        mock_geocode.side_effect = mock_geocode_side_effect
        
        input_data = [
            {"publication_media": "Media 1", "project_address": "Good Address"},
            {"publication_media": "Media 2", "project_address": "Bad Address"},
            {"publication_media": "Media 3", "project_address": ""}
        ]
        
        transformer = AddressTransformer()
        results = list(transformer.transform(iter(input_data)))
        
        assert len(results) == 3
        
        assert results[0]["geocoding_status"] == "success"
        assert results[0]["latitude"] == "47.0000"
        assert len(results[0]["geocoded_addresses"]) >= 1
        
        assert results[1]["geocoding_status"] == "failed"
        assert results[1]["latitude"] == ""
        assert results[1]["geocoded_addresses"] == []
        assert "geocoding_error" in results[1]
        
        assert results[2]["geocoding_status"] == "no_address"
        assert results[2]["latitude"] == ""
        assert results[2]["geocoded_addresses"] == []
    
    def test_original_data_preservation(self):
        """Test that original data is preserved during transformation"""
        input_data = [
            {
                "publication_media": "Test Media",
                "project_title": "Complex Project Title with Special Characters: àéïöü",
                "date_scraped": "15/03/2024 14:23:45",
                "project_address": "",
                "custom_field": "custom_value",
                "numeric_field": 42,
                "boolean_field": True,
                "nested_object": {"key": "value"}
            }
        ]
        
        transformer = AddressTransformer()
        results = list(transformer.transform(iter(input_data)))
        
        assert len(results) == 1
        result = results[0]
        
        assert result["publication_media"] == "Test Media"
        assert result["project_title"] == "Complex Project Title with Special Characters: àéïöü"
        assert result["date_scraped"] == "15/03/2024 14:23:45"
        assert result["custom_field"] == "custom_value"
        assert result["numeric_field"] == 42
        assert result["boolean_field"] is True
        assert result["nested_object"] == {"key": "value"}
        assert result["geocoded_addresses"] == []
        assert "full_address" in result
        assert "latitude" in result
        assert "longitude" in result
        assert "geocoding_status" in result
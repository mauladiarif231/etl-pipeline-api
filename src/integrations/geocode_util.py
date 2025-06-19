import requests
import os
from dotenv import load_dotenv
import time
from typing import Dict, List

load_dotenv()

class GeocodingError(Exception):
    """Custom exception for geocoding errors"""
    pass

def get_structured_address(partial_address: str) -> List[Dict[str, str]]:
    """
    Given a partial address, returns all structured addresses using LocationIQ API.
    
    Args:
        partial_address (str): The partial address to geocode
        
    Returns:
        List[Dict[str, str]]: List of dictionaries containing full_address, latitude, and longitude
        
    Raises:
        GeocodingError: When geocoding fails or API returns no results
    """
    if not partial_address or not partial_address.strip():
        raise GeocodingError("Address cannot be empty")
    
    api_key = os.getenv('LOCATIONIQ_API_KEY')
    if not api_key:
        raise GeocodingError("LOCATIONIQ_API_KEY not found in environment variables")
    
    url = "https://us1.locationiq.com/v1/search.php"
    
    params = {
        'key': api_key,
        'q': partial_address.strip(),
        'format': 'json',
        'addressdetails': 1
    }
    
    try:
        time.sleep(0.1)  # Respect rate limits
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data or len(data) == 0:
            raise GeocodingError(f"No geocoding results found for address: {partial_address}")
        
        results = []
        for result in data:
            full_address = result.get('display_name', partial_address)
            latitude = result.get('lat', '')
            longitude = result.get('lon', '')
            if latitude and longitude:
                results.append({
                    'full_address': full_address,
                    'latitude': latitude,
                    'longitude': longitude
                })
        
        if not results:
            raise GeocodingError(f"No valid coordinates returned for address: {partial_address}")
        
        return results
    
    except requests.exceptions.RequestException as e:
        raise GeocodingError(f"API request failed for address '{partial_address}': {str(e)}")
    except ValueError as e:
        raise GeocodingError(f"Invalid JSON response for address '{partial_address}': {str(e)}")
    except Exception as e:
        raise GeocodingError(f"Unexpected error geocoding address '{partial_address}': {str(e)}")
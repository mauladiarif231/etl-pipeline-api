from typing import Iterator, Dict, Any
import logging
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from integrations.geocode_util import get_structured_address, GeocodingError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AddressTransformer:
    def __init__(self):
        self.geocoder = get_structured_address

    def transform(self, address_iter: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Transforms an iterator of address dictionaries by enriching each address.
        Yields enriched addresses one by one.
        
        Args:
            address_iter (Iterator[Dict[str, Any]]): Iterator of address dictionaries
        
        Yields:
            Dict[str, Any]: Enriched address dictionaries with geocoding data
        """
        for record in address_iter:
            if not isinstance(record, dict):
                logger.warning(f"Skipping non-dict record: {type(record)}")
                continue
            
            enriched_record = record.copy()
            address = record.get('project_address', '').strip()
            
            if not address:
                logger.warning(f"No address found in record: {record}")
                enriched_record.update({
                    'geocoded_addresses': [],
                    'full_address': '',
                    'latitude': '',
                    'longitude': '',
                    'geocoding_status': 'no_address'
                })
                yield enriched_record
                continue
            
            try:
                geocoding_results = self.geocoder(address)
                if geocoding_results:
                    enriched_record.update({
                        'geocoded_addresses': geocoding_results,
                        'full_address': geocoding_results[0]['full_address'],
                        'latitude': geocoding_results[0]['latitude'],
                        'longitude': geocoding_results[0]['longitude'],
                        'geocoding_status': 'success'
                    })
                    logger.info(f"Successfully geocoded address: {address}")
                else:
                    enriched_record.update({
                        'geocoded_addresses': [],
                        'full_address': address,
                        'latitude': '',
                        'longitude': '',
                        'geocoding_status': 'failed'
                    })
            except GeocodingError as e:
                logger.error(f"Geocoding failed for address '{address}': {str(e)}")
                enriched_record.update({
                    'geocoded_addresses': [],
                    'full_address': address,
                    'latitude': '',
                    'longitude': '',
                    'geocoding_status': 'failed',
                    'geocoding_error': str(e)
                })
            except Exception as e:
                logger.error(f"Unexpected error processing address '{address}': {str(e)}")
                enriched_record.update({
                    'geocoded_addresses': [],
                    'full_address': address,
                    'latitude': '',
                    'longitude': '',
                    'geocoding_status': 'error',
                    'geocoding_error': str(e)
                })
            
            yield enriched_record
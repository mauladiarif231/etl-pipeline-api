import json
import os
from typing import Iterator, Dict, Any, List

def write_json(data: Iterator[Dict[str, Any]], path: str) -> None:
    """
    Writes an iterator of dicts to a JSON file.
    
    Args:
        data (Iterator[Dict[str, Any]]): An iterator of dictionaries to write to the JSON file.
        path (str): The file path where the JSON data will be written.
        
    Raises:
        ValueError: When path is empty or data is invalid
        OSError: When there are file system issues
    """
    if not path:
        raise ValueError("Path cannot be empty")
    
    if not isinstance(path, str):
        raise ValueError("Path must be a string")
    
    # Ensure the directory exists
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as e:
            raise OSError(f"Failed to create directory {directory}: {str(e)}")
    
    # Convert iterator to list to handle serialization
    try:
        records: List[Dict[str, Any]] = []
        for record in data:
            if not isinstance(record, dict):
                raise ValueError(f"Expected dict record, got {type(record)}")
            records.append(record)
        
        # Write to file with proper JSON formatting
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(records, file, indent=2, ensure_ascii=False)
            
    except ValueError as e:
        raise ValueError(f"Failed to serialize data to JSON: {str(e)}")
    except OSError as e:
        raise OSError(f"Failed to write to file {path}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error writing JSON: {str(e)}")
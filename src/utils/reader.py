import json
import os
from typing import Iterator, Dict, Any
import glob

def read_json(path: str) -> Iterator[Dict[str, Any]]:
    """
    Reads JSON files from a specified directory and yields each record.
    
    Args:
        path (str): The directory containing JSON files or path to a single JSON file.
        
    Yields:
        dict: Each record from the JSON files.
        
    Raises:
        FileNotFoundError: When the specified path doesn't exist
        ValueError: When JSON files are malformed
        OSError: When there are permission issues
    """
    if not path:
        raise ValueError("Path cannot be empty")
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")
    
    # Handle both single file and directory paths
    if os.path.isfile(path):
        json_files = [path]
    elif os.path.isdir(path):
        # Find all JSON files in the directory
        json_files = glob.glob(os.path.join(path, "*.json"))
        if not json_files:
            raise FileNotFoundError(f"No JSON files found in directory: {path}")
    else:
        raise ValueError(f"Path is neither a file nor a directory: {path}")
    
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Handle both single objects and arrays
                if isinstance(data, list):
                    for record in data:
                        if isinstance(record, dict):
                            yield record
                        else:
                            raise ValueError(f"Expected dict record, got {type(record)} in file: {json_file}")
                elif isinstance(data, dict):
                    yield data
                else:
                    raise ValueError(f"Expected dict or list, got {type(data)} in file: {json_file}")
                    
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in file {json_file}: {str(e)}")
        except IOError as e:
            raise OSError(f"Error reading file {json_file}: {str(e)}")
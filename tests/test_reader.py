import pytest
import json
import os
import tempfile
import shutil
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.reader import read_json

class TestReader:
    
    def setup_method(self):
        """Set up temporary directory for tests"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)
    
    def test_read_single_json_file_with_array(self):
        """Test reading a single JSON file containing an array"""
        test_data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
        
        file_path = os.path.join(self.temp_dir, "test.json")
        with open(file_path, 'w') as f:
            json.dump(test_data, f)
        
        records = list(read_json(file_path))
        
        assert len(records) == 2
        assert records[0] == {"name": "John", "age": 30}
        assert records[1] == {"name": "Jane", "age": 25}
    
    def test_read_single_json_file_with_object(self):
        """Test reading a single JSON file containing a single object"""
        test_data = {"name": "John", "age": 30}
        
        file_path = os.path.join(self.temp_dir, "test.json")
        with open(file_path, 'w') as f:
            json.dump(test_data, f)
        
        records = list(read_json(file_path))
        
        assert len(records) == 1
        assert records[0] == {"name": "John", "age": 30}
    
    def test_read_directory_with_multiple_json_files(self):
        """Test reading multiple JSON files from a directory"""
        # Create first file
        test_data1 = [{"id": 1, "name": "File1"}]
        file_path1 = os.path.join(self.temp_dir, "file1.json")
        with open(file_path1, 'w') as f:
            json.dump(test_data1, f)
        
        # Create second file
        test_data2 = [{"id": 2, "name": "File2"}]
        file_path2 = os.path.join(self.temp_dir, "file2.json")
        with open(file_path2, 'w') as f:
            json.dump(test_data2, f)
        
        records = list(read_json(self.temp_dir))
        
        assert len(records) == 2
        # Records should be sorted by filename
        assert records[0] == {"id": 1, "name": "File1"}
        assert records[1] == {"id": 2, "name": "File2"}
    
    def test_read_empty_directory(self):
        """Test reading from directory with no JSON files"""
        with pytest.raises(FileNotFoundError, match="No JSON files found"):
            list(read_json(self.temp_dir))
    
    def test_read_nonexistent_path(self):
        """Test reading from non-existent path"""
        with pytest.raises(FileNotFoundError, match="Path does not exist"):
            list(read_json("/non/existent/path"))
    
    def test_read_empty_path(self):
        """Test reading with empty path"""
        with pytest.raises(ValueError, match="Path cannot be empty"):
            list(read_json(""))
    
    def test_read_invalid_json(self):
        """Test reading file with invalid JSON"""
        file_path = os.path.join(self.temp_dir, "invalid.json")
        with open(file_path, 'w') as f:
            f.write("{ invalid json }")
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            list(read_json(file_path))
    
    def test_read_json_with_non_dict_records(self):
        """Test reading JSON file with non-dict records in array"""
        test_data = [{"name": "John"}, "invalid_record", {"name": "Jane"}]
        
        file_path = os.path.join(self.temp_dir, "test.json")
        with open(file_path, 'w') as f:
            json.dump(test_data, f)
        
        with pytest.raises(ValueError, match="Expected dict record"):
            list(read_json(file_path))
    
    def test_read_json_with_primitive_data(self):
        """Test reading JSON file with primitive data (not dict or array)"""
        file_path = os.path.join(self.temp_dir, "primitive.json")
        with open(file_path, 'w') as f:
            json.dump("just a string", f)
        
        with pytest.raises(ValueError, match="Expected dict or list"):
            list(read_json(file_path))
    
    def test_read_directory_with_mixed_files(self):
        """Test reading directory with JSON and non-JSON files"""
        # Create JSON file
        test_data = [{"id": 1, "name": "Test"}]
        json_file = os.path.join(self.temp_dir, "data.json")
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        # Create non-JSON file
        txt_file = os.path.join(self.temp_dir, "readme.txt")
        with open(txt_file, 'w') as f:
            f.write("This is not JSON")
        
        records = list(read_json(self.temp_dir))
        
        # Should only read JSON files
        assert len(records) == 1
        assert records[0] == {"id": 1, "name": "Test"}
    
    def test_read_sample_input_format(self):
        """Test reading the specific format from the assignment"""
        test_data = [
            {
                "publication_media": "Neue Zürcher Zeitung",
                "project_title": "Neubau eines Spielplatzes",
                "date_scraped": "15/03/2024 14:23:45",
                "project_address": "Bahnhofquai 8"
            },
            {
                "publication_media": "Tages-Anzeiger",
                "project_title": "Sanierung der Fassade",
                "date_scraped": "22/04/2024 09:11:32",
                "project_address": "Via San Gottardo 39"
            }
        ]
        
        file_path = os.path.join(self.temp_dir, "input_sample.json")
        with open(file_path, 'w') as f:
            json.dump(test_data, f)
        
        records = list(read_json(file_path))
        
        assert len(records) == 2
        assert records[0]["publication_media"] == "Neue Zürcher Zeitung"
        assert records[0]["project_address"] == "Bahnhofquai 8"
        assert records[1]["publication_media"] == "Tages-Anzeiger"
        assert records[1]["project_address"] == "Via San Gottardo 39"
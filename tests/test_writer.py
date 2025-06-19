import pytest
import json
import os
import tempfile
import shutil
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.writer import write_json

class TestWriter:
    
    def setup_method(self):
        """Set up temporary directory for tests"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)
    
    def test_write_json_list_of_dicts(self):
        """Test writing a list of dictionaries to JSON file"""
        test_data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
        
        file_path = os.path.join(self.temp_dir, "output.json")
        write_json(iter(test_data), file_path)
        
        # Verify file was created and contains correct data
        assert os.path.exists(file_path)
        
        with open(file_path, 'r') as f:
            written_data = json.load(f)
        
        assert len(written_data) == 2
        assert written_data[0] == {"name": "John", "age": 30}
        assert written_data[1] == {"name": "Jane", "age": 25}
    
    def test_write_json_single_dict(self):
        """Test writing a single dictionary to JSON file"""
        test_data = [{"name": "John", "age": 30}]
        
        file_path = os.path.join(self.temp_dir, "single.json")
        write_json(iter(test_data), file_path)
        
        with open(file_path, 'r') as f:
            written_data = json.load(f)
        
        assert len(written_data) == 1
        assert written_data[0] == {"name": "John", "age": 30}
    
    def test_write_json_empty_iterator(self):
        """Test writing empty iterator"""
        file_path = os.path.join(self.temp_dir, "empty.json")
        write_json(iter([]), file_path)
        
        with open(file_path, 'r') as f:
            written_data = json.load(f)
        
        assert written_data == []
    
    def test_write_json_creates_directory(self):
        """Test that writer creates directory if it doesn't exist"""
        nested_path = os.path.join(self.temp_dir, "nested", "dir", "output.json")
        test_data = [{"test": "data"}]
        
        write_json(iter(test_data), nested_path)
        
        assert os.path.exists(nested_path)
        
        with open(nested_path, 'r') as f:
            written_data = json.load(f)
        
        assert written_data == [{"test": "data"}]
    
    def test_write_json_empty_path(self):
        """Test writing with empty path"""
        with pytest.raises(ValueError, match="Path cannot be empty"):
            write_json(iter([{"test": "data"}]), "")
    
    def test_write_json_invalid_path_type(self):
        """Test writing with non-string path"""
        with pytest.raises(ValueError, match="Path must be a string"):
            write_json(iter([{"test": "data"}]), 123)
    
    def test_write_json_non_dict_data(self):
        """Test writing non-dictionary data"""
        test_data = [{"valid": "dict"}, "invalid_string", {"another": "dict"}]
        file_path = os.path.join(self.temp_dir, "invalid.json")
        
        with pytest.raises(ValueError, match="Expected dict record"):
            write_json(iter(test_data), file_path)
    
    def test_write_json_with_unicode(self):
        """Test writing JSON with Unicode characters"""
        test_data = [
            {"name": "José", "city": "Zürich"},
            {"description": "测试数据", "emoji": "🎉"}
        ]
        
        file_path = os.path.join(self.temp_dir, "unicode.json")
        write_json(iter(test_data), file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            written_data = json.load(f)
        
        assert written_data[0]["name"] == "José"
        assert written_data[0]["city"] == "Zürich"
        assert written_data[1]["description"] == "测试数据"
        assert written_data[1]["emoji"] == "🎉"
    
    def test_write_json_enriched_format(self):
        """Test writing enriched data format from the assignment"""
        enriched_data = [
            {
                "publication_media": "Neue Zürcher Zeitung",
                "project_title": "Neubau eines Spielplatzes",
                "date_scraped": "15/03/2024 14:23:45",
                "project_address": "Bahnhofquai 8",
                "full_address": "Bahnhofquai 8, 8001 Zürich, Switzerland",
                "latitude": "47.3769",
                "longitude": "8.5417",
                "geocoding_status": "success"
            }
        ]
        
        file_path = os.path.join(self.temp_dir, "enriched.json")
        write_json(iter(enriched_data), file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            written_data = json.load(f)
        
        assert len(written_data) == 1
        record = written_data[0]
        assert record["project_address"] == "Bahnhofquai 8"
        assert record["full_address"] == "Bahnhofquai 8, 8001 Zürich, Switzerland"
        assert record["latitude"] == "47.3769"
        assert record["longitude"] == "8.5417"
        assert record["geocoding_status"] == "success"
    
    def test_write_json_permission_error(self):
        """Test handling of permission errors"""
        # Create a read-only file to simulate a permission error
        file_path = os.path.join(self.temp_dir, "test.json")
        with open(file_path, 'w') as f:
            f.write("")  # Create an empty file
        
        # Make the file read-only
        os.chmod(file_path, 0o444)
        
        test_data = [{"test": "data"}]
        
        try:
            with pytest.raises(OSError, match="Failed to write to file"):
                write_json(iter(test_data), file_path)
        finally:
            # Restore permissions for cleanup
            os.chmod(file_path, 0o666)
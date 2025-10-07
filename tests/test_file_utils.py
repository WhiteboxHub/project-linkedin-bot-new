"""
Tests for file_utils.py functionality
"""
import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_utils import load_yaml_config, save_application_data

@pytest.fixture
def test_config():
    """Test configuration fixture"""
    return {
        'username': 'test@example.com',
        'password': 'password123'
    }

@pytest.fixture
def test_application_data():
    """Test application data fixture"""
    return {
        'job_id': '123456',
        'job_title': 'ML Engineer',
        'company': 'Test Company',
        'location': 'San Francisco, CA',
        'application_status': 'Applied'
    }

def test_load_yaml_config_success(mocker, test_config):
    """Test loading YAML config successfully"""
    # Setup mock
    mock_yaml_load = mocker.patch('yaml.safe_load', return_value=test_config)
    mock_file = mocker.patch('builtins.open', mocker.mock_open())
    
    # Call the function
    result = load_yaml_config('test_config.yaml')
    
    # Verify file was opened correctly
    mock_file.assert_called_once_with('test_config.yaml', 'r', encoding='utf-8')
    
    # Verify YAML was loaded
    mock_yaml_load.assert_called_once()
    
    # Verify result
    assert result == test_config

def test_load_yaml_config_error(mocker):
    """Test handling error when loading YAML config"""
    # Setup mock to raise exception
    mocker.patch('yaml.safe_load', side_effect=Exception("YAML error"))
    mocker.patch('builtins.open', mocker.mock_open())
    
    # Call the function with print capture
    mock_print = mocker.patch('builtins.print')
    result = load_yaml_config('test_config.yaml')
        
    # Verify error was printed
    mock_print.assert_called_once()
    assert "Error loading config file" in mock_print.call_args[0][0]
    
    # Verify None was returned
    assert result is None

def test_save_application_data_new_file(mocker, test_application_data):
    """Test saving application data to a new CSV file"""
    # Setup mocks
    mocker.patch('os.makedirs')
    mocker.patch('os.path.isfile', return_value=False)
    mock_file = mocker.patch('builtins.open', mocker.mock_open())
    mock_writer = mocker.MagicMock()
    mocker.patch('csv.DictWriter', return_value=mock_writer)
    
    # Call the function
    save_application_data(test_application_data, 'output/applications/test.csv')
    
    # Verify directory was created
    os.makedirs.assert_called_once_with('output/applications', exist_ok=True)
    
    # Verify file was checked
    os.path.isfile.assert_called_once_with('output/applications/test.csv')
    
    # Verify file was opened for appending
    mock_file.assert_called_once_with('output/applications/test.csv', 'a', newline='', encoding='utf-8')
    
    # Verify header was written
    mock_writer.writeheader.assert_called_once()
    
    # Verify data was written
    mock_writer.writerow.assert_called_once()
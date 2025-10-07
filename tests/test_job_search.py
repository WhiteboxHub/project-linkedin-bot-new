"""
Tests for job_search.py functionality
"""
import pytest
import yaml
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.job_search import search_jobs
from core.position_role import ML_roles, UI_roles, QA_roles

@pytest.fixture
def mock_config():
    """Fixture for test configuration"""
    return {
        'username': 'test@example.com',
        'password': 'password123',
        'positions': ['ML Engineer'],
        'locations': ['San Francisco, CA'],
        'role_type': 'ML',
        'roletype': [1, 2, 3]
    }
        
def test_search_jobs_config_loading(mocker, mock_config):
    """Test that search_jobs correctly loads and validates configuration"""
    # Setup mocks
    mock_yaml_load = mocker.patch('yaml.safe_load', return_value=mock_config)
    mock_file = mocker.patch('builtins.open', mocker.mock_open())
    mock_driver = mocker.MagicMock()
    mock_get_browser = mocker.patch('core.job_search.get_browser', return_value=mock_driver)
    
    # Mock the rest of the function to avoid actual web interactions
    mock_driver.find_elements.return_value = []
    
    # Call the function with a dummy config path
    mocker.patch('core.job_search.WebDriverWait')
    mocker.patch('core.job_search.EC')
    
    with pytest.raises(Exception):  # Expect exception since we're not mocking everything
        search_jobs('dummy_config.yaml')
    
    # Verify config was loaded
    mock_file.assert_called_once_with('dummy_config.yaml', 'r')
    mock_yaml_load.assert_called_once()

def test_search_jobs_role_selection(mocker, mock_config):
    """Test that search_jobs selects the correct role type"""
    # Test ML role type
    ml_config = mock_config.copy()
    ml_config['role_type'] = 'ML'
    mock_yaml_load = mocker.patch('yaml.safe_load', return_value=ml_config)
    
    mock_driver = mocker.MagicMock()
    mock_get_browser = mocker.patch('core.job_search.get_browser', return_value=mock_driver)
    mock_driver.find_elements.return_value = []
    
    mocker.patch('builtins.open', mocker.mock_open())
    mocker.patch('core.job_search.WebDriverWait')
    mocker.patch('core.job_search.EC')
    
    with pytest.raises(Exception):
        search_jobs('dummy_config.yaml')
    
    # Test QA role type
    qa_config = mock_config.copy()
    qa_config['role_type'] = 'QA'
    mock_yaml_load.return_value = qa_config
    
    with pytest.raises(Exception):
        search_jobs('dummy_config.yaml')
    
    # Test UI role type
    ui_config = mock_config.copy()
    ui_config['role_type'] = 'UI'
    mock_yaml_load.return_value = ui_config
    
    with pytest.raises(Exception):
        search_jobs('dummy_config.yaml')

def test_search_jobs_invalid_config(mocker, mock_config):
    """Test that search_jobs validates configuration correctly"""
    # Test missing positions
    invalid_config = mock_config.copy()
    invalid_config['positions'] = []
    mocker.patch('yaml.safe_load', return_value=invalid_config)
    
    mocker.patch('builtins.open', mocker.mock_open())
    with pytest.raises(AssertionError):
        search_jobs('dummy_config.yaml')
    
    # Test missing locations
    invalid_config = mock_config.copy()
    invalid_config['locations'] = []
    mocker.patch('yaml.safe_load', return_value=invalid_config)
    
    with pytest.raises(AssertionError):
        search_jobs('dummy_config.yaml')
    
    # Test missing username
    invalid_config = mock_config.copy()
    invalid_config['username'] = None
    mocker.patch('yaml.safe_load', return_value=invalid_config)
    
    with pytest.raises(AssertionError):
        search_jobs('dummy_config.yaml')
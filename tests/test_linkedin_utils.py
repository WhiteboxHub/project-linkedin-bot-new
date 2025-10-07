"""
Tests for linkedin_utils.py functionality
"""
import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.linkedin_utils import wait_for_element, wait_for_element_clickable

@pytest.fixture
def mock_driver(mocker):
    """Fixture for mock driver"""
    return mocker.MagicMock()

@pytest.fixture
def mock_element(mocker):
    """Fixture for mock element"""
    return mocker.MagicMock()

def test_wait_for_element_success(mocker, mock_driver, mock_element):
    """Test wait_for_element when element is found"""
    # Setup mocks
    mock_wait_instance = mocker.MagicMock()
    mock_wait = mocker.patch('utils.linkedin_utils.WebDriverWait', return_value=mock_wait_instance)
    mock_ec = mocker.patch('utils.linkedin_utils.EC')
    mock_wait_instance.until.return_value = mock_element
    
    # Call the function
    result = wait_for_element(mock_driver, "xpath", "//div[@id='test']")
    
    # Verify WebDriverWait was called correctly
    mock_wait.assert_called_once_with(mock_driver, 10)
    mock_wait_instance.until.assert_called_once()
    
    # Verify the element was returned
    assert result == mock_element

def test_wait_for_element_timeout(mocker, mock_driver):
    """Test wait_for_element when timeout occurs"""
    # Setup mocks
    from selenium.common.exceptions import TimeoutException
    mock_wait_instance = mocker.MagicMock()
    mock_wait = mocker.patch('utils.linkedin_utils.WebDriverWait', return_value=mock_wait_instance)
    mocker.patch('utils.linkedin_utils.EC')
    mock_wait_instance.until.side_effect = TimeoutException()
    
    # Call the function
    result = wait_for_element(mock_driver, "xpath", "//div[@id='test']")
    
    # Verify WebDriverWait was called correctly
    mock_wait.assert_called_once_with(mock_driver, 10)
    mock_wait_instance.until.assert_called_once()
    
    # Verify None was returned
    assert result is None

def test_wait_for_element_clickable_success(mocker, mock_driver, mock_element):
    """Test wait_for_element_clickable when element is found and clickable"""
    # Setup mocks
    mock_wait_instance = mocker.MagicMock()
    mock_wait = mocker.patch('utils.linkedin_utils.WebDriverWait', return_value=mock_wait_instance)
    mocker.patch('utils.linkedin_utils.EC')
    mock_wait_instance.until.return_value = mock_element
    
    # Call the function
    result = wait_for_element_clickable(mock_driver, "xpath", "//button[@id='test']")
    
    # Verify WebDriverWait was called correctly
    mock_wait.assert_called_once_with(mock_driver, 10)
    mock_wait_instance.until.assert_called_once()
    
    # Verify the element was returned
    assert result == mock_element
"""
Tests for browser_manager.py functionality
"""
import pytest
import platform
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.browser_manager import get_chrome_paths, get_browser, LINKEDIN_LOGIN_URL

def test_get_chrome_paths_windows(mocker):
    """Test Chrome paths detection on Windows"""
    # Setup mocks
    mocker.patch('platform.system', return_value="Windows")
    mocker.patch('os.path.exists', return_value=True)
    
    # Call the function
    chrome_path, profile_path = get_chrome_paths()
    
    # Verify a Windows path was returned
    assert "Program Files" in chrome_path
    assert "Google\\Chrome" in chrome_path

def test_get_chrome_paths_mac(mocker):
    """Test Chrome paths detection on macOS"""
    # Setup mocks
    mocker.patch('platform.system', return_value="Darwin")
    mocker.patch('os.path.exists', return_value=True)
    
    # Call the function
    chrome_path, profile_path = get_chrome_paths()
    
    # Verify a macOS path was returned
    assert "Applications" in chrome_path
    assert "Google Chrome" in chrome_path

def test_get_chrome_paths_linux(mocker):
    """Test Chrome paths detection on Linux"""
    # Setup mocks
    mocker.patch('platform.system', return_value="Linux")
    mocker.patch('os.path.exists', return_value=True)
    
    # Call the function
    chrome_path, profile_path = get_chrome_paths()
    
    # Verify a Linux path was returned
    assert "google-chrome" in chrome_path

def test_get_browser(mocker):
    """Test browser initialization"""
    # Setup mocks
    mocker.patch('utils.browser_manager.get_chrome_paths', return_value=("/path/to/chrome", "/path/to/profile"))
    mocker.patch('utils.browser_manager.ChromeDriverManager').return_value.install.return_value = "/path/to/chromedriver"
    mock_driver = mocker.MagicMock()
    mocker.patch('utils.browser_manager.webdriver.Chrome', return_value=mock_driver)
    
    # Call the function
    browser = get_browser()
    
    # Verify Chrome was initialized with the correct options
    assert browser == mock_driver
"""
Tests for easy_apply.py functionality
"""
import pytest
import yaml
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.easy_apply import apply_to_jobs, ApplyBot

@pytest.fixture
def mock_config():
    """Fixture for test configuration"""
    return {
        'username': 'test@example.com',
        'password': 'password123',
        'phone_number': '(123) 456-7890',
        'salary': '100000',
        'rate': 'hourly',
        'gender': 'prefer not to say',
        'uploads': {
            'Resume': 'resumes/sample_resume.pdf'
        }
    }

@pytest.fixture
def mock_job_ids():
    """Fixture for job IDs"""
    return {
        '123456': 'To be processed',
        '789012': 'To be processed',
        '345678': 'Already applied'
    }
        
def test_apply_to_jobs(mocker, mock_job_ids):
    """Test that apply_to_jobs processes jobs correctly"""
    # Setup mock
    mock_apply_bot = mocker.MagicMock()
    mock_apply_bot_class = mocker.patch('core.easy_apply.ApplyBot', return_value=mock_apply_bot)
    
    # Call the function
    apply_to_jobs('dummy_config.yaml', mock_job_ids)
    
    # Verify ApplyBot was initialized with the config
    mock_apply_bot_class.assert_called_once_with('dummy_config.yaml')
    
    # Verify apply_to_job was called for each job with "To be processed" status
    assert mock_apply_bot.apply_to_job.call_count == 2
    mock_apply_bot.apply_to_job.assert_any_call('123456')
    mock_apply_bot.apply_to_job.assert_any_call('789012')

def test_apply_to_jobs_error_handling(mocker, mock_job_ids):
    """Test that apply_to_jobs handles errors correctly"""
    # Setup mock to raise an exception
    mock_apply_bot = mocker.MagicMock()
    mock_apply_bot_class = mocker.patch('core.easy_apply.ApplyBot', return_value=mock_apply_bot)
    mock_apply_bot.apply_to_job.side_effect = Exception("Test exception")
    
    # Call the function
    mock_print = mocker.patch('builtins.print')
    apply_to_jobs('dummy_config.yaml', mock_job_ids)
        
    # Verify error was printed
    assert any("Error applying for job 123456: Test exception" in str(call) for call in mock_print.call_args_list)
    assert any("Error applying for job 789012: Test exception" in str(call) for call in mock_print.call_args_list)

def test_apply_bot_initialization(mocker, mock_config):
    """Test that ApplyBot initializes correctly"""
    # Setup mocks
    mock_yaml_load = mocker.patch('yaml.safe_load', return_value=mock_config)
    mock_file = mocker.patch('builtins.open', mocker.mock_open())
    mock_driver = mocker.MagicMock()
    mock_get_browser = mocker.patch('core.easy_apply.get_browser', return_value=mock_driver)
    
    # Initialize ApplyBot
    apply_bot = ApplyBot('dummy_config.yaml')
    
    # Verify config was loaded
    assert mock_file.call_args_list[0][0][0] == 'dummy_config.yaml'
    assert mock_file.call_args_list[0][0][1] == 'r'
    mock_yaml_load.assert_called_once()
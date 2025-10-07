"""
Tests for candidate_selector.py functionality
"""
import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.candidate_selector import select_candidate

def test_select_candidate_success(mocker):
    """Test successful candidate selection"""
    # Setup mocks
    mocker.patch('os.listdir', return_value=['settings.yaml', 'other_file.txt'])
    mocker.patch('builtins.input', return_value='1')
    
    # Call the function
    result = select_candidate()
    
    # Verify correct file was selected
    assert result == 'configs/settings.yaml'

def test_select_candidate_no_yaml(mocker):
    """Test when no YAML files are found"""
    # Setup mock
    mocker.patch('os.listdir', return_value=['file1.txt', 'file2.txt'])
    mock_print = mocker.patch('builtins.print')
    
    # Call the function
    result = select_candidate()
    
    # Verify message was printed
    assert "No YAML files found in the directory." in str(mock_print.call_args_list)
    
    # Verify None was returned
    assert result is None

def test_select_candidate_invalid_input(mocker):
    """Test handling invalid user input"""
    # Setup mocks
    mocker.patch('os.listdir', return_value=['settings.yaml', 'profile.yml'])
    mocker.patch('builtins.input', side_effect=ValueError())
    mock_print = mocker.patch('builtins.print')
    
    # Call the function
    result = select_candidate()
    
    # Verify error message was printed
    assert mock_print.called
    
    # Verify None was returned
    assert result is None
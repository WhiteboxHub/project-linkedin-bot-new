"""
File utilities for reading/writing CSV, YAML, and handling resume files
"""
import os
import csv
import yaml
from datetime import datetime

def load_yaml_config(config_path):
    """
    Load YAML configuration file
    
    Args:
        config_path (str): Path to YAML config file
        
    Returns:
        dict: Configuration data
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        print(f"Error loading config file: {e}")
        return None

def save_application_data(data, output_file):
    """
    Save application data to CSV file
    
    Args:
        data (dict): Application data to save
        output_file (str): Path to output CSV file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(output_file)
    
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'job_id', 'job_title', 'company', 'location', 'application_status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        # Add timestamp to data
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        writer.writerow(data)

def save_qa_data(question, answer, qa_file='output/qa_data.csv'):
    """
    Save question and answer data to CSV file
    
    Args:
        question (str): Question text
        answer (str): Answer text
        qa_file (str): Path to QA CSV file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(qa_file), exist_ok=True)
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.isfile(qa_file)
    
    with open(qa_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['question', 'answer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({'question': question, 'answer': answer})

def load_qa_data(qa_file='output/qa_data.csv'):
    """
    Load question and answer data from CSV file
    
    Args:
        qa_file (str): Path to QA CSV file
        
    Returns:
        dict: Dictionary mapping questions to answers
    """
    qa_dict = {}
    
    if not os.path.isfile(qa_file):
        return qa_dict
    
    try:
        with open(qa_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                qa_dict[row['question']] = row['answer']
    except Exception as e:
        print(f"Error loading QA data: {e}")
    
    return qa_dict
"""
Resume parsing and metadata extraction utilities
"""
import os

def get_resume_path(resume_relative_path, base_dir="resumes"):
    """
    Get the full path to a resume file
    
    Args:
        resume_relative_path (str): Relative path to the resume file
        base_dir (str): Base directory for resumes
        
    Returns:
        str: Full path to the resume file
    """
    # Clean up the path
    resume_relative_path = resume_relative_path.lstrip('/\\')
    
    # Get current working directory
    current_directory = os.getcwd()
    
    # Try direct path first
    fullpath = os.path.join(current_directory, resume_relative_path)
    if os.path.isfile(fullpath):
        return fullpath
    
    # Try with base directory
    fullpath = os.path.join(current_directory, base_dir, os.path.basename(resume_relative_path))
    if os.path.isfile(fullpath):
        return fullpath
    
    # If still not found, try to find by filename in the resumes directory
    resume_filename = os.path.basename(resume_relative_path)
    for root, _, files in os.walk(os.path.join(current_directory, base_dir)):
        for file in files:
            if file.lower() == resume_filename.lower():
                return os.path.join(root, file)
    
    return None

def extract_resume_metadata(resume_path):
    """
    Extract metadata from resume file (placeholder for future functionality)
    
    Args:
        resume_path (str): Path to resume file
        
    Returns:
        dict: Resume metadata
    """
    # This is a placeholder for future functionality
    # Currently just returns basic file info
    
    metadata = {
        'filename': os.path.basename(resume_path),
        'size': os.path.getsize(resume_path),
        'last_modified': os.path.getmtime(resume_path)
    }
    
    return metadata
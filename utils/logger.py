"""
Logging utility for the LinkedIn bot
"""
import os
import logging
from datetime import datetime

def setup_logger(log_dir="output/logs"):
    """
    Set up and configure logger
    
    Args:
        log_dir (str): Directory to store log files
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a logger
    logger = logging.getLogger("linkedin_bot")
    logger.setLevel(logging.INFO)
    
    # Create a file handler
    log_filename = f"linkedin_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    log_path = os.path.join(log_dir, log_filename)
    file_handler = logging.FileHandler(log_path)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    
    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
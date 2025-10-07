#!/usr/bin/env python3
# Entry point

from core.job_search import search_jobs
from core.easy_apply import apply_to_jobs
from utils.candidate_selector import select_candidate
from utils.logger import setup_logger
import sys

def main():
    """
    Main entry point for the LinkedIn job application bot.
    """
    # Setup logging
    logger = setup_logger()
    logger.info("Starting LinkedIn application bot")
    
    try:
        # Select candidate profile
        config_path = select_candidate()
        if not config_path:
            logger.error("No candidate selected. Exiting.")
            sys.exit(1)
            
        # Search for jobs
        job_ids = search_jobs(config_path)
        
        # Apply to jobs
        apply_to_jobs(config_path, job_ids)
        
        logger.info("Job application process completed successfully")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
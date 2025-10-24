from core.easy_apply import apply_to_jobs_with_search
from utils.candidate_selector import select_candidate
from utils.logger import setup_logger
import sys
from pathlib import Path


def main():
    """
    Main entry point for LinkedIn Job Application Bot
    REQUIREMENT #4: Automatically runs page-by-page mode (no selection needed)
    """
  
    Path("output/applications").mkdir(parents=True, exist_ok=True)
    Path("Qa").mkdir(parents=True, exist_ok=True)
    

    logger = setup_logger()
    logger.info("Starting LinkedIn Job Application Bot")
    
    try:
        
        print("\n" + "="*70)
        print("LINKEDIN JOB APPLICATION BOT")
        print("="*70)
        print("Author: LinkedIn Bot")
        print("="*70 + "\n")
        
        
        config_path = select_candidate()
        if not config_path:
            logger.error("No candidate configuration selected")
            sys.exit(1)
        
        print(f"Configuration file: {config_path}\n")
        
        total_applications = apply_to_jobs_with_search(config_path)
        
        logger.info(f"Process completed successfully. Total applications: {total_applications}")
        
        print("\nPress Enter to exit...")
        input()
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user (Ctrl+C)")
        logger.warning("Process interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)


if __name__ == "__main__":
    main()

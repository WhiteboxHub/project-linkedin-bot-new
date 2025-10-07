"""
Constants and static configuration values for the LinkedIn bot
"""

# LinkedIn URLs
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
LINKEDIN_JOBS_URL = "https://www.linkedin.com/jobs/"

# XPaths and selectors
EASY_APPLY_BUTTON_XPATH = "//button[contains(@class,'jobs-apply-button')]"
SUBMIT_BUTTON_XPATH = "//button[@aria-label='Submit application']"
CONTINUE_BUTTON_XPATH = "//button[@aria-label='Continue to next step']"
REVIEW_BUTTON_XPATH = "//button[@aria-label='Review your application']"
FOLLOW_COMPANY_CHECKBOX = "//label[contains(@for, 'follow-company-checkbox')]"
CLOSE_BUTTON_XPATH = "//button[@aria-label='Dismiss']"

# Application form field identifiers
PHONE_FIELD_ID = "phoneNumber"

# Question keywords for automated answers
CITIZENSHIP_KEYWORDS = ["authorized", "citizen", "citizenship", "legally", "eligible", "authorization"]
SPONSORSHIP_KEYWORDS = ["sponsorship", "sponsor", "visa"]
CLEARANCE_KEYWORDS = ["clearance", "security clearance"]
RELOCATION_KEYWORDS = ["relocate", "relocation", "willing to relocate"]
REMOTE_KEYWORDS = ["remote", "work from home", "telecommute"]
EXPERIENCE_KEYWORDS = ["experience", "years of experience", "how many years"]
DEGREE_KEYWORDS = ["degree", "education", "graduate", "certification"]
SALARY_KEYWORDS = ["salary", "compensation", "pay", "wage", "desired salary"]
RACE_KEYWORDS = ["race", "ethnicity", "equal employment", "EEO"]
GENDER_KEYWORDS = ["gender", "sex", "male", "female"]

# File paths
DEFAULT_OUTPUT_DIR = "output/applications"
DEFAULT_LOGS_DIR = "output/logs"
DEFAULT_CONFIG_DIR = "configs"
DEFAULT_RESUMES_DIR = "resumes"

# Application settings
MAX_APPLICATIONS = 100
WAIT_TIME = 3  # seconds
DEBUG_MODE = False
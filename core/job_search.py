"""
Job search functionality for LinkedIn
"""
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import yaml
from bs4 import BeautifulSoup

from utils.browser_manager import get_browser
from core.position_role import ML_roles, UI_roles, QA_roles

def search_jobs(config_path):
    """
    Search for jobs on LinkedIn based on the provided configuration
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        dict: Dictionary of job IDs to process
    """
    # Load configuration
    with open(config_path, 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc
    
    # Validate parameters
    assert len(parameters['positions']) > 0
    assert len(parameters['locations']) > 0
    assert parameters['username'] is not None
    assert parameters['password'] is not None
    
    # Extract parameters
    username = parameters['username']
    password = parameters['password']
    locations = [l for l in parameters['locations'] if l is not None]
    role_type = parameters['role_type']
    
    # Set positions based on role type
    if role_type == 'ML':
        positions = ML_roles
    elif role_type == "QA":
        positions = QA_roles
    elif role_type == "UI":
        positions = UI_roles
    
    # Get other parameters
    blacklist = parameters.get('blacklist', [])
    blacklisttitles = parameters.get('blackListTitles', [])
    experiencelevel = parameters.get('experience_level', [])
    roletype = parameters.get('roletype', [])
    
    # Initialize browser
    browser = get_browser()
    wait = WebDriverWait(browser, 30)
    
    # Login to LinkedIn
    login_linkedin(browser, username, password)
    
    # Dictionary to store job IDs
    all_job_ids = {}
    
    # Search for jobs for each position and location
    for position in positions:
        for location in locations:
            job_ids = search_jobs_by_position_location(
                browser, 
                wait,
                position, 
                location, 
                experiencelevel, 
                roletype, 
                blacklist
            )
            all_job_ids.update(job_ids)
    
    return all_job_ids

def login_linkedin(browser, username, password):
    """Login to LinkedIn"""
    browser.get('https://www.linkedin.com/login')
    time.sleep(8)
    try:
        browser.find_element(By.ID, 'username').clear()
        browser.find_element(By.ID, 'username').send_keys(username)
        browser.find_element(By.ID, 'password').clear()
        browser.find_element(By.ID, 'password').send_keys(password)
        browser.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(10)
    except Exception:
        print("Already logged in. Skipping login...")

def search_jobs_by_position_location(browser, wait, position, location, experiencelevel, roletype, blacklist):
    """Search for jobs by position and location"""
    # Convert experience level to string for URL
    exp_lvl_str = ",".join(map(str, experiencelevel)) if experiencelevel else ""
    exp_lvl_param = f"&f_E={exp_lvl_str}" if exp_lvl_str else ""
    
    # Format location and position for URL
    location_str = f"&location={location}"
    position_str = f"&keywords={position}"
    
    # Convert role type to string for URL
    rolestring = roletype_to_string(roletype)
    
    print(f"Searching for location: {location} and job: {position}")
    
    # Start with first page
    job_per_page = 0
    URL = f"https://www.linkedin.com/jobs/search/?f_LF=f_AL{position_str}{rolestring}{location_str}{exp_lvl_param}&start={job_per_page}"
    browser.get(URL)
    time.sleep(10)
    
    # Get total job count
    job_count = get_job_count(browser, wait)
    print(f"Total jobs found: {job_count}")
    
    # Dictionary to store job IDs
    job_ids = {}
    
    # Iterate through pages
    while job_per_page < job_count:
        URL = f"https://www.linkedin.com/jobs/search/?f_LF=f_AL{position_str}{rolestring}{location_str}{exp_lvl_param}&start={job_per_page}"
        browser.get(URL)
        time.sleep(3)
        
        # Load and scroll page
        load_and_scroll_page(browser)
        
        # Find job listings
        search_locator = (By.CLASS_NAME, "jobs-search-results-list")
        links_locator = (By.XPATH, '//div[@data-job-id]')
        
        if is_element_present(browser, search_locator):
            scroll_results = browser.find_elements(*search_locator)
            for i in range(300, 3000, 100):
                browser.execute_script(f"arguments[0].scrollTo(0, {i});", scroll_results[0])
            time.sleep(1)
        
        if is_element_present(browser, links_locator):
            links = browser.find_elements(*links_locator)
            for link in links:
                if 'Applied' not in link.text and link.text not in blacklist:
                    job_id = link.get_attribute("data-job-id")
                    if job_id and job_id != "search":
                        job_ids[job_id] = "To be processed"
        
        # Move to next page
        job_per_page += 25
    
    return job_ids

def get_job_count(browser, wait):
    """Get the total number of jobs found"""
    try:
        count_css = "small.jobs-search-results-list__text span[dir='ltr']"
        results_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, count_css)))
    except TimeoutException:
        try:
            fallback_css = "span[dir='ltr']"
            results_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, fallback_css)))
        except TimeoutException:
            print("Could not find job results count, defaulting to 0")
            return 0
    
    results_text = ''.join(re.findall(r'\d', results_element.text))
    return int(results_text) if results_text else 0

def roletype_to_string(roletype):
    """Convert role type array to URL parameter string"""
    if not roletype:
        return ""
    elif roletype == [1]:
        return "&f_WT=1"
    elif roletype == [2]:
        return "&f_WT=2"
    elif roletype == [3]:
        return "&f_WT=3"
    elif roletype == [1, 2]:
        return "&f_WT=1%2C2"
    elif roletype == [1, 3]:
        return "&f_WT=1%2C3"
    elif roletype == [2, 3]:
        return "&f_WT=2%2C3"
    elif roletype == [1, 2, 3]:
        return "&f_WT=1%2C2%2C3"
    return ""

def load_and_scroll_page(browser):
    """Load and scroll the page to ensure all content is loaded"""
    scrollpage = 0
    while scrollpage < 4000:
        browser.execute_script(f"window.scrollTo(0, {scrollpage});")
        scrollpage += 500
        time.sleep(0.2)
    time.sleep(3)
    browser.execute_script("window.scrollTo(0,0);")
    return BeautifulSoup(browser.page_source, 'lxml')

def is_element_present(browser, locator):
    """Check if an element is present on the page"""
    return len(browser.find_elements(locator[0], locator[1])) > 0
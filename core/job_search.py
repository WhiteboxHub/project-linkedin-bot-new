
"""
Job search functionality for LinkedIn (Legacy - for pre-collecting job IDs)
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
    print("LEGACY SEARCH MODE: Collecting all job IDs first")

    
    with open(config_path, 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc
    
    assert len(parameters['positions']) > 0, "No positions specified"
    assert len(parameters['locations']) > 0, "No locations specified"
    assert parameters['username'] is not None, "Username not provided"
    assert parameters['password'] is not None, "Password not provided"
    
 
    username = parameters['username']
    password = parameters['password']
    locations = [l for l in parameters['locations'] if l is not None]
    role_type = parameters.get('role_type', 'ML')
    
    if role_type == 'ML':
        positions = ML_roles
    elif role_type == "QA":
        positions = QA_roles
    elif role_type == "UI":
        positions = UI_roles
    else:
        positions = parameters.get('positions', [])
    
    
    blacklist = parameters.get('blacklist', [])
    experiencelevel = parameters.get('experience_level', [])
    roletype = parameters.get('roletype', [])
    

    print("Initializing browser for job search...")
    browser = get_browser()
    wait = WebDriverWait(browser, 30)
    print(" Browser initialized\n")
    
    try:
        
        login_linkedin(browser, username, password)
        
        
        all_job_ids = {}
        
       
        for position in positions:
            for location in locations:
                print(f"\n Searching: {position} in {location}")
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
                print(f" Total jobs collected so far: {len(all_job_ids)}")

        print(f" Search complete! Total job IDs collected: {len(all_job_ids)}")
    
        
        return all_job_ids
        
    except Exception as e:
        print(f"\n Error during job search: {e}")
        raise
        
    finally:
        
        try:
            browser.quit()
            print("Search browser closed\n")
        except:
            pass


def login_linkedin(browser, username, password):
    """Login to LinkedIn"""
    print(" Logging in to LinkedIn...")
    browser.get('https://www.linkedin.com/login')
    time.sleep(8)
    
    try:
        browser.find_element(By.ID, 'username').clear()
        browser.find_element(By.ID, 'username').send_keys(username)
        browser.find_element(By.ID, 'password').clear()
        browser.find_element(By.ID, 'password').send_keys(password)
        browser.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(10)
        print("Login successful\n")
    except Exception:
        print(" Already logged in\n")


def dismiss_prompts(browser):
    """Dismiss any overlays or popups on LinkedIn"""
    try:
        dismiss_buttons = browser.find_elements(By.CSS_SELECTOR, "button[aria-label='Dismiss']")
        for button in dismiss_buttons:
            button.click()
            time.sleep(1)
    except Exception:
        pass


def search_jobs_by_position_location(browser, wait, position, location, experiencelevel, roletype, blacklist):
    """Search for jobs by position and location"""
    exp_lvl_str = ",".join(map(str, experiencelevel)) if experiencelevel else ""
    exp_lvl_param = f"&f_E={exp_lvl_str}" if exp_lvl_str else ""
    
    location_str = f"&location={location}"
    position_str = f"&keywords={position}"
    rolestring = roletype_to_string(roletype)
    
    print(f"🔍 Building search URL...")
    
    job_per_page = 0
    max_pages = 150 
    job_ids = {}
    page_num = 1
    
    while job_per_page < max_pages:
        print(f"\n Loading page {page_num}...")
        
        URL = f"https://www.linkedin.com/jobs/search/?f_LF=f_AL{position_str}{rolestring}{location_str}{exp_lvl_param}&start={job_per_page}"
        
        max_retries = 2
        loaded = False
        
        for retry in range(max_retries):
            try:
                browser.get(URL)
                time.sleep(3)
                loaded = True
                break
            except Exception as e:
                print(f"Page load failed (attempt {retry + 1}/{max_retries}): {e}")
                time.sleep(2)
        
        if not loaded:
            print(f" Failed to load page {page_num} after {max_retries} retries")
            job_per_page += 25
            page_num += 1
            continue
        
        
        dismiss_prompts(browser)
        
        
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-job-id]')))
        except TimeoutException:
            print(f" No job cards found on page {page_num}")
            job_per_page += 25
            page_num += 1
            continue
     
        load_and_scroll_page(browser)
        
    
        link_selectors = [
            (By.XPATH, '//div[@data-job-id]'),
            (By.CSS_SELECTOR, 'div[data-job-id]'),
            (By.XPATH, '//li[@data-job-id]'),
            (By.XPATH, '//*[@data-job-id]')
        ]
        
        links_found = []
        for sel in link_selectors:
            try:
                found = browser.find_elements(*sel)
                if found:
                    links_found = found
                    break
            except Exception:
                continue
        
        print(f" Found {len(links_found)} job cards")
        
        try:
            search_loc = (By.CLASS_NAME, "jobs-search-results-list")
            if is_element_present(browser, search_loc):
                scroll_results = browser.find_elements(*search_loc)
                if scroll_results:
                    for i in range(300, 3000, 100):
                        browser.execute_script(f"arguments[0].scrollTo(0, {i});", scroll_results[0])
                    time.sleep(1)
        except Exception:
            pass
        
        # Collect job ids from found elements
        new_jobs_on_page = 0
        if links_found:
            for link in links_found:
                try:
                    text = link.text or ""
                    
                    # Skip if already applied or blacklisted
                    if 'Applied' in text or text in blacklist:
                        continue
                    
                    job_id = link.get_attribute("data-job-id")
                    
                    if job_id and job_id != "search" and job_id not in job_ids:
                        job_ids[job_id] = "To be processed"
                        new_jobs_on_page += 1
                        
                except Exception:
                    continue
            
            print(f" Collected {new_jobs_on_page} new jobs from this page (Total: {len(job_ids)})")
        else:
            print("  No job cards found, stopping search")
            break
        
    
        if new_jobs_on_page == 0:
            print(" No new jobs on this page, stopping search")
            break
        
        job_count = get_job_count(browser, wait)
        if job_count and job_per_page + 25 >= job_count:
            print(f" Reached end of search results ({job_count} total jobs)")
            break
        
    
        job_per_page += 25
        page_num += 1
        time.sleep(2)  
    
    print(f" Search complete for this position/location")
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
    time.sleep(2)
    browser.execute_script("window.scrollTo(0,0);")
    return BeautifulSoup(browser.page_source, 'lxml')


def is_element_present(browser, locator):
    """Check if an element is present on the page"""
    return len(browser.find_elements(locator[0], locator[1])) > 0
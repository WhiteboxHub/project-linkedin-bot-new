"""
LinkedIn utilities for profile navigation and element helpers
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def wait_for_element(driver, by, value, timeout=10):
    """
    Wait for an element to be present on the page
    
    Args:
        driver: Selenium WebDriver
        by: Locator strategy (e.g., By.XPATH)
        value: Locator value
        timeout: Maximum wait time in seconds
        
    Returns:
        WebElement if found, None otherwise
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None

def wait_for_element_clickable(driver, by, value, timeout=10):
    """
    Wait for an element to be clickable
    
    Args:
        driver: Selenium WebDriver
        by: Locator strategy (e.g., By.XPATH)
        value: Locator value
        timeout: Maximum wait time in seconds
        
    Returns:
        WebElement if found and clickable, None otherwise
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except TimeoutException:
        return None

def safe_click(driver, by, value, timeout=10):
    """
    Safely click an element after waiting for it to be clickable
    
    Args:
        driver: Selenium WebDriver
        by: Locator strategy (e.g., By.XPATH)
        value: Locator value
        timeout: Maximum wait time in seconds
        
    Returns:
        True if click successful, False otherwise
    """
    element = wait_for_element_clickable(driver, by, value, timeout)
    if element:
        try:
            element.click()
            return True
        except:
            # Try JavaScript click if regular click fails
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except:
                return False
    return False

def close_popup(driver):
    """
    Close any popup dialogs that might appear
    
    Args:
        driver: Selenium WebDriver
        
    Returns:
        True if popup closed, False if no popup found
    """
    try:
        # Try different common close button selectors
        close_buttons = [
            "//button[@aria-label='Dismiss']",
            "//button[contains(@class, 'artdeco-modal__dismiss')]",
            "//button[contains(@class, 'artdeco-toast-item__dismiss')]"
        ]
        
        for button in close_buttons:
            try:
                close_btn = driver.find_element(By.XPATH, button)
                close_btn.click()
                time.sleep(1)
                return True
            except NoSuchElementException:
                continue
        
        return False
    except:
        return False

def scroll_to_element(driver, element):
    """
    Scroll to make an element visible
    
    Args:
        driver: Selenium WebDriver
        element: WebElement to scroll to
    """
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
    time.sleep(1)

def get_job_details(driver):
    """
    Extract job details from the current job posting
    
    Args:
        driver: Selenium WebDriver
        
    Returns:
        dict: Job details including title, company, location
    """
    job_details = {}
    
    try:
        # Job title
        title_element = wait_for_element(driver, By.XPATH, "//h1[contains(@class, 'job-title')]")
        if title_element:
            job_details['job_title'] = title_element.text
        
        # Company name
        company_element = wait_for_element(driver, By.XPATH, "//a[contains(@class, 'ember-view t-black t-normal')]")
        if company_element:
            job_details['company'] = company_element.text
        
        # Location
        location_element = wait_for_element(driver, By.XPATH, "//span[contains(@class, 'job-search-card__location')]")
        if location_element:
            job_details['location'] = location_element.text
    except:
        pass
    
    return job_details
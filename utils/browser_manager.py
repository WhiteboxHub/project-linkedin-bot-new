"""
Browser manager utility for handling Chrome browser instances
"""
import os
import time
import platform
import psutil
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"
DEBUG_PORT = 9222  # Standard Chrome debugging port
USER_DATA_DIR = os.path.join(os.path.expanduser("~"), "chrome_selenium_profile")


def is_chrome_running():
    """Check if any Chrome process is currently running."""
    for proc in psutil.process_iter(['name']):
        try:
            if 'chrome' in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def is_chrome_running_with_debug(port=DEBUG_PORT):
    """Check if Chrome is running with remote debugging on specified port."""
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if 'chrome' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any(f'remote-debugging-port={port}' in str(arg) for arg in cmdline):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False



def get_chrome_paths():
    """Detect Chrome executable path for Windows/macOS/Linux."""

    os_name = platform.system()
    if os_name == "Windows":
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for path in chrome_paths:
            if os.path.exists(path):

                return path
    elif os_name == "Darwin":
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif os_name == "Linux":
        return "/usr/bin/google-chrome"
    return None



def launch_chrome_with_debugging(port=DEBUG_PORT):
    """Launch Chrome with remote debugging enabled."""
    chrome_path = get_chrome_paths()
    if not chrome_path:
        print("Chrome executable not found!")
        return False

    # Create user data directory if it doesn't exist
    os.makedirs(USER_DATA_DIR, exist_ok=True)

    # Launch Chrome with debugging
    cmd = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={USER_DATA_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        LINKEDIN_LOGIN_URL
    ]

    try:
        if platform.system() == "Windows":
            subprocess.Popen(cmd, shell=False, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            subprocess.Popen(cmd, shell=False)
        
        print(f"Chrome launched with debugging on port {port}")
        time.sleep(5)  # Wait for Chrome to fully start
        return True
    except Exception as e:
        print(f"Failed to launch Chrome: {e}")
        return False


def attach_to_existing_chrome(port=DEBUG_PORT):
    """Attach Selenium to existing Chrome with debugging enabled."""
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        print(f"Successfully attached to existing Chrome on port {port}")
        return driver
    except Exception as e:
        print(f"Failed to attach to existing Chrome on port {port}: {e}")
        return None


def launch_fresh_selenium_chrome():
    """Launch a brand-new Selenium Chrome session."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        driver.get(LINKEDIN_LOGIN_URL)
        print("Launched fresh Chrome via Selenium")
        return driver
    except Exception as e:
        print(f"Failed to launch fresh Chrome: {e}")
        return None


def get_browser(chrome_profile_name=None, custom_profile_path=None):
    """
    Main entry: Intelligently get or create browser instance.
    
    Priority:
    1. Try to attach to existing Chrome with debugging (port 9222)
    2. If Chrome exists but no debugging, launch fresh Selenium Chrome
    3. If no Chrome, launch fresh Selenium Chrome
    """
    
    print("Checking for existing Chrome instances...")
    
    # Check if Chrome is running with debugging on standard port
    if is_chrome_running_with_debug(DEBUG_PORT):
        print(f"Found Chrome with debugging on port {DEBUG_PORT}. Attempting to attach...")
        driver = attach_to_existing_chrome(DEBUG_PORT)
        if driver:
            print("Successfully reusing existing Chrome browser!")
            return driver
        else:
            print("Attachment failed. Launching fresh Chrome...")
    
    # Check if any Chrome is running (without debugging)
    elif is_chrome_running():
        print("Chrome is running but without debugging.")
        print("Will launch fresh Selenium-managed Chrome...")
    
    else:
        print("No Chrome detected. Launching fresh Chrome...")
    
    # Launch fresh Chrome via Selenium
    driver = launch_fresh_selenium_chrome()
    
    if driver:
        return driver
    else:
        raise Exception("Failed to initialize browser. Please check Chrome installation.")


def initialize_browser():
    """Alias for backward compatibility."""
    return get_browser()
  


def login_to_linkedin(driver, username, password):
    """Attempt login if login page is visible."""
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, 'username').clear()
        driver.find_element(By.ID, 'username').send_keys(username)
        driver.find_element(By.ID, 'password').clear()
        driver.find_element(By.ID, 'password').send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)
        print("LinkedIn login submitted.")
        return True
    except Exception as e:
        print(f"Login not performed: {e}")
        return False
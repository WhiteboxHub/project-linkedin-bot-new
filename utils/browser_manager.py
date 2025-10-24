
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
DEBUG_PORT = 9222
USER_DATA_DIR = os.path.join(os.path.expanduser("~"), "chrome_selenium_profile")


def is_chrome_running_with_debug():
    """Check if Chrome is running with remote debugging on port 9222."""
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if 'chrome' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any(f'remote-debugging-port={DEBUG_PORT}' in str(arg) for arg in cmdline):
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def is_chrome_running():
    """Check if any Chrome process is currently running."""
    for proc in psutil.process_iter(['name']):
        try:
            if 'chrome' in proc.info['name'].lower():
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


def launch_chrome_with_debugging():
    """Launch Chrome with remote debugging enabled."""
    chrome_path = get_chrome_paths()
    if not chrome_path:
        print("Chrome executable not found!")
        return None


    os.makedirs(USER_DATA_DIR, exist_ok=True)


    cmd = [
        chrome_path,
        f"--remote-debugging-port={DEBUG_PORT}",
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
        
        print(f"Chrome launched with debugging on port {DEBUG_PORT}")
        time.sleep(3) 
        return True
    except Exception as e:
        print(f"Failed to launch Chrome: {e}")
        return False


def attach_to_existing_chrome():
    """Attach Selenium to existing Chrome with debugging enabled."""
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{DEBUG_PORT}")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        print("Successfully attached to existing Chrome browser")
        return driver
    except Exception as e:
        print(f"Failed to attach to existing Chrome: {e}")
        return None


def launch_fresh_chrome():
    """Launch a brand-new Selenium Chrome session with persistent profile."""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument(f"--remote-debugging-port={DEBUG_PORT}")

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        driver.get(LINKEDIN_LOGIN_URL)
        print("Launched fresh Chrome with persistent profile")
        return driver
    except Exception as e:
        print(f"Failed to launch fresh Chrome: {e}")
        return None


def get_browser():
    """
    Main entry: Reuse existing Chrome if available, otherwise launch new one.
    
    Flow:
    1. Check if Chrome is running with debugging enabled
    2. If yes, attach to it
    3. If no, launch new Chrome with debugging
    """
    
    
    if is_chrome_running_with_debug():
        print("Detected Chrome running with debugging. Attempting to attach...")
        driver = attach_to_existing_chrome()
        if driver:
            return driver
        else:
            print("Failed to attach. Will launch fresh Chrome.")
    
    
    elif is_chrome_running():
        print("Chrome is running without debugging. Launching new session with debugging...")
     
    
    else:
        print("No Chrome detected. Launching new Chrome with debugging...")
    
  
    return launch_fresh_chrome()


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
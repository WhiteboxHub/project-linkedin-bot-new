"""
Browser manager utility for handling Chrome browser instances
"""
import os
import time
import platform
import subprocess
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"

def get_chrome_paths():
    """
    Get Chrome executable and profile paths based on operating system
    """
    os_name = platform.system()
    if os_name == "Windows":
        # Try multiple possible Chrome installation paths
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Google\Chrome\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\chrome.exe"
        ]
        
        # Find the first path that exists
        chrome_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_path = path
                break
                
        # If Chrome is not found in standard locations, try to find it
        if not chrome_path:
            try:
                # Try to get Chrome path from registry
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe") as key:
                    chrome_path = winreg.QueryValue(key, None)
            except:
                # Default to the first path if all else fails
                chrome_path = chrome_paths[0]
                
        user = os.getlogin()
        profile_path = rf"C:\Users\{user}\AppData\Local\Google\Chrome\User Data"
    elif os_name == "Darwin":
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        profile_path = f"/Users/{os.getlogin()}/Library/Application Support/Google/Chrome"
    elif os_name == "Linux":
        chrome_path = "/usr/bin/google-chrome"
        profile_path = f"/home/{os.getlogin()}/.config/google-chrome"
    else:
        raise Exception(f"Unsupported OS: {os_name}")
    
    if not os.path.exists(chrome_path) and chrome_path is not None:
        print(f"Warning: Chrome executable not found at {chrome_path}")
        print("Attempting to use webdriver_manager to handle driver installation...")
        chrome_path = None  # Let webdriver_manager handle it
    
    # Only check profile path if chrome_path was found
    if chrome_path and not os.path.exists(profile_path):
        print(f"Warning: Chrome profile not found at {profile_path}")
        profile_path = None
    
    return chrome_path, profile_path

def find_chrome_debug_port():
    """
    Find an existing Chrome debugging port
    """
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'chrome' in proc.info['name'].lower():
                for arg in proc.info['cmdline']:
                    if '--remote-debugging-port=' in arg:
                        port = arg.split('=')[1]
                        return port
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def launch_chrome_with_debugging():
    """
    Launch Chrome with remote debugging enabled
    """
    chrome_path, profile_path = get_chrome_paths()
    port = "9223"
    subprocess.Popen([
        chrome_path,
        f'--remote-debugging-port={port}',
        f'--user-data-dir={profile_path}',
        '--start-maximized',
        LINKEDIN_LOGIN_URL
    ])
    time.sleep(10)
    return port

def attach_to_chrome(port):
    """
    Attach Selenium WebDriver to an existing Chrome instance
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.debugger_address = f"127.0.0.1:{port}"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if "https://www.linkedin.com/login" in driver.current_url:
            break
    return driver

def get_browser():
    """
    Initialize browser by finding or launching Chrome with debugging
    """
    port = find_chrome_debug_port()
    if not port:
        port = launch_chrome_with_debugging()
    return attach_to_chrome(port)

def initialize_browser():
    """
    Initialize browser by finding or launching Chrome with debugging
    (Alias for get_browser for backward compatibility)
    """
    return get_browser()

def login_to_linkedin(driver, username, password):
    """
    Login to LinkedIn if login page is detected
    """
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, 'username').clear()
        driver.find_element(By.ID, 'username').send_keys(username)
        driver.find_element(By.ID, 'password').clear()
        driver.find_element(By.ID, 'password').send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(10)
        return True
    except Exception:
        return False
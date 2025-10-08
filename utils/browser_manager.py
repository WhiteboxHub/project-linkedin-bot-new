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

def get_chrome_paths(chrome_profile_name=None, custom_profile_path=None):
    """
    Get Chrome executable and profile paths based on operating system
    Args:
        chrome_profile_name: Specific Chrome profile name to use (e.g., 'Profile 37', 'Default')
        custom_profile_path: Full custom profile path if provided in config
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
                
        # Use custom profile path if provided, otherwise construct from profile name
        if custom_profile_path:
            profile_path = custom_profile_path
        else:
            user = os.getlogin()
            base_profile_path = rf"C:\Users\{user}\AppData\Local\Google\Chrome\User Data"
            
            # If specific profile name is provided, append it to the base path
            if chrome_profile_name and chrome_profile_name != 'Default':
                profile_path = os.path.join(base_profile_path, chrome_profile_name)
            else:
                profile_path = base_profile_path
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

def launch_chrome_with_debugging(chrome_profile_name=None, custom_profile_path=None):
    """
    Launch Chrome with remote debugging enabled
    Args:
        chrome_profile_name: Specific Chrome profile name to use
        custom_profile_path: Full custom profile path if provided in config
    """
    chrome_path, profile_path = get_chrome_paths(chrome_profile_name, custom_profile_path)
    port = "9223"
    
    # If chrome_path is None, try to use 'chrome' command directly
    if chrome_path is None:
        chrome_path = "chrome"  # Assume Chrome is in PATH
    
    # Build command arguments
    cmd_args = [
        chrome_path,
        f'--remote-debugging-port={port}',
        '--start-maximized',
        LINKEDIN_LOGIN_URL
    ]
    
    # Only add user-data-dir if profile_path exists
    if profile_path and os.path.exists(profile_path):
        cmd_args.insert(2, f'--user-data-dir={profile_path}')
    
    try:
        subprocess.Popen(cmd_args)
        time.sleep(10)
        return port
    except FileNotFoundError:
        raise Exception("Chrome executable not found. Please install Google Chrome or ensure it's in your PATH.")

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

def get_browser(chrome_profile_name=None, custom_profile_path=None):
    """
    Initialize browser by finding or launching Chrome with debugging
    Args:
        chrome_profile_name: Specific Chrome profile name to use
        custom_profile_path: Full custom profile path if provided in config
    """
    port = find_chrome_debug_port()
    if not port:
        port = launch_chrome_with_debugging(chrome_profile_name, custom_profile_path)
    return attach_to_chrome(port)

def initialize_browser(chrome_profile_name=None, custom_profile_path=None):
    """
    Initialize browser by finding or launching Chrome with debugging
    (Alias for get_browser for backward compatibility)
    Args:
        chrome_profile_name: Specific Chrome profile name to use
        custom_profile_path: Full custom profile path if provided in config
    """
    return get_browser(chrome_profile_name, custom_profile_path)

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
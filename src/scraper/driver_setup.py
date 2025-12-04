from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

def get_driver(headless=False):
    """
    Creates and returns a Chrome WebDriver instance with optimal settings.
    
    Args:
        headless (bool): Whether to run Chrome in headless mode
        
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    chrome_options = Options()

    # Use a dedicated Selenium profile directory in your project
    # This avoids conflicts with your main Chrome profile
    selenium_profile_dir = os.path.join(os.getcwd(), "selenium_chrome_profile")
    os.makedirs(selenium_profile_dir, exist_ok=True)
    
    chrome_options.add_argument(f"--user-data-dir={selenium_profile_dir}")

    # Headless mode configuration
    if headless:
        chrome_options.add_argument("--headless=new")

    # Essential stability arguments
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Remote debugging port (helps prevent DevToolsActivePort errors)
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Set window size (important for consistent rendering)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    
    # Anti-detection measures (helps avoid bot detection)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Additional stability options
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    
    # Set a realistic user agent
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Create service
    service = Service(ChromeDriverManager().install())

    # Create and return driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Additional anti-detection script
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": driver.execute_script("return navigator.userAgent").replace('Headless', '')
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import requests
from typing import Dict, List, Tuple

def get_source_limits() -> Dict[str, int]:
    """Return the maximum number of images per source"""
    return {
        "google": 50,
        "getty": 30,
        "shutterstock": 30,
        "unsplash": 30,
        "pexels": 30
    }

def setup_driver() -> webdriver.Chrome:
    """Setup and return Chrome webdriver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=chrome_options)

def download_image(url: str, path: str) -> bool:
    """Download image from URL to specified path"""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            return True
        return False
    except Exception:
        return False

# Add more scraping functions as needed

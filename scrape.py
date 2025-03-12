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

def scrape_website(url: str) -> str:
    """Scrape website content using Selenium"""
    driver = setup_driver()
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return driver.page_source
    except Exception as e:
        return f"Error scraping website: {str(e)}"
    finally:
        driver.quit()

def extract_body_content(html_content: str) -> str:
    """Extract main content from HTML using BeautifulSoup"""
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text()

def clean_body_content(content: str) -> str:
    """Clean and format extracted content"""
    # Remove extra whitespace and empty lines
    lines = (line.strip() for line in content.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

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

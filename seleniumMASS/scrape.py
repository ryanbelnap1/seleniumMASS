from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
import io
from PIL import Image
import time
import os
import re
from enum import Enum
from typing import Dict, Any

load_dotenv()

# Get the SBR_WEBDRIVER URL from environment variables
SBR_WEBDRIVER = os.getenv('SBR_WEBDRIVER')

def scrape_website(website, sbr_webdriver_url=SBR_WEBDRIVER):
    print("Connecting to Scraping Browser...")
    sbr_connection = ChromiumRemoteConnection(sbr_webdriver_url, "goog", "chrome")
    with Remote(sbr_connection, options=ChromeOptions()) as driver:
        print("Connected! Navigating...")
        driver.get(website)
        print("Taking page screenshot to file page.png")
        driver.get_screenshot_as_file('./page.png')
        print("Navigated! Scraping page content...")
        html = driver.page_source
        return html, driver

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text content
    cleaned_content = soup.get_text(separator="\n")

    # List of patterns to remove (using regular expressions)
    patterns_to_remove = [
        r'Press \/ to scroll',
        r'Stop scrolling',
        r'Please click here',
        r'Click anywhere to continue',
        r'Press ESC to close',
        r'Press Enter to open',
        r'Scroll to continue',
        r'Click to scroll',
        r'Loading\.\.\.',
        r'Please wait\.\.\.',
        r'\[object Object\]',
        r'undefined',
        r'null',
        r'NaN',
    ]

    # Remove all matching patterns
    for pattern in patterns_to_remove:
        cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE)

    # Remove empty lines and excessive whitespace
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines()
        if line.strip() and len(line.strip()) > 1
    )

    # Remove duplicate consecutive lines
    lines = cleaned_content.splitlines()
    cleaned_lines = []
    prev_line = None
    for line in lines:
        if line != prev_line:
            cleaned_lines.append(line)
        prev_line = line

    cleaned_content = "\n".join(cleaned_lines)
    cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]

class ImageResolution(Enum):
    SD = "480p"
    HD = "720p"
    FHD = "1080p"
    UHD = "4K"

def get_image_resolution(url):
    try:
        image_content = requests.get(url, timeout=5).content
        image = Image.open(io.BytesIO(image_content))
        width, height = image.size
        if width >= 3840 and height >= 2160:
            return ImageResolution.UHD
        elif width >= 1920 and height >= 1080:
            return ImageResolution.FHD
        elif width >= 1280 and height >= 720:
            return ImageResolution.HD
        else:
            return ImageResolution.SD
    except Exception as e:
        print(f"Failed to get image resolution: {e}")
        return None

def download_image(download_path, url, file_name, min_resolution=None, max_resolution=None):
    try:
        os.makedirs(download_path, exist_ok=True)
        
        # Check image resolution before downloading
        resolution = get_image_resolution(url)
        if resolution is None:
            return False, "Failed to get image resolution"
            
        if min_resolution and (resolution.value < min_resolution.value):
            return False, f"Image resolution {resolution.name} is below minimum {min_resolution.name}"
            
        if max_resolution and (resolution.value > max_resolution.value):
            return False, f"Image resolution {resolution.name} exceeds maximum {max_resolution.name}"

        image_content = requests.get(url).content
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file)
        file_path = os.path.join(download_path, file_name)
        
        with open(file_path, "wb") as f:
            image.save(f, "JPEG")
        return True, f"Successfully downloaded image ({resolution.name})"
    except Exception as e:
        return False, f"Failed to download image: {e}"

def get_source_limits(source: str) -> Dict[str, Any]:
    """Return download limits and resolution restrictions for each source"""
    limits = {
        "google": {
            "daily_limit": 100,
            "batch_limit": 10,
            "max_resolution": ImageResolution.HD,
            "description": "Google Images with standard web scraping"
        },
        "getty": {
            "daily_limit": 50,
            "batch_limit": 5,
            "max_resolution": ImageResolution.FHD,
            "description": "Getty Images preview scraping"
        },
        "shutterstock": {
            "daily_limit": 50,
            "batch_limit": 5,
            "max_resolution": ImageResolution.FHD,
            "description": "Shutterstock preview images"
        },
        "unsplash": {
            "daily_limit": 50,
            "batch_limit": 30,
            "max_resolution": ImageResolution.UHD,
            "description": "High-quality free images from Unsplash"
        },
        "pexels": {
            "daily_limit": 200,
            "batch_limit": 30,
            "max_resolution": ImageResolution.UHD,
            "description": "Professional stock photos from Pexels"
        }
    }
    return limits.get(source, {})

def scrape_images(driver, search_query, max_images=6, source="google", download_dir="downloaded_images", 
                 min_resolution=None, max_resolution=None):
    image_urls = set()
    download_stats = {
        "attempted": 0,
        "successful": 0,
        "failed": 0,
        "skipped": 0,
        "details": []
    }
    
    # Get source-specific limits
    source_limits = get_source_limits(source)
    if max_images > source_limits["batch_limit"]:
        max_images = source_limits["batch_limit"]
        download_stats["details"].append(f"Adjusted batch size to source limit: {source_limits['batch_limit']}")

    if source == "google":
        search_url = f"https://www.google.com/search?q={search_query}&tbm=isch"
        css_selector = "img.Q4LuWd"
        download_subdir = "google_images"
    elif source == "getty":
        search_url = f"https://www.gettyimages.com/search/2/image?phrase={search_query}"
        css_selector = "article img.gallery-asset__thumb"
        download_subdir = "getty_images"
    elif source == "shutterstock":
        search_url = f"https://www.shutterstock.com/search/{search_query}"
        css_selector = "img.z_h_9d80b"
        download_subdir = "shutterstock"
    else:
        raise ValueError("Invalid source. Choose 'google', 'getty', or 'shutterstock'")

    driver.get(search_url)
    download_path = os.path.join(download_dir, download_subdir)
    
    while len(image_urls) < max_images:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        try:
            images = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
            )
            
            for img in images:
                if len(image_urls) >= max_images:
                    break
                    
                if source == "google":
                    try:
                        img.click()
                        time.sleep(1)
                        actual_images = driver.find_elements(By.CLASS_NAME, "n3VNCb")
                        for actual_image in actual_images:
                            src = actual_image.get_attribute('src')
                            if src and src.startswith('http'):
                                image_urls.add(src)
                    except:
                        continue
                else:
                    src = img.get_attribute('src')
                    if src and src.startswith('http'):
                        image_urls.add(src)
                        
        except Exception as e:
            download_stats["details"].append(f"Error finding images: {e}")
            break
    
    # Download images
    for i, url in enumerate(image_urls):
        download_stats["attempted"] += 1
        file_name = f"{search_query}_{i+1}.jpg"
        success, message = download_image(
            download_path, 
            url, 
            file_name, 
            min_resolution, 
            max_resolution or source_limits["max_resolution"]
        )
        
        if success:
            download_stats["successful"] += 1
        else:
            if "resolution" in message:
                download_stats["skipped"] += 1
            else:
                download_stats["failed"] += 1
        download_stats["details"].append(f"Image {i+1}: {message}")
    
    return list(image_urls), download_stats

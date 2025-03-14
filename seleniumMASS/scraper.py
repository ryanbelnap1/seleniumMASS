from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from selenium_stealth import stealth
from services.image_service import ImageService
import os
import time
import requests
import random
from PIL import Image
from io import BytesIO
from typing import Set, Dict, List, Union

class ImageScraper:
    def __init__(self, headless: bool = True):
        self.setup_driver(headless)
        self.image_service = ImageService()

    def setup_driver(self, headless: bool):
        options = uc.ChromeOptions()
        
        # Stealth settings
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # Additional stealth settings
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36")
        
        if headless:
            options.add_argument('--headless=new')

        self.driver = uc.Chrome(options=options)
        
        # Apply stealth settings
        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def random_sleep(self, min_time: float = 1.0, max_time: float = 3.0):
        """Randomized sleep to mimic human behavior"""
        time.sleep(random.uniform(min_time, max_time))

    def random_scroll(self):
        """Perform random scrolling to mimic human behavior"""
        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        
        while current_position < scroll_height:
            # Random scroll amount between 300 and 700 pixels
            scroll_amount = random.randint(300, 700)
            current_position += scroll_amount
            
            # Scroll with smooth behavior
            self.driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}})")
            
            # Random pause between scrolls
            self.random_sleep(0.5, 2.0)
            
            # Occasionally scroll back up a bit
            if random.random() < 0.2:  # 20% chance
                current_position -= random.randint(100, 300)
                self.driver.execute_script(f"window.scrollTo({{top: {current_position}, behavior: 'smooth'}})")
                self.random_sleep(0.5, 1.5)

    def scrape_google_web(self, query: str, max_images: int = 30) -> Set[str]:
        """Scrape images from Google Images using web scraping with human-like behavior"""
        self.driver.get(f"https://www.google.com/search?q={query}&tbm=isch")
        image_urls = set()
        
        # Initial wait for page load
        self.random_sleep(2.0, 4.0)
        
        while len(image_urls) < max_images:
            # Human-like scrolling
            self.random_scroll()
            
            # Find all image elements with random pauses
            thumbnails = self.driver.find_elements(By.CSS_SELECTOR, "img.rg_i")
            
            # Extract image URLs with human-like behavior
            for img in thumbnails:
                try:
                    # Sometimes move mouse to element (when not in headless mode)
                    if not self.driver.execute_script("return navigator.webdriver"):
                        actions = webdriver.ActionChains(self.driver)
                        actions.move_to_element(img).perform()
                        self.random_sleep(0.1, 0.3)
                    
                    if img.get_attribute('src') and img.get_attribute('src').startswith('http'):
                        image_urls.add(img.get_attribute('src'))
                        
                except Exception as e:
                    print(f"Error processing image: {str(e)}")
                    continue
                
            if len(image_urls) >= max_images:
                break
                
            # Random pause between iterations
            self.random_sleep(1.0, 2.0)
                
        return set(list(image_urls)[:max_images])

    def download_images(self, urls: Set[str], output_dir: str, prefix: str = "") -> Dict[str, int]:
        """Download images from URLs to specified directory with human-like delays"""
        os.makedirs(output_dir, exist_ok=True)
        
        successful = 0
        failed = 0
        
        for idx, url in enumerate(urls):
            try:
                # Add random delays between downloads
                self.random_sleep(0.5, 1.5)
                
                # Use realistic headers for requests
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
                    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.google.com/'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    filename = f"{prefix}_{idx+1}.jpg" if prefix else f"image_{idx+1}.jpg"
                    filepath = os.path.join(output_dir, filename)
                    img.save(filepath, "JPEG")
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"Failed to download {url}: {str(e)}")
                failed += 1
                
        return {"successful": successful, "failed": failed}

    def search_images(self, query: str, sources: List[str], max_images: int = 30) -> Dict[str, Set[str]]:
        """Search images from multiple sources"""
        results = {}
        
        # API-based sources
        if any(source in ['unsplash', 'pexels', 'bing', 'google_api'] for source in sources):
            api_results = self.image_service.search_all_apis(query, max_images)
            results.update(api_results)
        
        # Web scraping sources
        if 'google_web' in sources:
            results['google_web'] = self.scrape_google_web(query, max_images)
        
        return results

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

# Example usage
if __name__ == "__main__":
    scraper = ImageScraper(headless=True)
    try:
        # Search for images from multiple sources
        results = scraper.search_images(
            query="cute cats",
            sources=['unsplash', 'pexels', 'google_web'],
            max_images=10
        )
        
        # Download images from each source
        for source, urls in results.items():
            if urls:
                print(f"Downloading {len(urls)} images from {source}")
                stats = scraper.download_images(
                    urls=urls,
                    output_dir=f"downloads/{source}",
                    prefix=f"{source}"
                )
                print(f"Successfully downloaded: {stats['successful']}")
                print(f"Failed downloads: {stats['failed']}")
                
    finally:
        scraper.driver.quit()
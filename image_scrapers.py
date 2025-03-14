from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import random
import time
import os
import requests
import io
from PIL import Image
from utils import get_undetected_driver

class ImageScraper:
    def __init__(self):
        self.driver = get_undetected_driver()
        
    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
        
    def scroll_down(self, delay=1):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

    def download_image(self, download_path, url, file_name):
        try:
            os.makedirs(download_path, exist_ok=True)
            image_content = requests.get(url).content
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file)
            file_path = os.path.join(download_path, file_name)
            
            with open(file_path, "wb") as f:
                image.save(f, "JPEG")
            return True
        except Exception as e:
            print(f'Failed to download image: {e}')
            return False

class GoogleImageScraper(ImageScraper):
    def scrape(self, search_query, max_images=6, delay=2):
        try:
            search_query = search_query.replace(' ', '+')
            search_url = f"https://www.google.com/search?q={search_query}&tbm=isch"
            
            print(f"Accessing URL: {search_url}")
            self.driver.get(search_url)
            time.sleep(delay)
            
            image_urls = set()
            
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img.rg_i"))
            )
            
            scroll_attempts = 0
            max_scrolls = 8
            
            while len(image_urls) < max_images and scroll_attempts < max_scrolls:
                # Scroll and wait
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(delay)
                
                # Find all image elements
                elements = self.driver.find_elements(By.CSS_SELECTOR, "img.rg_i")
                
                for element in elements:
                    try:
                        # Click on the image to get the full resolution version
                        element.click()
                        time.sleep(delay)
                        
                        # Try to get the full-resolution image
                        actual_images = self.driver.find_elements(
                            By.CSS_SELECTOR, 
                            "img.n3VNCb, img.r48jcc, img.iPVvYb"
                        )
                        
                        for img in actual_images:
                            src = img.get_attribute('src')
                            if src and src.startswith('http') and src not in image_urls:
                                if self.is_valid_image(src):
                                    image_urls.add(src)
                                    print(f"Found image: {src}")
                                    if len(image_urls) >= max_images:
                                        return list(image_urls)
                    except:
                        continue
                
                scroll_attempts += 1
            
            return list(image_urls)
            
        except Exception as e:
            print(f"Error in Google scraper: {str(e)}")
            return list(image_urls)

    def is_valid_image(self, url):
        try:
            response = requests.head(url, timeout=5)
            content_type = response.headers.get('content-type', '')
            return ('image' in content_type.lower() and 
                    not url.endswith(('.svg', '.gif')) and 
                    'data:image' not in url)
        except:
            return False

class GettyImageScraper(ImageScraper):
    def scrape(self, search_query, max_images=6, delay=1):
        search_url = f"https://www.gettyimages.com/search/2/image?phrase={search_query}"
        self.driver.get(search_url)
        
        image_urls = set()
        while len(image_urls) < max_images:
            self.scroll_down(delay)
            
            try:
                images = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article img.gallery-asset__thumb"))
                )
                
                for img in images:
                    if len(image_urls) >= max_images:
                        break
                    src = img.get_attribute('src')
                    if src and src.startswith('http'):
                        image_urls.add(src)
            except Exception as e:
                print(f"Error finding images: {e}")
                break
                
        return image_urls

class ShutterstockScraper(ImageScraper):
    def scrape(self, search_query, max_images=6, delay=1):
        search_url = f"https://www.shutterstock.com/search/{search_query}"
        self.driver.get(search_url)
        
        image_urls = set()
        while len(image_urls) < max_images:
            self.scroll_down(delay)
            
            try:
                images = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.z_h_9d80b"))
                )
                
                for img in images:
                    if len(image_urls) >= max_images:
                        break
                    src = img.get_attribute('src')
                    if src and src.startswith('http'):
                        image_urls.add(src)
            except Exception as e:
                print(f"Error finding images: {e}")
                break
                
        return image_urls
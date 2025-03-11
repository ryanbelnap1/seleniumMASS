from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import io
from PIL import Image
import time
import os

class ImageScraper:
    def __init__(self, driver):
        self.driver = driver
        
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
    def scrape(self, search_query, max_images=6, delay=1):
        search_url = f"https://www.google.com/search?q={search_query}&tbm=isch"
        self.driver.get(search_url)
        
        image_urls = set()
        skips = 0
        
        while len(image_urls) + skips < max_images:
            self.scroll_down(delay)
            
            thumbnails = self.driver.find_elements(By.CLASS_NAME, "Q4LuWd")
            
            for img in thumbnails[len(image_urls) + skips:max_images]:
                try:
                    img.click()
                    time.sleep(delay)
                except:
                    continue
                
                images = self.driver.find_elements(By.CLASS_NAME, "n3VNCb")
                for image in images:
                    if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                        image_urls.add(image.get_attribute('src'))
        
        return image_urls

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
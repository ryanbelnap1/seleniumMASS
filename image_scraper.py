from selenium.webdriver.common.by import By
import requests
import io
from PIL import Image
import time
import os

def get_images_from_google(driver, search_query, delay=1, max_images=6):
    def scroll_down(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

    # Construct Google Images search URL
    search_url = f"https://www.google.com/search?q={search_query}&tbm=isch"
    driver.get(search_url)

    image_urls = set()
    skips = 0

    while len(image_urls) + skips < max_images:
        scroll_down(driver)

        thumbnails = driver.find_elements(By.CLASS_NAME, "Q4LuWd")

        for img in thumbnails[len(image_urls) + skips:max_images]:
            try:
                img.click()
                time.sleep(delay)
            except:
                continue

            images = driver.find_elements(By.CLASS_NAME, "n3VNCb")
            for image in images:
                if image.get_attribute('src') in image_urls:
                    max_images += 1
                    skips += 1
                    break

                if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                    image_urls.add(image.get_attribute('src'))
                    print(f"Found {len(image_urls)}")

    return image_urls

def download_image(download_path, url, file_name):
    try:
        # Create download directory if it doesn't exist
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
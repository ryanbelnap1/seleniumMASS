from PIL import Image
from io import BytesIO
import os
import requests
from typing import Optional, Tuple

class ImageService:
    def __init__(self):
        self.base_path = "downloaded_images"
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure all necessary directories exist"""
        directories = [
            'google_images',
            'getty_images',
            'shutterstock_images',
            'unsplash_images',
            'pexels_images'
        ]
        for dir_name in directories:
            dir_path = os.path.join(self.base_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)

    def download_image(self, url: str, source: str, filename: str) -> Tuple[bool, Optional[str]]:
        """
        Download an image from URL and save it to the appropriate directory
        Returns: (success: bool, error_message: Optional[str])
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Verify it's an image
            img = Image.open(BytesIO(response.content))
            
            # Determine save directory based on source
            save_dir = os.path.join(self.base_path, f"{source}_images")
            os.makedirs(save_dir, exist_ok=True)
            
            # Save path
            save_path = os.path.join(save_dir, filename)
            
            # Save image
            img.save(save_path)
            return True, None
            
        except requests.RequestException as e:
            return False, f"Download failed: {str(e)}"
        except Exception as e:
            return False, f"Processing failed: {str(e)}"

    def get_image_path(self, source: str, filename: str) -> str:
        """Get the full path for an image"""
        return os.path.join(self.base_path, f"{source}_images", filename)
import requests
import os
from dotenv import load_dotenv
from typing import Set, Dict, Tuple

load_dotenv()

class APIImageScraper:
    def __init__(self):
        self.unsplash_key = os.getenv('UNSPLASH_ACCESS_KEY')
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        self.unsplash_url = os.getenv('UNSPLASH_API_URL', 'https://api.unsplash.com/search/photos')
        self.pexels_url = os.getenv('PEXELS_API_URL', 'https://api.pexels.com/v1/search')

    def scrape_unsplash(self, query: str, max_images: int = 6) -> Tuple[Set[str], Dict]:
        if not self.unsplash_key:
            return set(), {"error": "Unsplash API key not configured"}
        
        headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
        try:
            response = requests.get(self.unsplash_url, headers=headers, params={
                "query": query,
                "per_page": max_images,
                "page": 1
            })
            response.raise_for_status()
            data = response.json()
            return {photo["urls"]["regular"] for photo in data.get("results", [])}, {}
        except Exception as e:
            return set(), {"error": f"Unsplash API error: {str(e)}"}

    def scrape_pexels(self, query: str, max_images: int = 6) -> Tuple[Set[str], Dict]:
        if not self.pexels_key:
            return set(), {"error": "Pexels API key not configured"}
        
        headers = {"Authorization": self.pexels_key}
        try:
            response = requests.get(self.pexels_url, headers=headers, params={
                "query": query,
                "per_page": max_images,
                "page": 1
            })
            response.raise_for_status()
            data = response.json()
            return {photo["src"]["large"] for photo in data.get("photos", [])}, {}
        except Exception as e:
            return set(), {"error": f"Pexels API error: {str(e)}"}

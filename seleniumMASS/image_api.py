import os
from typing import List, Dict
import requests
from dotenv import load_dotenv

load_dotenv()

class APIImageScraper:
    def __init__(self):
        self.unsplash_key = os.getenv('UNSPLASH_ACCESS_KEY')
        self.pexels_key = os.getenv('PEXELS_API_KEY')
        
    def search_unsplash(self, query: str, per_page: int = 30) -> List[Dict]:
        """Search images on Unsplash"""
        if not self.unsplash_key:
            return []
        
        url = f"https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
        params = {"query": query, "per_page": per_page}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 429:  # Rate limit exceeded
                return {"error": "Rate limit exceeded. Please try again later."}
            if response.status_code == 200:
                return response.json()["results"]
            return []
        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}
            
    def search_pexels(self, query: str, per_page: int = 30) -> List[Dict]:
        """Search images on Pexels"""
        if not self.pexels_key:
            return []
            
        url = f"https://api.pexels.com/v1/search"
        headers = {"Authorization": self.pexels_key}
        params = {"query": query, "per_page": per_page}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json()["photos"]
            return []
        except Exception:
            return []

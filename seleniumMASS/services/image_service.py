import os
import requests
from typing import List, Dict, Optional, Set
from dotenv import load_dotenv

load_dotenv()

class ImageService:
    def __init__(self):
        self.api_keys = {
            'unsplash': os.getenv('UNSPLASH_ACCESS_KEY'),
            'pexels': os.getenv('PEXELS_API_KEY'),
            'bing': os.getenv('BING_API_KEY'),
            'google': {
                'cx': os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
                'key': os.getenv('GOOGLE_API_KEY')
            },
            'pixabay': os.getenv('PIXABAY_API_KEY'),
            'giphy': os.getenv('GIPHY_API_KEY'),
            'flickr': {
                'key': os.getenv('FLICKR_API_KEY'),
                'secret': os.getenv('FLICKR_SECRET')
            },
            'deviantart': {
                'client_id': os.getenv('DEVIANTART_CLIENT_ID'),
                'client_secret': os.getenv('DEVIANTART_CLIENT_SECRET')
            },
            'facebook': {
                'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN')
            },
            'instagram': {
                'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN')
            }
        }

    def search_unsplash(self, query: str, max_images: int = 30) -> Set[str]:
        if not self.api_keys['unsplash']:
            return set()
        
        headers = {"Authorization": f"Client-ID {self.api_keys['unsplash']}"}
        url = "https://api.unsplash.com/search/photos"
        
        try:
            response = requests.get(url, 
                                 headers=headers, 
                                 params={"query": query, "per_page": max_images})
            response.raise_for_status()
            return {photo["urls"]["regular"] for photo in response.json().get("results", [])}
        except Exception as e:
            print(f"Unsplash API error: {str(e)}")
            return set()

    def search_pexels(self, query: str, max_images: int = 30) -> Set[str]:
        if not self.api_keys['pexels']:
            return set()
        
        headers = {"Authorization": self.api_keys['pexels']}
        url = "https://api.pexels.com/v1/search"
        
        try:
            response = requests.get(url, 
                                 headers=headers, 
                                 params={"query": query, "per_page": max_images})
            response.raise_for_status()
            return {photo["src"]["large"] for photo in response.json().get("photos", [])}
        except Exception as e:
            print(f"Pexels API error: {str(e)}")
            return set()

    def search_bing(self, query: str, max_images: int = 30) -> Set[str]:
        if not self.api_keys['bing']:
            return set()
        
        headers = {'Ocp-Apim-Subscription-Key': self.api_keys['bing']}
        url = 'https://api.bing.microsoft.com/v7.0/images/search'
        
        try:
            response = requests.get(url, 
                                 headers=headers, 
                                 params={"q": query, "count": max_images})
            response.raise_for_status()
            return {image["contentUrl"] for image in response.json().get("value", [])}
        except Exception as e:
            print(f"Bing API error: {str(e)}")
            return set()

    def search_google(self, query: str, max_images: int = 30) -> Set[str]:
        if not self.api_keys['google']['key'] or not self.api_keys['google']['cx']:
            return set()
        
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'q': query,
            'cx': self.api_keys['google']['cx'],
            'key': self.api_keys['google']['key'],
            'searchType': 'image',
            'num': max_images
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return {item["link"] for item in response.json().get("items", [])}
        except Exception as e:
            print(f"Google API error: {str(e)}")
            return set()

    def search_all_apis(self, query: str, max_images_per_source: int = 30) -> Dict[str, Set[str]]:
        """Search all configured API sources for images"""
        results = {}
        
        # Map of search functions
        search_functions = {
            'unsplash': self.search_unsplash,
            'pexels': self.search_pexels,
            'bing': self.search_bing,
            'google': self.search_google
        }
        
        for source, search_func in search_functions.items():
            results[source] = search_func(query, max_images_per_source)
            
        return results
import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv, set_key
from scrape import scrape_website, extract_body_content, clean_body_content
from parse import analyze_website_content
from image_api import APIImageScraper
from typing import List

def update_env_file(key: str, value: str) -> None:
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    set_key(env_path, key, value)
    load_dotenv(override=True)

def main():
    st.title("Mass Image Scraper")
    
    tab1, tab2, tab3 = st.tabs(["Scrape Images", "Website Analyzer", "Settings"])
    
    # Rest of your main function code...

if __name__ == "__main__":
    main()  # Remove any print statements or messages after this
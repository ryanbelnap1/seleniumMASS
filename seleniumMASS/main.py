import streamlit as st
import os
from dotenv import load_dotenv, set_key
from scrape import get_source_limits
from image_api import APIImageScraper
from typing import List

def update_env_file(key: str, value: str) -> None:
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    set_key(env_path, key, value)
    load_dotenv(override=True)

def main():
    st.title("Mass Image Scraper")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Scrape", "Settings", "About"])
    
    with tab1:
        # Search configuration
        search_query = st.text_input("Enter search terms:", placeholder="e.g., nature landscape")
        
        # Source selection with radio buttons for better UX
        st.subheader("Select Image Source")
        source_type = st.radio(
            "Choose source type:",
            ["API Services", "Web Scraping"],
            help="Select whether to use API services or web scraping"
        )
        
        if source_type == "API Services":
            api_source = st.selectbox(
                "Select API service:",
                ["Unsplash", "Pexels"],
                help="Choose which API service to use"
            )
        else:
            web_source = st.selectbox(
                "Select web source:",
                ["Google Images", "Getty Images", "Shutterstock"],
                help="Choose which website to scrape"
            )
        
        # Number of images
        num_images = st.number_input(
            "Number of images:",
            min_value=1,
            max_value=50,
            value=6
        )
        
        if st.button("Start Scraping"):
            if not search_query:
                st.error("Please enter search terms")
                return
                
            if not selected_sources:
                st.error("Please select at least one source")
                return
                
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            api_scraper = APIImageScraper()
            total_images = 0
            errors = []
            
            for idx, source in enumerate(selected_sources):
                status_text.text(f"Scraping from {source}...")
                
                if source in ["unsplash", "pexels"]:
                    scrape_func = getattr(api_scraper, f"scrape_{source}")
                    images, error = scrape_func(search_query, num_images)
                    if error:
                        errors.append(f"{source}: {error['error']}")
                    total_images += len(images)
                else:
                    # Existing scraping logic for other sources
                    pass
                
                progress_bar.progress((idx + 1) / len(selected_sources))
            
            if errors:
                st.error("\n".join(errors))
            
            status_text.text(f"Completed! Total images found: {total_images}")
    
    with tab2:
        # API and URL Configuration
        with st.expander("Configure Services", expanded=True):
            st.subheader("Unsplash Configuration")
            unsplash_url = st.text_input(
                "Unsplash API URL",
                value=os.getenv('UNSPLASH_API_URL', 'https://api.unsplash.com/search/photos'),
                help="Enter your Unsplash API endpoint URL"
            )
            unsplash_key = st.text_input(
                "Unsplash API Key", 
                type="password",
                value=os.getenv('UNSPLASH_ACCESS_KEY', ''),
                help="Enter your Unsplash API access key"
            )
            
            st.subheader("Pexels Configuration")
            pexels_url = st.text_input(
                "Pexels API URL",
                value=os.getenv('PEXELS_API_URL', 'https://api.pexels.com/v1/search'),
                help="Enter your Pexels API endpoint URL"
            )
            pexels_key = st.text_input(
                "Pexels API Key", 
                type="password",
                value=os.getenv('PEXELS_API_KEY', ''),
                help="Enter your Pexels API access key"
            )
            
            st.subheader("BrightData Configuration")
            brightdata_url = st.text_input(
                "BrightData Webdriver URL",
                value=os.getenv('SBR_WEBDRIVER', 'http://localhost:4444/wd/hub'),
                help="Enter your BrightData webdriver URL"
            )
            
            if st.button("Save Configuration"):
                # Update all configuration values
                if unsplash_url:
                    update_env_file('UNSPLASH_API_URL', unsplash_url)
                if unsplash_key:
                    update_env_file('UNSPLASH_ACCESS_KEY', unsplash_key)
                if pexels_url:
                    update_env_file('PEXELS_API_URL', pexels_url)
                if pexels_key:
                    update_env_file('PEXELS_API_KEY', pexels_key)
                if brightdata_url:
                    update_env_file('SBR_WEBDRIVER', brightdata_url)
                st.success("Configuration saved successfully!")
                st.rerun()

    with tab3:
        st.write("""
        # About Mass Image Scraper
        
        This tool allows you to scrape images from multiple sources simultaneously.
        
        ## Features
        - Multi-source image scraping
        - API integration for high-quality images
        - Customizable search parameters
        - Download limit management
        
        ## Sources
        - Google Images
        - Getty Images
        - Shutterstock
        - Unsplash API
        - Pexels API
        """)

if __name__ == "__main__":
            st.success("Parsed data saved to parsed_data.xlsx")
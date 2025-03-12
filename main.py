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
        
        # Initialize selected_sources
        selected_sources = []
        
        if source_type == "API Services":
            api_source = st.selectbox(
                "Select API service:",
                ["Unsplash", "Pexels"],
                help="Choose which API service to use"
            )
            selected_sources = [api_source.lower()]
        else:
            web_source = st.selectbox(
                "Select web source:",
                ["Google Images", "Getty Images", "Shutterstock"],
                help="Choose which website to scrape"
            )
            # Convert "Google Images" to "google" for internal use
            selected_sources = [web_source.split()[0].lower()]
        
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
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            debug_text = st.empty()  # Add debug information area
            
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
                    try:
                        from selenium import webdriver
                        from selenium.webdriver.chrome.options import Options
                        from scrape import scrape_images
                        
                        # Setup Chrome options
                        chrome_options = Options()
                        chrome_options.add_argument('--no-sandbox')
                        chrome_options.add_argument('--disable-dev-shm-usage')
                        # chrome_options.add_argument('--headless')  # Comment this out for debugging
                        
                        debug_text.text("Initializing Chrome driver...")
                        driver = webdriver.Chrome(options=chrome_options)
                        
                        debug_text.text("Starting image scraping...")
                        images, stats = scrape_images(
                            driver=driver,
                            search_query=search_query,
                            max_images=num_images,
                            source=source
                        )
                        
                        debug_text.text(f"Scraping completed. Stats: {stats}")
                        total_images += stats["successful"]
                        if stats["failed"] > 0:
                            errors.append(f"{source}: Failed to download {stats['failed']} images")
                        if stats["skipped"] > 0:
                            errors.append(f"{source}: Skipped {stats['skipped']} images")
                        
                        driver.quit()
                    except Exception as e:
                        errors.append(f"{source}: {str(e)}")
                        debug_text.text(f"Error details: {str(e)}")
                
                progress_bar.progress((idx + 1) / len(selected_sources))
            
            if errors:
                st.error("\n".join(errors))
            
            if total_images == 0:
                st.warning("No images were found. This might be due to:")
                st.write("1. Chrome driver not properly installed")
                st.write("2. Network connectivity issues")
                st.write("3. Website blocking automated access")
                st.write("\nTry running these commands in your terminal:")
                st.code("pip install webdriver-manager")
                st.code("playwright install")
            else:
                status_text.text(f"Completed! Total images found: {total_images}")
    
    with tab2:
        st.subheader("Website Content Analyzer")
        
        # Simple URL input
        website_url = st.text_input("Enter website URL:", placeholder="https://example.com")
        
        if website_url:
            # Analysis type selection
            analysis_type = st.selectbox(
                "What would you like to do with this website?",
                [
                    "Analyze Products and Prices",
                    "Generate Website Summary",
                    "Extract Contact Information",
                    "Create Content Spreadsheet",
                    "Custom Analysis"
                ]
            )

            if st.button("Analyze"):
                with st.spinner("Analyzing website content..."):
                    try:
                        # Fetch and process website content
                        html_content, driver = scrape_website(website_url)
                        body_content = extract_body_content(html_content)
                        cleaned_content = clean_body_content(body_content)
                        
                        # Get analysis based on selected type
                        result = analyze_website_content(cleaned_content, analysis_type)
                        
                        # Display results based on analysis type
                        if analysis_type == "Generate Website Summary":
                            st.markdown("### Website Summary")
                            st.write(result["summary"])
                            
                        elif analysis_type == "Analyze Products and Prices":
                            st.markdown("### Product Analysis")
                            df = pd.DataFrame(result["products"])
                            st.dataframe(df)
                            
                            if st.button("Download as Excel"):
                                df.to_excel("products.xlsx", index=False)
                                with open("products.xlsx", 'rb') as f:
                                    st.download_button(
                                        "Click to Download",
                                        f,
                                        "website_products.xlsx",
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                            
                        elif analysis_type == "Extract Contact Information":
                            st.markdown("### Contact Information")
                            st.json(result["contacts"])
                            
                        elif analysis_type == "Create Content Spreadsheet":
                            st.markdown("### Content Structure")
                            df = pd.DataFrame(result["content"])
                            st.dataframe(df)
                            
                            if st.button("Download as Excel"):
                                df.to_excel("content.xlsx", index=False)
                                with open("content.xlsx", 'rb') as f:
                                    st.download_button(
                                        "Click to Download",
                                        f,
                                        "website_content.xlsx",
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                            
                        elif analysis_type == "Custom Analysis":
                            custom_query = st.text_area(
                                "What would you like to know about this website?",
                                placeholder="e.g., Find all article titles and their publication dates"
                            )
                            if custom_query:
                                result = analyze_website_content(cleaned_content, "custom", custom_query)
                                st.markdown("### Analysis Results")
                                st.write(result["custom"])
                        
                        driver.quit()
                        
                    except Exception as e:
                        st.error(f"Error analyzing website: {str(e)}")
    
    with tab3:
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

if __name__ == "__main__":
    main()  # Just call main(), remove the "Parsed data saved" message

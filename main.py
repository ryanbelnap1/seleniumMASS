import streamlit as st
import os
from dotenv import load_dotenv
from seleniumMASS.scraper import ImageScraper
from services.image_service import ImageService

# Load environment variables
load_dotenv()

def main():
    st.title("Image Scraper Application")
    
    # Initialize services
    image_service = ImageService()
    scraper = ImageScraper(headless=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        search_query = st.text_input("Search Query")
        source = st.selectbox(
            "Image Source",
            ["google", "getty", "shutterstock", "unsplash", "pexels"]
        )
        num_images = st.number_input("Number of Images", min_value=1, max_value=100, value=10)
        
    # Main content area
    if st.button("Start Scraping"):
        if not search_query:
            st.error("Please enter a search query")
            return
            
        try:
            with st.spinner(f"Scraping {num_images} images from {source}..."):
                # Here you would implement the actual scraping logic
                st.info("Scraping functionality to be implemented")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            
    # Display downloaded images
    st.header("Downloaded Images")
    image_dir = os.path.join("downloaded_images", f"{source}_images")
    if os.path.exists(image_dir):
        images = os.listdir(image_dir)
        if images:
            for image in images:
                image_path = os.path.join(image_dir, image)
                st.image(image_path, caption=image)
        else:
            st.info("No images downloaded yet")

if __name__ == "__main__":
    main()  # Just call main(), remove the "Parsed data saved" message

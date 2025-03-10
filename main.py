import streamlit as st
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content,
)
from parse import parse_with_ollama
import pandas as pd

# Streamlit UI
st.title("AI Web Scraper")
url = st.text_input("Enter Website URL")
sbr_webdriver_url = st.text_input("Enter the SBR_WEBDRIVER URL")

# Step 1: Scrape the Website
if st.button("Scrape Website"):
    if url and sbr_webdriver_url:
        st.write("Scraping the website...")

        # Scrape the website
        dom_content = scrape_website(url, sbr_webdriver_url)
        body_content = extract_body_content(dom_content)
        cleaned_content = clean_body_content(body_content)

        # Store the DOM content in Streamlit session state
        st.session_state.dom_content = cleaned_content

        # Display the DOM content in an expandable text box
        with st.expander("View DOM Content"):
            st.text_area("DOM Content", cleaned_content, height=300)
    else:
        st.error("Please enter both the Website URL and the SBR_WEBDRIVER URL.")

# Step 2: Ask Questions About the DOM Content
if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe what you want to parse")

    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content...")

            # Parse the content with Ollama
            dom_chunks = split_dom_content(st.session_state.dom_content)
            parsed_result = parse_with_ollama(dom_chunks, parse_description)
            st.write(parsed_result)

            # Convert parsed results to DataFrame and save to Excel
            parsed_data = parsed_result.split('\n')
            df = pd.DataFrame(parsed_data, columns=["Parsed Data"])
            df.to_excel("parsed_data.xlsx", index=False)
            st.success("Parsed data saved to parsed_data.xlsx")
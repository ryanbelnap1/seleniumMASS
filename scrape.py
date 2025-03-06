from selenium.webdriver import Remote, Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

chrome_driver_path = "./chromedriver"

def scrape_website(website, sbr_webdriver_url=None):
    print("Connecting to Scraping Browser...")
    driver = None
    try:
        if sbr_webdriver_url:
            sbr_connection = ChromiumRemoteConnection(sbr_webdriver_url, "goog", "chrome")
            driver = Remote(sbr_connection, options=ChromeOptions())
            driver.get(website)
        else:
            raise ValueError("SBR_WEBDRIVER URL is not provided. Falling back to local driver.")
    except Exception as e:
        print(f"Failed to connect using SBR_WEBDRIVER: {e}")
        print("Falling back to local driver...")
        options = ChromeOptions()
        driver = Chrome(service=Service(chrome_driver_path), options=options)
        driver.get(website)

    print("Waiting captcha to solve...")
    solve_res = driver.execute(
        "executeCdpCommand",
        {
            "cmd": "Captcha.waitForSolve",
            "params": {"detectTimeout": 10000},
        },
    )
    print("Captcha solve status:", solve_res["value"]["status"])
    print("Navigated! Scraping page content...")
    html = driver.page_source
    return html

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text or further process the content
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]
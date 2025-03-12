import subprocess
import requests
import os
import zipfile
import platform
from pathlib import Path

def get_chrome_version():
    """Get the installed Chrome version."""
    try:
        # For Ubuntu/Linux
        output = subprocess.check_output(['google-chrome', '--version'])
        version = output.decode('utf-8').strip().split()[-1]
        return version.split('.')[0]  # Return major version number
    except:
        try:
            # Alternative method for Linux
            output = subprocess.check_output(['chromium-browser', '--version'])
            version = output.decode('utf-8').strip().split()[-1]
            return version.split('.')[0]
        except:
            raise Exception("Could not determine Chrome version. Is Chrome installed?")

def download_chromedriver():
    """Download and setup the correct ChromeDriver version."""
    try:
        # Get Chrome version
        chrome_version = get_chrome_version()
        
        # Get the latest ChromeDriver version for this Chrome version
        url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_version}"
        response = requests.get(url)
        driver_version = response.text.strip()

        # Create drivers directory if it doesn't exist
        drivers_dir = Path(__file__).parent / "drivers"
        drivers_dir.mkdir(exist_ok=True)

        # Set the chromedriver path
        if platform.system() == "Windows":
            chromedriver_name = "chromedriver.exe"
        else:
            chromedriver_name = "chromedriver"
        
        chromedriver_path = drivers_dir / chromedriver_name

        # Download ChromeDriver
        print(f"Downloading ChromeDriver version {driver_version}...")
        if platform.system() == "Windows":
            zip_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_win32.zip"
        else:
            zip_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_linux64.zip"
        
        response = requests.get(zip_url)
        zip_path = drivers_dir / "chromedriver.zip"
        
        with open(zip_path, 'wb') as f:
            f.write(response.content)

        # Extract ChromeDriver
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(drivers_dir)

        # Make ChromeDriver executable on Linux/Mac
        if platform.system() != "Windows":
            os.chmod(chromedriver_path, 0o755)

        # Clean up
        os.remove(zip_path)
        
        return str(chromedriver_path)

    except Exception as e:
        raise Exception(f"Failed to setup ChromeDriver: {str(e)}")
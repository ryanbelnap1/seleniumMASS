#!/bin/bash

# Function to log messages
log() {
    echo "[SETUP] $1"
}

# Install Chrome if not present
if ! command -v google-chrome &> /dev/null; then
    log "Installing Google Chrome..."
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install -y ./google-chrome-stable_current_amd64.deb
    rm google-chrome-stable_current_amd64.deb
fi

# Setup ChromeDriver with additional configurations
log "Setting up ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}" -O chrome_version
DRIVER_VERSION=$(cat chrome_version)
rm chrome_version
wget -q "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
chmod +x chromedriver

# Add additional permissions for undetectable operation
sudo chown root:root chromedriver
sudo chmod 755 chromedriver
sudo mv chromedriver /usr/local/bin/
rm chromedriver_linux64.zip

# Create Chrome policies directory for additional settings
sudo mkdir -p /etc/opt/chrome/policies/managed/
cat << EOF | sudo tee /etc/opt/chrome/policies/managed/chrome_policies.json
{
    "CommandLineFlagSecurityWarningsEnabled": false,
    "DefaultBrowserSettingEnabled": false,
    "ChromeCleanupEnabled": false,
    "MetricsReportingEnabled": false
}
EOF

# Setup Python environment
log "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup Ollama
check_ollama
check_ollama_service
check_tinyllama

# Create directories
log "Creating directories..."
mkdir -p downloaded_images/{google_images,getty_images,shutterstock,unsplash_images,pexels_images}

# Set permissions
log "Setting permissions..."
chmod +x *.py
chmod 755 downloaded_images
chmod 755 downloaded_images/*
[ -f ".env" ] && chmod 600 .env

# Start the application
log "Starting the application..."
streamlit run main.py
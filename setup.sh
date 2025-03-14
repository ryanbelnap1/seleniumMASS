#!/bin/bash

# Function to log messages
log() {
    echo "[SETUP] $1"
}

# Function to check command status
check_status() {
    if [ $? -ne 0 ]; then
        log "Error: $1"
        exit 1
    fi
}

# Create directory structure
log "Creating directory structure..."
mkdir -p services
mkdir -p downloaded_images/{google_images,getty_images,shutterstock_images,unsplash_images,pexels_images}
chmod -R 755 downloaded_images services

# Create virtual environment
log "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
check_status "Failed to activate virtual environment"

# Install requirements
log "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt
check_status "Failed to install Python packages"

# Setup API configuration
log "Setting up API configuration..."
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
UNSPLASH_API_URL=https://api.unsplash.com
PEXELS_API_URL=https://api.pexels.com/v1
SBR_WEBDRIVER=http://localhost:4444/wd/hub
EOF
fi

log "Setup complete! Run 'source run.sh' to start the application"

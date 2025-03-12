#!/bin/bash

# Function to log messages
log() {
    echo "[SETUP] $1"
}

# Check if Ollama is installed
check_ollama() {
    if ! command -v ollama &> /dev/null; then
        log "Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
    fi
}

# Install system dependencies and set up environment
log "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv wget unzip curl

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

# Create directories and set permissions
log "Setting up directories and permissions..."
mkdir -p downloaded_images/{google_images,getty_images,shutterstock,unsplash_images,pexels_images}
chmod +x *.py
chmod +x *.sh
chmod 755 downloaded_images
chmod 755 downloaded_images/*
[ -f ".env" ] && chmod 600 .env

# Start the application
log "Starting the application..."
streamlit run main.py
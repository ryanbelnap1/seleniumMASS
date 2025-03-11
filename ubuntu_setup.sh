#!/bin/bash

# Function to log messages
log() {
    echo "[UBUNTU SETUP] $1"
}

# Install dos2unix if not present
if ! command -v dos2unix &> /dev/null; then
    log "Installing dos2unix..."
    sudo apt-get update
    sudo apt-get install -y dos2unix
fi

# Convert line endings
log "Converting line endings for shell scripts..."
dos2unix setup.sh
dos2unix run.sh

# Set execute permissions
log "Setting execute permissions..."
chmod +x setup.sh
chmod +x run.sh

log "Ubuntu setup complete! You can now run: ./setup.sh"
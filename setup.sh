#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print with color and prefix
log() {
    echo -e "${BLUE}[SETUP]${NC} ${GREEN}$1${NC}"
}

# Error handling
set -e
trap 'echo "Error occurred. Setup failed." >&2' ERR

# Check Python version
if ! command -v python3 &> /dev/null; then
    log "Installing Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Create and activate virtual environment
if [ ! -d "venv" ]; then
    log "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
log "Activating virtual environment..."
source venv/bin/activate

# Update pip
log "Updating pip..."
python -m pip install --upgrade pip

# Install requirements
log "Installing Python dependencies..."
pip install -r requirements.txt

# Update Chrome if installed, install if not
if ! command -v google-chrome &> /dev/null; then
    log "Installing Google Chrome..."
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg -i google-chrome-stable_current_amd64.deb
    sudo apt --fix-broken install -y
    rm google-chrome-stable_current_amd64.deb
else
    log "Updating Google Chrome..."
    sudo apt update
    sudo apt install --only-upgrade google-chrome-stable -y
fi

# Set up chromedriver permissions
if [ -f "chromedriver" ]; then
    log "Setting chromedriver permissions..."
    chmod +x chromedriver
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    log "Creating .env file..."
    echo "SBR_WEBDRIVER=http://localhost:4444/wd/hub" > .env
fi

# Create necessary directories
log "Creating necessary directories..."
mkdir -p downloaded_images/{google_images,getty_images,shutterstock}

# Final setup message
log "Setup complete! Run 'source run.sh' to start the application"

# Create run script
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
streamlit run main.py
EOF

chmod +x run.sh
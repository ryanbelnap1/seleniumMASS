#!/bin/bash

# Function to log messages
log() {
    echo "[SETUP] $1"
}

# Function to check and install Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        log "Installing Python..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
    fi
}

# Function to check and install Chrome
install_chrome() {
    if ! command -v google-chrome &> /dev/null; then
        log "Installing Google Chrome..."
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
    else
        log "Updating Google Chrome..."
        sudo apt-get update
        sudo apt-get install --only-upgrade google-chrome-stable
    fi
}

# Function to prompt for API keys
prompt_api_keys() {
    echo "Would you like to configure API keys for additional image sources? (y/n)"
    read -r configure_apis

    if [ "$configure_apis" = "y" ]; then
        echo "Enter your Unsplash API key (press Enter to skip):"
        read -r unsplash_key
        
        echo "Enter your Pexels API key (press Enter to skip):"
        read -r pexels_key
        
        # Create or update .env file
        if [ ! -f ".env" ]; then
            echo "SBR_WEBDRIVER=http://localhost:4444/wd/hub" > .env
        fi
        
        # Add or update API keys if provided
        if [ ! -z "$unsplash_key" ]; then
            if grep -q "UNSPLASH_ACCESS_KEY" .env; then
                sed -i "s/UNSPLASH_ACCESS_KEY=.*/UNSPLASH_ACCESS_KEY=$unsplash_key/" .env
            else
                echo "UNSPLASH_ACCESS_KEY=$unsplash_key" >> .env
            fi
        fi
        
        if [ ! -z "$pexels_key" ]; then
            if grep -q "PEXELS_API_KEY" .env; then
                sed -i "s/PEXELS_API_KEY=.*/PEXELS_API_KEY=$pexels_key/" .env
            else
                echo "PEXELS_API_KEY=$pexels_key" >> .env
            fi
        fi
    fi
}

# Set permissions for Python files
log "Setting permissions for Python files..."
chmod +x *.py

# Check and install dependencies
check_python
install_chrome

# Create and activate virtual environment
log "Creating virtual environment..."
python3 -m venv venv

log "Activating virtual environment..."
source venv/bin/activate

# Update pip
log "Updating pip..."
pip install --upgrade pip

# Install Python dependencies
log "Installing Python dependencies..."
pip install -r requirements.txt

# Set chromedriver permissions
log "Setting chromedriver permissions..."
if [ -f "chromedriver" ]; then
    chmod +x chromedriver
fi

# Create .env file if it doesn't exist
log "Creating .env file..."
if [ ! -f ".env" ]; then
    cp sample.env .env
fi

# Create necessary directories
log "Creating necessary directories..."
mkdir -p downloaded_images/{google_images,getty_images,shutterstock,unsplash_images,pexels_images}

# Prompt for API keys
log "Setting up API configuration..."
prompt_api_keys

# Create run script
log "Creating run script..."
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
streamlit run main.py
EOF

chmod +x run.sh
# Final setup message
log "Setup complete! Run 'source run.sh' to start the application"

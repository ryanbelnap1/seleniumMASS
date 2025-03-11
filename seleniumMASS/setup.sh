#!/bin/bash

# Function to log messages
log() {
    echo "[SETUP] $1"
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

# Create necessary directories
log "Creating necessary directories..."
mkdir -p downloaded_images/{google_images,getty_images,shutterstock,unsplash_images,pexels_images}

# Prompt for API keys
log "Setting up API configuration..."
prompt_api_keys

# Final setup message
log "Setup complete! Run 'source run.sh' to start the application"

# Create run script
cat > run.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
streamlit run main.py
EOF

chmod +x run.sh
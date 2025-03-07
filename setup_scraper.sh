#!/bin/bash

# Update package list and upgrade installed packages
sudo apt update && sudo apt upgrade -y

# Update Google Chrome to the latest version
sudo apt install --only-upgrade google-chrome-stable -y

# Create a virtual environment with python3 and activate it
python3 -m venv venv
source venv/bin/activate

# Install the requirements from requirements.txt
pip install -r requirements.txt

# Install ollama within the virtual environment
pip install ollama

# Run ollama command within the virtual environment
ollama run llama3.3

# Confirm the setup is complete
echo "Setup is complete!"
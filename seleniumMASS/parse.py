from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
import time
import requests

def check_ollama_service():
    """Check if Ollama service is running and accessible"""
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        return response.status_code == 200
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        return False

def analyze_website_content(content, analysis_type, custom_query=None):
    """
    Analyze website content using AI with specific focus areas
    """
    # Check if Ollama service is running
    if not check_ollama_service():
        return {
            "error": "Ollama service is not running. Please start it with 'ollama serve' command",
            "status": "failed"
        }

    try:
        # Initialize Ollama with tinyllama and optimized parameters
        model = Ollama(
            model="tinyllama",
            base_url="http://127.0.0.1:11434",
            temperature=0.3,
            num_ctx=2048,
            timeout=60
        )
        
        # Test the model connection
        try:
            model.invoke("test")
        except Exception as e:
            return {
                "error": f"Failed to communicate with Ollama model: {str(e)}",
                "status": "failed"
            }
            
    except Exception as e:
        return {
            "error": f"Failed to initialize Ollama: {str(e)}",
            "status": "failed"
        }

    # Rest of your analyze_website_content function...
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
import time
import requests

def check_ollama_service():
    """Check if Ollama service is running and accessible"""
    try:
        response = requests.get("http://127.0.0.1:11434/api/tags")
        return response.status_code == 200
    except requests.exceptions.RequestException:
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

    # Truncate content for better performance
    max_content_length = 4000
    if len(content) > max_content_length:
        content = content[:max_content_length] + "..."

    prompts = {
        "Generate Website Summary": """
            Provide a brief summary of this website content focusing on:
            1. Main purpose
            2. Key features
            3. Target audience
            Be concise and direct.
        """,
        
        "Analyze Products and Prices": """
            List only the clearly mentioned products with:
            - product_name
            - price
            - description
            Format as simple JSON.
        """,
        
        "Extract Contact Information": """
            Extract only:
            - emails
            - phones
            - addresses
            - social links
            Format as simple JSON.
        """,
        
        "Create Content Spreadsheet": """
            List main:
            - sections
            - headers
            - content blocks
            Format as simple JSON array.
        """
    }
    
    prompt_template = ChatPromptTemplate.from_template(
        "Content: {content}\nTask: {task}\nProvide structured response."
    )
    
    try:
        start_time = time.time()
        chain = prompt_template | model
        
        if analysis_type == "custom":
            task = custom_query
        else:
            task = prompts[analysis_type]
        
        result = chain.invoke({
            "content": content,
            "task": task
        })
        
        processing_time = time.time() - start_time
        
        # Process results
        response = {
            "processing_time": f"{processing_time:.2f} seconds",
            "status": "success"
        }
        
        if analysis_type == "Generate Website Summary":
            response["summary"] = result
        elif analysis_type == "Analyze Products and Prices":
            response["products"] = parse_json_result(result)
        elif analysis_type == "Extract Contact Information":
            response["contacts"] = parse_json_result(result)
        elif analysis_type == "Create Content Spreadsheet":
            response["content"] = parse_json_result(result)
        else:
            response["custom"] = result
            
        return response
        
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "status": "failed",
            "processing_time": f"{time.time() - start_time:.2f} seconds"
        }

def parse_json_result(result):
    """Convert the model's response to structured data"""
    try:
        import json
        return json.loads(result)
    except:
        return [{"content": str(result)}]

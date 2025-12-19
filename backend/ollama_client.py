import requests
import json

# Configuration
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3.1:8b" 

def ask_ollama(prompt: str) -> str:
    """
    Sends a prompt to the local Ollama instance and returns the response text.
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_ctx": 4096  # Larger context window for analyzing long code/transcripts
        }
    }

    try:
        # Timeout set to 180 seconds because detailed analysis can be slow
        res = requests.post(OLLAMA_URL, json=payload, timeout=180)
        res.raise_for_status()
        
        response_json = res.json()
        return response_json.get("response", "").strip()
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Ollama. Is it running on port 11434?")
        return "Error: Ollama is not running. Please start it with 'ollama serve'."
    except requests.exceptions.Timeout:
        return "Error: AI response timed out."
    except Exception as e:
        print(f"Ollama Error: {e}")
        return f"Error: {str(e)}"
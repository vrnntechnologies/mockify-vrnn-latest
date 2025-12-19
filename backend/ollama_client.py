import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "llama3"

def ask_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_ctx": 4096
        }
    }

    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=180)
        res.raise_for_status()
        data = res.json()
        return data["message"]["content"].strip()

    except requests.exceptions.ConnectionError:
        return "Error: Ollama is not running. Start it using `ollama serve`."
    except requests.exceptions.Timeout:
        return "Error: AI response timed out."
    except Exception as e:
        return f"Ollama Error: {str(e)}"

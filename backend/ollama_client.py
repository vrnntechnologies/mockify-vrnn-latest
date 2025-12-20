import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "mistral"

def ask_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
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
        return data.get("response", "").strip()

    except Exception as e:
        return f"Ollama Error: {str(e)}"

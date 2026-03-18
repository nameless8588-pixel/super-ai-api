from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from cachetools import TTLCache
import ollama
import sys
import os
import time

# --- Load .env ---
load_dotenv()

# --- Cache Setup (1 ghante tak same jawab store rahega) ---
cache = TTLCache(maxsize=100, ttl=3600)

# --- Path Setup ---
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_path, 'tools'))

try:
    from internet import search_internet
except:
    def search_internet(q): return "Search error."

# --- API Setup ---
app = FastAPI(title="🚀 Super AI API", version="2.0")

# --- Keys .env se ---
VALID_KEYS = {
    os.getenv("API_KEY_FREE"): "free",
    os.getenv("API_KEY_PRO"): "pro",
    os.getenv("API_KEY_BOSS"): "boss"
}

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_key(key: str = Depends(api_key_header)):
    if key not in VALID_KEYS:
        raise HTTPException(status_code=403, detail="❌ Invalid API Key!")
    return key

@app.get("/")
def home():
    return {
        "name": "Super AI API",
        "version": "2.0",
        "status": "✅ Online",
        "endpoints": ["/ask", "/search", "/stream", "/status"]
    }

@app.get("/status")
def status():
    return {
        "api": "✅ Online",
        "ai_model": "gemma3:1b",
        "internet": "✅ Active",
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    }

@app.get("/ask")
def ask(q: str, key: str = Depends(verify_key)):
    # Cache check --- same sawal ka jawab turant milega
    if q in cache:
        return {
            "sawal": q,
            "jawab": cache[q],
            "internet_use": False,
            "response_time": "0.01s ⚡ (cached)",
            "plan": VALID_KEYS[key]
        }

    start = time.time()

    # Internet check
    try:
        check = ollama.chat(model='gemma3:1b', messages=[
            {'role': 'user', 'content': f"Is '{q}' a greeting or simple chat? If yes say NO. Does it need internet search? YES/NO only"}
        ])
        context = ""
        if "YES" in check['message']['content'].upper():
            context = f"\nInternet Data: {search_internet(q)}"
    except:
        context = ""

    # AI Jawab
    response = ollama.chat(model='gemma3:1b', messages=[
        {'role': 'user', 'content': "Tu ek smart Indian dost hai. Sirf 1-2 line mein Hinglish mein jawab de. Koi explanation mat de."},
        {'role': 'assistant', 'content': "Haan bhai!"},
        {'role': 'user', 'content': f"{q} {context}"}
    ])

    reply = response['message']['content']
    cache[q] = reply  # Cache mein save karo

    return {
        "sawal": q,
        "jawab": reply,
        "internet_use": bool(context),
        "response_time": f"{round(time.time()-start, 2)}s",
        "plan": VALID_KEYS[key]
    }

@app.get("/search")
def search(q: str, key: str = Depends(verify_key)):
    start = time.time()
    result = search_internet(q)
    return {
        "query": q,
        "result": result,
        "response_time": f"{round(time.time()-start, 2)}s"
    }

@app.get("/stream")
def stream(q: str, key: str = Depends(verify_key)):
    def generate():
        for chunk in ollama.chat(model='gemma3:1b', messages=[
            {'role': 'user', 'content': "Hinglish mein jawab de."},
            {'role': 'user', 'content': q}
        ], stream=True):
            yield chunk['message']['content']
    return StreamingResponse(generate(), media_type="text/plain")
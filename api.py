from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from cachetools import TTLCache
from groq import Groq
import sys
import os
import time

load_dotenv()
cache = TTLCache(maxsize=100, ttl=3600)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_path, 'tools'))
try:
    from internet import search_internet
except:
    def search_internet(q): return "Search error."

app = FastAPI(title="Super AI API", version="2.0")
VALID_KEYS = {os.getenv("API_KEY_FREE"): "free", os.getenv("API_KEY_PRO"): "pro", os.getenv("API_KEY_BOSS"): "boss"}
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_key(key: str = Depends(api_key_header)):
    if key not in VALID_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key!")
    return key

@app.get("/")
def home():
    return {"name": "Super AI API", "version": "2.0", "status": "Online"}

@app.get("/ask")
def ask(q: str, key: str = Depends(verify_key)):
    if q in cache:
        return {"sawal": q, "jawab": cache[q], "cached": True}
    start = time.time()
    try:
        context = search_internet(q)
    except:
        context = ""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": "Tu ek smart Indian dost hai. Hinglish mein jawab de."},
            {"role": "assistant", "content": "Haan bhai!"},
            {"role": "user", "content": f"{q} {context}"}
        ]
    )
    reply = response.choices[0].message.content
    cache[q] = reply
    return {"sawal": q, "jawab": reply, "response_time": f"{round(time.time()-start, 2)}s", "plan": VALID_KEYS[key]}

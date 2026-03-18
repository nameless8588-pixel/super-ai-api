from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
from cachetools import TTLCache
from groq import Groq
import requests
import base64
import sys
import os
import time

load_dotenv()
cache = TTLCache(maxsize=100, ttl=3600)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_REPO = os.getenv("GITHUB_REPO")
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_path, 'tools'))
try:
    from internet import search_internet
except:
    def search_internet(q): return "Search error."

app = FastAPI(title="Super AI API", version="3.0")
VALID_KEYS = {os.getenv("API_KEY_FREE"): "free", os.getenv("API_KEY_PRO"): "pro", os.getenv("API_KEY_BOSS"): "boss"}
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_key(key: str = Depends(api_key_header)):
    if key not in VALID_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key!")
    return key

@app.get("/")
def home():
    return {"name": "Super AI API", "version": "3.0", "status": "Online"}

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

@app.get("/create")
def create(task: str, filename: str = "ai_generated.py", key: str = Depends(verify_key)):
    start = time.time()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Tu ek expert Python developer hai. Sirf Python code likh, koi explanation nahi. Code ko ```python ``` mein mat wrap kar."},
            {"role": "user", "content": f"Yeh banao: {task}"}
        ]
    )
    code = response.choices[0].message.content
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{filename}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    check = requests.get(url, headers=headers)
    data = {"message": f"AI ne banaya: {filename}", "content": base64.b64encode(code.encode()).decode()}
    if check.status_code == 200:
        data["sha"] = check.json()["sha"]
    requests.put(url, json=data, headers=headers)
    return {"task": task, "filename": filename, "code": code, "response_time": f"{round(time.time()-start, 2)}s"}

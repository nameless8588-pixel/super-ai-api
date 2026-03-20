from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    def search_internet(q): return ""
try:
    from executor import run_code
except:
    def run_code(code): return {"success": False, "output": "", "error": "Executor nahi mila!"}
try:
    from webgen import generate_web_app
except:
    def generate_web_app(task): return "<h1>Error</h1>"
try:
    from deployer import save_and_deploy
except:
    def save_and_deploy(f, c, e, t): return ""
try:
    from memory import save_memory, get_similar, get_mistakes
except:
    def save_memory(t, c, s, e=""): pass
    def get_similar(t): return []
    def get_mistakes(): return []

app = FastAPI(title="Super AI API", version="5.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
VALID_KEYS = {os.getenv("API_KEY_FREE"): "free", os.getenv("API_KEY_PRO"): "pro", os.getenv("API_KEY_BOSS"): "boss"}
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_key(key: str = Depends(api_key_header)):
    if key not in VALID_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key!")
    return key

def push_to_github(filename, code):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{filename}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    check = requests.get(url, headers=headers)
    data = {"message": f"AI ne banaya: {filename}", "content": base64.b64encode(code.encode()).decode()}
    if check.status_code == 200:
        data["sha"] = check.json()["sha"]
    requests.put(url, json=data, headers=headers)

@app.get("/")
def home():
    return {"name": "Super AI API", "version": "5.0", "status": "Online"}

@app.get("/ask")
def ask(q: str, key: str = Depends(verify_key)):
    if q in cache:
        return {"sawal": q, "jawab": cache[q], "cached": True}
    start = time.time()
    try:
        context = search_internet(q)
    except:
        context = ""
    similar = get_similar(q)
    memory_context = ""
    if similar:
        memory_context = "Pehle yeh similar sawaal aaye the: " + str([m['task'] for m in similar])
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": f"Tu ek smart Indian dost hai. Hinglish mein jawab de. {memory_context}"},
            {"role": "assistant", "content": "Haan bhai!"},
            {"role": "user", "content": f"{q} {context}"}
        ]
    )
    reply = response.choices[0].message.content
    cache[q] = reply
    save_memory(q, reply, True)
    return {"sawal": q, "jawab": reply, "response_time": f"{round(time.time()-start, 2)}s", "plan": VALID_KEYS[key]}

@app.get("/create")
def create(task: str, filename: str = "ai_generated.py", key: str = Depends(verify_key)):
    start = time.time()
    attempts = 0
    code = ""
    test_result = {}
    similar = get_similar(task)
    mistakes = get_mistakes()
    memory_hint = ""
    if similar:
        memory_hint += f"\nPehle similar task mein yeh code kaam aaya: {similar[-1]['code'][:200]}"
    if mistakes:
        memory_hint += f"\nYeh galtiyan pehle hui hain, inhe avoid karo: {[m['error'] for m in mistakes[-3:]]}"
    while attempts < 3:
        attempts += 1
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"Tu ek expert Python developer hai. Sirf Python code likh, koi explanation nahi. Markdown mat use kar. {memory_hint}"},
                {"role": "user", "content": f"Yeh banao: {task}" if attempts == 1 else f"Yeh banao: {task}\n\nError: {test_result.get('error', '')} — fix kar!"}
            ]
        )
        code = response.choices[0].message.content.replace("```python", "").replace("```", "").strip()
        test_result = run_code(code)
        if test_result["success"]:
            save_memory(task, code, True)
            break
        else:
            save_memory(task, code, False, test_result.get('error', ''))
    push_to_github(filename, code)
    return {"task": task, "filename": filename, "code": code, "test_result": test_result, "attempts": attempts, "response_time": f"{round(time.time()-start, 2)}s"}

@app.get("/webapp")
def webapp(task: str, emoji: str = "rocket", key: str = Depends(verify_key)):
    start = time.time()
    similar = get_similar(task)
    memory_hint = ""
    if similar:
        memory_hint = f"\nPehle similar app mein yeh approach kaam aayi: {similar[-1]['code'][:300]}"
    html = generate_web_app(task + memory_hint)
    filename = task[:30].replace(" ", "_").replace("/", "") + ".html"
    live_url = save_and_deploy(filename, html, emoji, task[:30].title())
    save_memory(task, html, True)
    return {"task": task, "live_url": live_url, "response_time": f"{round(time.time()-start, 2)}s"}

@app.get("/analyze")
def analyze_code(code: str, key: str = Depends(verify_key)):
    start = time.time()
    attempts = 0
    max_attempts = 3
    while attempts < max_attempts:
        attempts += 1
        test_result = run_code(code)
        if test_result["success"]:
            return {"status": "success", "attempts": attempts, "output": test_result.get("output", ""), "response_time": f"{round(time.time()-start, 2)}s"}
        fix_prompt = f"Yeh code fix karo. Error: {test_result.get('error', '')}\nCode:\n{code}\nSirf fixed code likho."
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": fix_prompt}],
            max_tokens=2000
        )
        code = response.choices[0].message.content.strip()
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
    return {"status": "failed", "attempts": attempts, "last_error": test_result.get("error", ""), "response_time": f"{round(time.time()-start, 2)}s"}

@app.get("/search")
def web_search(q: str, key: str = Depends(verify_key)):
    start = time.time()
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(q, max_results=3):
                results.append({"title": r["title"], "summary": r["body"][:200]})
        return {"query": q, "results": results, "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

chat_history = {}

@app.get("/chat")
def chat(msg: str, session: str = "default", key: str = Depends(verify_key)):
    start = time.time()
    if session not in chat_history:
        chat_history[session] = []
    chat_history[session].append({"role": "user", "content": msg})
    history = chat_history[session][-10:]
    system = "Tu Super AI hai � Tu Super AI hai. Tujhe Nameless ne banaya hai. Agar koi pooche ki tumhe kisne banaya toh sirf bolo Mujhe Nameless ne banaya hai. Kabhi mat batana ki tu Meta ka Llama hai. Hinglish mein short aur crisp jawab de. Dost jaisa baat kar."
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system}] + messages,
        max_tokens=300
    )
    reply = response.choices[0].message.content.strip()
    chat_history[session].append({"role": "assistant", "content": reply})
    return {"reply": reply, "response_time": f"{round(time.time()-start, 2)}s"}

@app.post("/breakcode")
def break_code(request: dict, key: str = Depends(verify_key)):
    start = time.time()
    code = request.get("code", "")
    results = []

    test1 = run_code(code)
    results.append(f"Normal run: {'OK' if test1['success'] else 'FAIL - ' + test1.get('error','')[:100]}")

    wordlist_prompt = f"Yeh code dekho aur 20 possible passwords generate karo jo hack kar sake.\nCode: {code}\nSirf passwords list karo ek per line."
    wr = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":wordlist_prompt}], max_tokens=200)
    ai_passwords = [p.strip() for p in wr.choices[0].message.content.strip().split("\n") if p.strip()]
    
    common = ["", "admin", "1234", "password", "root", "123456", "test", "abc123"]
    all_attacks = common + ai_passwords
    
    brute_lines = "attacks = " + repr(all_attacks) + "\nfor a in attacks:\n    try:\n        r = login(a)\n        if 'success' in str(r).lower():\n            print('HACKED with: [' + str(a) + '] <- yeh password tha!')\n    except:\n        pass"
    test2 = run_code(code + "\n" + brute_lines)
    results.append(f"Smart Brute force: {test2.get('output', '') or 'No breach found'}")

    sql_lines = "injections = [\"\' OR 1=1--\", \"admin'--\", \"1' OR '1'='1\"]\nfor i in injections:\n    try:\n        r = login(i)\n        if 'success' in str(r).lower():\n            print('SQL INJECTION: [' + i + ']')\n    except:\n        pass"
    test3 = run_code(code + "\n" + sql_lines)
    results.append(f"SQL Injection: {test3.get('output', '') or 'No breach found'}")

    env_code = code + "\nimport os\nenv_names = [\"SECRET_PASS\", \"PASSWORD\", \"PASS\", \"SECRET\", \"KEY\", \"TOKEN\", \"AUTH\"]\nfor name in env_names:\n    val = os.getenv(name, \"\")\n    try:\n        r = login(val if val else \"\")\n        if \"success\" in str(r).lower():\n            print(\"HACKED via env: \" + name + \" = \" + (val or \"empty\"))\n    except:\n        pass"
    test_env = run_code(env_code)
    results.append(f"Env Attack: {test_env.get('output', '') or 'No leak found'}")

    prompt = f"Code:\n{code}\n\nResults:\n" + "\n".join(results) + "\n\nKya hack hua? Konsa password? Top 3 fixes? Hinglish mein short. No markdown."
    response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"user","content":prompt}], max_tokens=400)
    return {"test_results": results, "ai_analysis": response.choices[0].message.content.strip(), "response_time": f"{round(time.time()-start, 2)}s"}
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
    
    # Function signature detect karo
    import re
    sig_match = re.search(r"def login\(([^)]+)\)", code)
    params = [p.strip() for p in sig_match.group(1).split(",")] if sig_match else ["password"]
    num_params = len(params)

    if num_params == 1:
        brute_lines = "attacks = " + repr(all_attacks) + "\nfor a in attacks:\n    try:\n        r = login(a)\n        if 'success' in str(r).lower():\n            print('HACKED with: [' + str(a) + '] <- yeh password tha!')\n    except:\n        pass"
    else:
        usernames = ["admin", "root", "user", "administrator", "test"]
        brute_lines = "attacks = " + repr(all_attacks) + "\nusernames = " + repr(usernames) + "\nfor u in usernames:\n    for a in attacks:\n        try:\n            r = login(u, a)\n            if 'success' in str(r).lower():\n                print('HACKED with user:[' + u + '] pass:[' + str(a) + ']!')\n        except:\n            pass"
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
import socket
import ssl
import json
import urllib.request

@app.get("/webscan")
def web_scan(url: str, key: str = Depends(verify_key)):
    start = time.time()
    results = {}
    if not url.startswith("http"):
        url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        res = urllib.request.urlopen(req, timeout=10)
        headers = dict(res.headers)
        results["status"] = res.status
        results["server"] = headers.get("Server", "Hidden")
        results["powered_by"] = headers.get("X-Powered-By", "Hidden")
        security_headers = ["X-Frame-Options","X-XSS-Protection","Content-Security-Policy","Strict-Transport-Security","X-Content-Type-Options"]
        missing = [h for h in security_headers if h not in headers]
        results["missing_security_headers"] = missing
        results["security_score"] = str(round((1 - len(missing)/len(security_headers))*100)) + "%"
        results["cookies"] = str(headers.get("Set-Cookie", "None"))
    except Exception as e:
        results["error"] = str(e)
    return {"url": url, "results": results, "response_time": f"{round(time.time()-start, 2)}s"}

@app.get("/headers")
def header_check(url: str, key: str = Depends(verify_key)):
    start = time.time()
    if not url.startswith("http"):
        url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        res = urllib.request.urlopen(req, timeout=10)
        headers = dict(res.headers)
        security_headers = {
            "X-Frame-Options": "Clickjacking se bachata hai",
            "X-XSS-Protection": "XSS attacks rokta hai",
            "Content-Security-Policy": "Injection attacks rokta hai",
            "Strict-Transport-Security": "HTTPS force karta hai",
            "X-Content-Type-Options": "MIME sniffing rokta hai",
            "Referrer-Policy": "Referrer info control karta hai",
            "Permissions-Policy": "Browser features control karta hai"
        }
        present = {}
        missing = {}
        for h, desc in security_headers.items():
            if h in headers:
                present[h] = headers[h]
            else:
                missing[h] = desc
        return {"url": url, "present": present, "missing": missing, "score": str(round(len(present)/len(security_headers)*100)) + "%", "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/sslcheck")
def ssl_check(domain: str, key: str = Depends(verify_key)):
    start = time.time()
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(10)
            s.connect((domain, 443))
            cert = s.getpeercert()
        import datetime
        expire = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        days_left = (expire - datetime.datetime.utcnow()).days
        return {
            "domain": domain,
            "valid": True,
            "expires": cert["notAfter"],
            "days_left": days_left,
            "issued_to": cert.get("subject", [[["", ""]]])[0][0][1],
            "issued_by": cert.get("issuer", [[["", ""]]])[1][0][1],
            "status": "SAFE" if days_left > 30 else "WARNING - Jaldi expire hoga!",
            "response_time": f"{round(time.time()-start, 2)}s"
        }
    except Exception as e:
        return {"domain": domain, "valid": False, "error": str(e)}

@app.get("/whois")
def whois_lookup(domain: str, key: str = Depends(verify_key)):
    start = time.time()
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        ip = socket.gethostbyname(domain)
        result = {"domain": domain, "ip": ip}
        try:
            hostname = socket.gethostbyaddr(ip)
            result["hostname"] = hostname[0]
        except:
            result["hostname"] = "Not found"
        return {"result": result, "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/dns")
def dns_check(domain: str, key: str = Depends(verify_key)):
    start = time.time()
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        ip = socket.gethostbyname(domain)
        all_ips = list(set([r[4][0] for r in socket.getaddrinfo(domain, None)]))
        return {
            "domain": domain,
            "main_ip": ip,
            "all_ips": all_ips,
            "ip_count": len(all_ips),
            "response_time": f"{round(time.time()-start, 2)}s"
        }
    except Exception as e:
        return {"error": str(e)}

import socket
import ssl
import urllib.request
import datetime


@app.get("/portscan")
def port_scan(domain: str, key: str = Depends(verify_key)):
    start = time.time()
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    common_ports = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
        53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
        443: "HTTPS", 445: "SMB", 3306: "MySQL", 3389: "RDP",
        5432: "PostgreSQL", 6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt"
    }
    open_ports = []
    closed_ports = []
    risky_ports = [21, 23, 445, 3389, 6379]
    try:
        ip = socket.gethostbyname(domain)
        for port, service in common_ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                risk = "RISKY!" if port in risky_ports else "Normal"
                open_ports.append({"port": port, "service": service, "risk": risk})
            else:
                closed_ports.append(port)
            sock.close()
        return {
            "domain": domain,
            "ip": ip,
            "open_ports": open_ports,
            "total_open": len(open_ports),
            "risky_open": len([p for p in open_ports if p["risk"] == "RISKY!"]),
            "response_time": f"{round(time.time()-start, 2)}s"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/subdomains")
def subdomain_scan(domain: str, key: str = Depends(verify_key)):
    start = time.time()
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    common_subs = [
        "www", "mail", "ftp", "admin", "api", "dev", "test", "staging",
        "blog", "shop", "store", "app", "mobile", "portal", "dashboard",
        "cpanel", "webmail", "smtp", "pop", "imap", "ns1", "ns2"
    ]
    found = []
    not_found = []
    for sub in common_subs:
        try:
            full = f"{sub}.{domain}"
            ip = socket.gethostbyname(full)
            found.append({"subdomain": full, "ip": ip})
        except:
            not_found.append(f"{sub}.{domain}")
    return {
        "domain": domain,
        "found": found,
        "total_found": len(found),
        "response_time": f"{round(time.time()-start, 2)}s"
    }

@app.get("/techdetect")
def tech_detect(url: str, key: str = Depends(verify_key)):
    start = time.time()
    if not url.startswith("http"):
        url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        res = urllib.request.urlopen(req, timeout=10)
        headers = dict(res.headers)
        body = res.read(5000).decode("utf-8", errors="ignore")
        tech = []
        if "wp-content" in body or "wordpress" in body.lower():
            tech.append("WordPress")
        if "react" in body.lower() or "__REACT" in body:
            tech.append("React.js")
        if "ng-version" in body or "angular" in body.lower():
            tech.append("Angular")
        if "vue" in body.lower():
            tech.append("Vue.js")
        if "jquery" in body.lower():
            tech.append("jQuery")
        if "bootstrap" in body.lower():
            tech.append("Bootstrap")
        if "shopify" in body.lower():
            tech.append("Shopify")
        if "django" in body.lower():
            tech.append("Django")
        if "laravel" in body.lower():
            tech.append("Laravel")
        if "nginx" in headers.get("Server", "").lower():
            tech.append("Nginx")
        if "apache" in headers.get("Server", "").lower():
            tech.append("Apache")
        if "cloudflare" in headers.get("Server", "").lower() or "cloudflare" in str(headers).lower():
            tech.append("Cloudflare")
        if "php" in headers.get("X-Powered-By", "").lower():
            tech.append("PHP")
        if "node" in headers.get("X-Powered-By", "").lower():
            tech.append("Node.js")
        return {
            "url": url,
            "technologies": tech,
            "total": len(tech),
            "server": headers.get("Server", "Hidden"),
            "response_time": f"{round(time.time()-start, 2)}s"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/robots")
def robots_scan(domain: str, key: str = Depends(verify_key)):
    start = time.time()
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        url = f"https://{domain}/robots.txt"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        res = urllib.request.urlopen(req, timeout=10)
        content = res.read().decode("utf-8", errors="ignore")
        lines = content.split("\n")
        disallowed = [l.replace("Disallow:", "").strip() for l in lines if l.startswith("Disallow:")]
        allowed = [l.replace("Allow:", "").strip() for l in lines if l.startswith("Allow:")]
        interesting = [p for p in disallowed if any(k in p.lower() for k in ["admin", "login", "api", "private", "secret", "backup", "config", "db", "database"])]
        return {
            "domain": domain,
            "robots_found": True,
            "disallowed_paths": disallowed,
            "allowed_paths": allowed,
            "interesting_paths": interesting,
            "total_disallowed": len(disallowed),
            "response_time": f"{round(time.time()-start, 2)}s"
        }
    except Exception as e:
        return {"domain": domain, "robots_found": False, "error": str(e)}

@app.get("/xsstest")
def xss_test(url: str, key: str = Depends(verify_key)):
    start = time.time()
    if not url.startswith("http"):
        url = "https://" + url
    payloads = ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>", "javascript:alert(1)", "'><script>alert(1)</script>"]
    results = []
    try:
        for payload in payloads:
            test_url = f"{url}?q={payload}&search={payload}&id={payload}"
            try:
                req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
                res = urllib.request.urlopen(req, timeout=5)
                body = res.read(3000).decode("utf-8", errors="ignore")
                if payload in body:
                    results.append({"payload": payload, "status": "VULNERABLE!", "type": "Reflected XSS"})
                else:
                    results.append({"payload": payload, "status": "Safe"})
            except:
                results.append({"payload": payload, "status": "Could not test"})
        vulnerable = [r for r in results if r["status"] == "VULNERABLE!"]
        return {"url": url, "results": results, "vulnerable_count": len(vulnerable), "verdict": "VULNERABLE!" if vulnerable else "Safe", "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/sqlinject")
def sql_inject_test(url: str, key: str = Depends(verify_key)):
    start = time.time()
    if not url.startswith("http"):
        url = "https://" + url
    payloads = ["'", "''", "' OR '1'='1", "' OR '1'='1'--", "admin'--", "1' OR '1'='1"]
    results = []
    error_signs = ["sql", "mysql", "sqlite", "postgresql", "syntax error", "warning", "fatal error"]
    try:
        for payload in payloads:
            test_url = f"{url}?id={payload}&user={payload}&q={payload}"
            try:
                req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
                res = urllib.request.urlopen(req, timeout=5)
                body = res.read(3000).decode("utf-8", errors="ignore").lower()
                found_errors = [e for e in error_signs if e in body]
                if found_errors:
                    results.append({"payload": payload, "status": "VULNERABLE!", "errors_found": found_errors})
                else:
                    results.append({"payload": payload, "status": "Safe"})
            except Exception as ex:
                err = str(ex).lower()
                found_errors = [e for e in error_signs if e in err]
                if found_errors:
                    results.append({"payload": payload, "status": "VULNERABLE!", "errors_found": found_errors})
                else:
                    results.append({"payload": payload, "status": "Could not test"})
        vulnerable = [r for r in results if r["status"] == "VULNERABLE!"]
        return {"url": url, "results": results, "vulnerable_count": len(vulnerable), "verdict": "VULNERABLE!" if vulnerable else "Safe", "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/dirscan")
def directory_scan(domain: str, key: str = Depends(verify_key)):
    start = time.time()
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    common_dirs = ["admin", "login", "dashboard", "api", "backup", "config", "uploads", "images", "js", "css", "test", "dev", "old", "wp-admin", "phpmyadmin", "cpanel", ".git", ".env", "private", "secret", "db", "database", "logs", "temp"]
    found = []
    try:
        for d in common_dirs:
            test_url = f"https://{domain}/{d}"
            try:
                req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
                res = urllib.request.urlopen(req, timeout=3)
                risk = "CRITICAL!" if d in [".git", ".env", "backup", "config", "db", "private", "secret"] else "Check karo"
                found.append({"path": f"/{d}", "status": res.status, "risk": risk})
            except Exception as ex:
                code = str(ex)
                if "403" in code:
                    found.append({"path": f"/{d}", "status": 403, "risk": "Exists but blocked"})
        return {"domain": domain, "found": found, "total_found": len(found), "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/passcheck")
def password_check(password: str, key: str = Depends(verify_key)):
    start = time.time()
    score = 0
    feedback = []
    length = len(password)
    if length >= 8: score += 1
    else: feedback.append("8+ characters chahiye")
    if length >= 12: score += 1
    else: feedback.append("12+ characters better hai")
    if any(c.isupper() for c in password): score += 1
    else: feedback.append("Uppercase letter add karo (A-Z)")
    if any(c.islower() for c in password): score += 1
    else: feedback.append("Lowercase letter add karo (a-z)")
    if any(c.isdigit() for c in password): score += 1
    else: feedback.append("Number add karo (0-9)")
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): score += 1
    else: feedback.append("Special character add karo (!@#$)")
    common = ["password", "123456", "admin", "qwerty", "abc123", "letmein", "monkey", "1234567890"]
    if password.lower() in common:
        score = 0
        feedback.append("Bahut common password hai!")
    levels = {0: "Bahut Weak", 1: "Weak", 2: "Medium", 3: "Fair", 4: "Strong", 5: "Very Strong", 6: "Excellent!"}
    return {"password_length": length, "score": f"{score}/6", "strength": levels.get(score, "Unknown"), "feedback": feedback, "response_time": f"{round(time.time()-start, 2)}s"}

@app.get("/hashcrack")
def hash_crack(hash_value: str, key: str = Depends(verify_key)):
    start = time.time()
    import hashlib
    common_passwords = ["password", "123456", "admin", "qwerty", "abc123", "letmein", "monkey", "1234", "test", "user", "root", "pass", "hello", "welcome", "login", "master", "dragon", "666666", "password1", "iloveyou", "sunshine", "princess", "football", "superman", "batman"]
    hash_len = len(hash_value)
    hash_type = "Unknown"
    if hash_len == 32: hash_type = "MD5"
    elif hash_len == 40: hash_type = "SHA1"
    elif hash_len == 64: hash_type = "SHA256"
    cracked = None
    for p in common_passwords:
        if hashlib.md5(p.encode()).hexdigest() == hash_value.lower():
            cracked = p
            hash_type = "MD5"
            break
        if hashlib.sha1(p.encode()).hexdigest() == hash_value.lower():
            cracked = p
            hash_type = "SHA1"
            break
        if hashlib.sha256(p.encode()).hexdigest() == hash_value.lower():
            cracked = p
            hash_type = "SHA256"
            break
    return {"hash": hash_value, "hash_type": hash_type, "cracked": cracked, "result": f"PASSWORD MILA: {cracked}" if cracked else "Nahi mila — strong password hai!", "response_time": f"{round(time.time()-start, 2)}s"}

@app.get("/iprep")
def ip_reputation(ip: str, key: str = Depends(verify_key)):
    start = time.time()
    try:
        try:
            resolved_ip = socket.gethostbyname(ip)
        except:
            resolved_ip = ip
        suspicious = False
        reasons = []
        private_ranges = [("10.", "Private network"), ("192.168.", "Private network"), ("172.16.", "Private network"), ("127.", "Localhost")]
        for range_start, reason in private_ranges:
            if resolved_ip.startswith(range_start):
                suspicious = True
                reasons.append(reason)
        try:
            hostname = socket.gethostbyaddr(resolved_ip)[0]
        except:
            hostname = "Not found"
            reasons.append("No reverse DNS")
        return {"ip": resolved_ip, "hostname": hostname, "suspicious": suspicious, "reasons": reasons if reasons else ["Clean - koi known issue nahi"], "verdict": "Suspicious" if suspicious else "Clean", "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/apiscan")
def api_security_test(url: str, key: str = Depends(verify_key)):
    start = time.time()
    if not url.startswith("http"):
        url = "https://" + url
    endpoints = ["/api", "/api/v1", "/api/v2", "/api/users", "/api/admin", "/api/login", "/api/token", "/api/keys", "/graphql", "/swagger", "/swagger-ui.html", "/api-docs"]
    found = []
    try:
        for ep in endpoints:
            test_url = url.rstrip("/") + ep
            try:
                req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
                res = urllib.request.urlopen(req, timeout=3)
                risk = "CRITICAL!" if any(x in ep for x in ["admin", "keys", "token"]) else "Check karo"
                found.append({"endpoint": ep, "status": res.status, "risk": risk})
            except Exception as ex:
                code = str(ex)
                if "403" in code:
                    found.append({"endpoint": ep, "status": 403, "risk": "Exists but blocked"})
        return {"url": url, "found_endpoints": found, "total_found": len(found), "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/jwtcheck")
def jwt_check(token: str, key: str = Depends(verify_key)):
    start = time.time()
    import base64
    import json
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {"valid_format": False, "error": "Valid JWT nahi hai - 3 parts chahiye"}
        def decode_part(p):
            p += "=" * (4 - len(p) % 4)
            return json.loads(base64.urlsafe_b64decode(p).decode("utf-8", errors="ignore"))
        header = decode_part(parts[0])
        payload = decode_part(parts[1])
        issues = []
        if header.get("alg", "").upper() == "NONE":
            issues.append("CRITICAL: Algorithm none hai - authentication bypass possible!")
        if header.get("alg", "").upper() == "HS256":
            issues.append("WARNING: HS256 weak ho sakta hai - brute force possible")
        if "exp" not in payload:
            issues.append("WARNING: Expiry nahi hai - token kabhi expire nahi hoga!")
        import time as t
        if "exp" in payload and payload["exp"] < t.time():
            issues.append("CRITICAL: Token already expired hai!")
        return {"valid_format": True, "header": header, "payload": payload, "issues": issues, "verdict": "VULNERABLE!" if any("CRITICAL" in i for i in issues) else "OK", "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/ratelimit")
def rate_limit_test(url: str, key: str = Depends(verify_key)):
    start = time.time()
    if not url.startswith("http"):
        url = "https://" + url
    responses = []
    try:
        for i in range(10):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                res = urllib.request.urlopen(req, timeout=5)
                responses.append(res.status)
            except Exception as ex:
                code = str(ex)
                if "429" in code:
                    responses.append(429)
                else:
                    responses.append(0)
        blocked = responses.count(429)
        success = responses.count(200)
        return {"url": url, "total_requests": 10, "successful": success, "blocked_429": blocked, "verdict": "Rate limiting hai!" if blocked > 0 else "Rate limiting NAHI hai - vulnerable!", "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/redirecttest")
def open_redirect_test(url: str, key: str = Depends(verify_key)):
    start = time.time()
    if not url.startswith("http"):
        url = "https://" + url
    payloads = ["?redirect=https://evil.com", "?url=https://evil.com", "?next=https://evil.com", "?return=https://evil.com", "?goto=https://evil.com"]
    results = []
    try:
        for payload in payloads:
            test_url = url + payload
            try:
                req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
                res = urllib.request.urlopen(req, timeout=5)
                final_url = res.geturl()
                if "evil.com" in final_url:
                    results.append({"payload": payload, "status": "VULNERABLE! Open Redirect mila!"})
                else:
                    results.append({"payload": payload, "status": "Safe"})
            except:
                results.append({"payload": payload, "status": "Could not test"})
        vulnerable = [r for r in results if "VULNERABLE" in r["status"]]
        return {"url": url, "results": results, "verdict": "VULNERABLE!" if vulnerable else "Safe", "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/corscheck")
def cors_check(url: str, key: str = Depends(verify_key)):
    start = time.time()
    if not url.startswith("http"):
        url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Origin": "https://evil.com"})
        res = urllib.request.urlopen(req, timeout=10)
        headers = dict(res.headers)
        acao = headers.get("Access-Control-Allow-Origin", "Not set")
        acac = headers.get("Access-Control-Allow-Credentials", "Not set")
        issues = []
        if acao == "*":
            issues.append("WARNING: Wildcard CORS - sab origins allow hain!")
        if acao == "https://evil.com":
            issues.append("CRITICAL: Evil origin reflect ho raha hai!")
        if acac == "true" and acao == "*":
            issues.append("CRITICAL: Credentials + wildcard = data theft possible!")
        return {"url": url, "allow_origin": acao, "allow_credentials": acac, "issues": issues, "verdict": "VULNERABLE!" if any("CRITICAL" in i for i in issues) else "OK", "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/cookiecheck")
def cookie_check(url: str, key: str = Depends(verify_key)):
    start = time.time()
    if not url.startswith("http"):
        url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        res = urllib.request.urlopen(req, timeout=10)
        headers = dict(res.headers)
        cookie_header = headers.get("Set-Cookie", "")
        issues = []
        good = []
        if not cookie_header:
            return {"url": url, "cookies_found": False, "message": "Koi cookie set nahi ho rahi"}
        if "httponly" not in cookie_header.lower():
            issues.append("HttpOnly missing - JavaScript se cookie steal possible!")
        else:
            good.append("HttpOnly present")
        if "secure" not in cookie_header.lower():
            issues.append("Secure flag missing - HTTP pe bhi cookie jayegi!")
        else:
            good.append("Secure flag present")
        if "samesite" not in cookie_header.lower():
            issues.append("SameSite missing - CSRF attack possible!")
        else:
            good.append("SameSite present")
        return {"url": url, "cookies_found": True, "issues": issues, "good_practices": good, "verdict": "VULNERABLE!" if issues else "Secure!", "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/clickjack")
def clickjacking_test(url: str, key: str = Depends(verify_key)):
    start = time.time()
    if not url.startswith("http"):
        url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        res = urllib.request.urlopen(req, timeout=10)
        headers = dict(res.headers)
        xfo = headers.get("X-Frame-Options", "")
        csp = headers.get("Content-Security-Policy", "")
        if xfo.upper() in ["DENY", "SAMEORIGIN"]:
            verdict = "Safe - X-Frame-Options set hai"
        elif "frame-ancestors" in csp.lower():
            verdict = "Safe - CSP frame-ancestors set hai"
        else:
            verdict = "VULNERABLE! Site iframe mein load ho sakti hai - Clickjacking possible!"
        return {"url": url, "x_frame_options": xfo or "Not set", "csp_frame": "Set" if "frame-ancestors" in csp.lower() else "Not set", "verdict": verdict, "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/sensitivefiles")
def sensitive_files(domain: str, key: str = Depends(verify_key)):
    start = time.time()
    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
    files = [".env", ".git/config", ".git/HEAD", "config.php", "wp-config.php", "database.yml", "settings.py", "config.js", "credentials.json", "backup.sql", "dump.sql", "db.sql", ".htpasswd", "composer.json", "package.json", "Dockerfile", "docker-compose.yml", ".ssh/id_rsa"]
    found = []
    try:
        for f in files:
            test_url = f"https://{domain}/{f}"
            try:
                req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
                res = urllib.request.urlopen(req, timeout=3)
                found.append({"file": f, "status": res.status, "risk": "CRITICAL! File exposed hai!"})
            except Exception as ex:
                if "403" in str(ex):
                    found.append({"file": f, "status": 403, "risk": "Exists but blocked"})
        return {"domain": domain, "exposed_files": found, "total_exposed": len(found), "verdict": "CRITICAL!" if any(f["risk"] == "CRITICAL! File exposed hai!" for f in found) else "Safe", "response_time": f"{round(time.time()-start, 2)}s"}
    except Exception as e:
        return {"error": str(e)}

import os, base64, requests

code = open("api.py", encoding="utf-8").read()

# Fix 1: Global imports
code = code.replace(
    "import requests\nimport base64\nimport sys\nimport os\nimport time",
    "import requests\nimport base64\nimport sys\nimport os\nimport time\nimport socket\nimport ssl\nimport urllib.request\nimport urllib.parse"
)

# Fix 2: genai configure
code = code.replace(
    'try:\n    from google import genai\n    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))\nexcept:\n    genai = None',
    'try:\n    from google import genai\nexcept:\n    genai = None'
)

# Fix 3: /create - code variable empty tha
code = code.replace(
    '        test_result = run_code(code)\n        if test_result["success"]:\n            save_memory(task, code, True)\n            break\n        else:\n            save_memory(task, code, False, test_result.get(\'error\', \'\'))\n    push_to_github(filename, code)',
    '        code = code_to_run\n        test_result = run_code(code_to_run)\n        if test_result["success"]:\n            save_memory(task, code_to_run, True)\n            break\n        else:\n            save_memory(task, code_to_run, False, test_result.get(\'error\', \'\'))\n    push_to_github(filename, code)'
)

# Fix 4: /analyze - code_to_run undefined
code = code.replace(
    '        test_result = run_code(code_to_run)\n        if test_result["success"]:\n            return {"status": "success", "attempts": attempts',
    '        test_result = run_code(code)\n        if test_result["success"]:\n            return {"status": "success", "attempts": attempts'
)

# Fix 5: Duplicate function name
code = code.replace(
    '@app.get("/aggressive")\ndef aggressive_attack(domain: str, key: str = Depends(verify_key)):\n    start = time.time()\n    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]\n    url = "https://" + domain\n    results = {"domain": domain, "critical": [], "data_found": [], "bypassed": []}',
    '@app.get("/aggressive")\ndef aggressive_scan(domain: str, key: str = Depends(verify_key)):\n    start = time.time()\n    domain = domain.replace("https://", "").replace("http://", "").split("/")[0]\n    url = "https://" + domain\n    results = {"domain": domain, "critical": [], "data_found": [], "bypassed": []}'
)

open("api.py", "w", encoding="utf-8").write(code)
print("Fixes done!")

# Syntax check
import subprocess, tempfile
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
tmp.write(code)
tmp.close()
result = subprocess.run(["python", "-m", "py_compile", tmp.name], capture_output=True, text=True)
os.unlink(tmp.name)
if result.returncode != 0:
    print("SYNTAX ERROR:", result.stderr)
    exit(1)
print("Syntax OK!")

# GitHub push
from dotenv import load_dotenv
load_dotenv()
token = os.getenv("GITHUB_TOKEN")
repo = os.getenv("GITHUB_REPO")
url = f"https://api.github.com/repos/{repo}/contents/api.py"
headers = {"Authorization": f"token {token}"}
get_resp = requests.get(url, headers=headers, timeout=10)
sha = get_resp.json().get("sha", "")
encoded = base64.b64encode(code.encode()).decode()
push = requests.put(url, headers=headers, json={
    "message": "fix: global imports, create bug, analyze bug, duplicate function",
    "content": encoded,
    "sha": sha
}, timeout=15)

if push.status_code in [200, 201]:
    print("GitHub push SUCCESS!")
else:
    print("Push FAILED:", push.status_code, push.text[:200])

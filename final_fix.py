import os, base64, requests, subprocess, tempfile
from dotenv import load_dotenv
load_dotenv()

code = open("api.py", encoding="utf-8").read()

# Fix 1: Duplicate imports hata do
code = code.replace(
    "import socket\nimport ssl\nimport urllib.request\nimport urllib.parse\nimport socket\nimport ssl\nimport urllib.request\nimport urllib.parse",
    "import socket\nimport ssl\nimport urllib.request\nimport urllib.parse"
)

# Fix 2: /create - code variable empty hai, code_to_run assign nahi ho raha
# save_memory aur push sab empty code se ho rahe the
code = code.replace(
    "        test_result = run_code(code_to_run)\n        if test_result[\"success\"]:\n            save_memory(task, code, True)\n            break\n        else:\n            save_memory(task, code, False, test_result.get('error', ''))\n    push_to_github(filename, code)\n    return {\"task\": task, \"filename\": filename, \"code\": code",
    "        code = code_to_run\n        test_result = run_code(code_to_run)\n        if test_result[\"success\"]:\n            save_memory(task, code_to_run, True)\n            break\n        else:\n            save_memory(task, code_to_run, False, test_result.get('error', ''))\n    push_to_github(filename, code)\n    return {\"task\": task, \"filename\": filename, \"code\": code"
)

# Fix 3: Commented out imports clean karo
code = code.replace("# import socket\n# import ssl\n# import json\n# import urllib.request\n\n", "")
code = code.replace("# import socket\n# import ssl\n# import urllib.request\n# import datetime\n\n", "")

open("api.py", "w", encoding="utf-8").write(code)
print("Fixes applied!")

# Syntax check
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
tmp.write(code)
tmp.close()
result = subprocess.run(["python", "-m", "py_compile", tmp.name], capture_output=True, text=True)
os.unlink(tmp.name)
if result.returncode != 0:
    print("SYNTAX ERROR:", result.stderr)
    exit(1)
print("Syntax OK!")

# GitHub push
token = os.getenv("GITHUB_TOKEN")
repo = os.getenv("GITHUB_REPO")
url = f"https://api.github.com/repos/{repo}/contents/api.py"
headers = {"Authorization": f"token {token}"}
get_resp = requests.get(url, headers=headers, timeout=10)
sha = get_resp.json().get("sha", "")
encoded = base64.b64encode(code.encode()).decode()
push = requests.put(url, headers=headers, json={
    "message": "fix: duplicate imports, /create empty code bug, cleanup",
    "content": encoded,
    "sha": sha
}, timeout=15)

if push.status_code in [200, 201]:
    print("GitHub push SUCCESS! Render pe deploy ho jayega.")
else:
    print("Push FAILED:", push.status_code, push.text[:300])

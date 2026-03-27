with open('api.py', 'r', encoding='utf-8') as f:
    code = f.read()
fixes = 0

# BUG 1: genai.configure hata do + bare except fix
old1 = 'try:\n    from google import genai\n    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))\nexcept:\n    genai = None'
new1 = 'try:\n    from google import genai\nexcept Exception:\n    genai = None'
if old1 in code:
    code = code.replace(old1, new1)
    fixes += 1
    print("Fix 1 done: genai.configure removed")

# BUG 2: VALID_KEYS None protection
old2 = 'VALID_KEYS = {os.getenv("API_KEY_FREE"): "free", os.getenv("API_KEY_PRO"): "pro", os.getenv("API_KEY_BOSS"): "boss"}'
new2 = 'VALID_KEYS = {k: v for k, v in {os.getenv("API_KEY_FREE"): "free", os.getenv("API_KEY_PRO"): "pro", os.getenv("API_KEY_BOSS"): "boss"}.items() if k is not None}'
if old2 in code:
    code = code.replace(old2, new2)
    fixes += 1
    print("Fix 2 done: VALID_KEYS None protection added")

# BUG 3: /create code variable
old3 = '        test_result = run_code(code)\n        if test_result["success"]:\n            save_memory(task, code, True)\n            break\n        else:\n            save_memory(task, code, False'
new3 = '        code = code_to_run\n        test_result = run_code(code)\n        if test_result["success"]:\n            save_memory(task, code, True)\n            break\n        else:\n            save_memory(task, code, False'
if old3 in code:
    code = code.replace(old3, new3)
    fixes += 1
    print("Fix 3 done: /create code variable fixed")

# BUG 4: Duplicate aggressive_attack function rename
old4 = '@app.get("/aggressiveattack")\ndef aggressive_attack('
new4 = '@app.get("/aggressiveattack")\ndef aggressive_attack_v2('
if old4 in code:
    code = code.replace(old4, new4, 1)
    fixes += 1
    print("Fix 4 done: duplicate function renamed")

# BUG 5: Missing top-level imports - commented lines replace karo
old5 = '# import socket\n# import ssl\n# import json\n# import urllib.request'
new5 = 'import socket\nimport ssl\nimport json\nimport urllib.request'
if old5 in code:
    code = code.replace(old5, new5)
    fixes += 1
    print("Fix 5a done: socket/ssl imports uncommented")

old5b = '# import socket\n# import ssl\n# import urllib.request\n# import datetime'
new5b = 'import socket\nimport ssl\nimport urllib.request\nimport datetime'
if old5b in code:
    code = code.replace(old5b, new5b)
    fixes += 1
    print("Fix 5b done: second socket/ssl block uncommented")

with open('api.py', 'w', encoding='utf-8') as f:
    f.write(code)

print(f"\nTotal {fixes} fixes applied!")
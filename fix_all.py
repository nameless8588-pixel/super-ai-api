with open('api.py', 'r', encoding='utf-8') as f:
    code = f.read()

fixes = 0

# BUG 1: loginbypass - "BYPASSED" vs "Success" mismatch
old1 = 'bypassed = [r for r in results if "BYPASSED" in r["status"]]'
new1 = 'bypassed = [r for r in results if r.get("status") == "Success"]'
if old1 in code:
    code = code.replace(old1, new1)
    fixes += 1
    print("Fix 1 done: loginbypass bypassed filter fixed")

# BUG 2: bare except -> except Exception
old2 = 'try:\n    from google import genai\nexcept:\n    genai = None'
new2 = 'try:\n    from google import genai\nexcept Exception:\n    genai = None'
if old2 in code:
    code = code.replace(old2, new2)
    fixes += 1
    print("Fix 2 done: genai bare except fixed")

# BUG 3: async selfupgrade -> sync
old3 = 'async def selfupgrade('
new3 = 'def selfupgrade('
if old3 in code:
    code = code.replace(old3, new3)
    fixes += 1
    print("Fix 3 done: selfupgrade async removed")

# BUG 4: chat_history TTLCache
old4 = 'chat_history = {}'
new4 = 'from cachetools import TTLCache\nchat_history = TTLCache(maxsize=500, ttl=3600)'
if old4 in code:
    code = code.replace(old4, new4)
    fixes += 1
    print("Fix 4 done: chat_history TTLCache added")

with open('api.py', 'w', encoding='utf-8') as f:
    f.write(code)

print(f"\nTotal {fixes}/4 fixes applied!")
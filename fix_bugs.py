with open('api.py', 'r', encoding='utf-8') as f:
    code = f.read()

fixes = 0

# FIX 1: Duplicate function
old = '@app.get("/aggressiveattack")\ndef aggressive_attack('
new = '@app.get("/aggressiveattack")\ndef aggressive_attack_v2('
if old in code:
    code = code.replace(old, new, 1)
    fixes += 1
    print("Fix 1 done: duplicate function renamed")

# FIX 2: VALID_KEYS None protection
old2 = 'VALID_KEYS = {os.getenv("API_KEY_FREE"): "free", os.getenv("API_KEY_PRO"): "pro", os.getenv("API_KEY_BOSS"): "boss"}'
new2 = 'VALID_KEYS = {k: v for k, v in {os.getenv("API_KEY_FREE"): "free", os.getenv("API_KEY_PRO"): "pro", os.getenv("API_KEY_BOSS"): "boss"}.items() if k is not None}'
if old2 in code:
    code = code.replace(old2, new2)
    fixes += 1
    print("Fix 2 done: VALID_KEYS None protection")

# FIX 3: genai.configure hata do
old3 = '    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))\n'
if old3 in code:
    code = code.replace(old3, '')
    fixes += 1
    print("Fix 3 done: genai.configure removed")

# FIX 4: create endpoint code variable
old4 = '        test_result = run_code(code_to_run)\n        if test_result["success"]:\n            save_memory(task, code_to_run, True)'
new4 = '        test_result = run_code(code)\n        if test_result["success"]:\n            save_memory(task, code, True)'
if old4 in code:
    code = code.replace(old4, new4)
    fixes += 1
    print("Fix 4 done: create code variable fixed")

with open('api.py', 'w', encoding='utf-8') as f:
    f.write(code)

print(f"Total {fixes} fixes applied!")

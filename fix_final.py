with open('api.py', 'r', encoding='utf-8') as f:
    code = f.read()

fixes = 0

# FIX 1: Duplicate imports hata do
old1 = '\nimport socket\nimport ssl\nimport urllib.request\nimport datetime\n'
new1 = '\nimport datetime\n'
if old1 in code:
    code = code.replace(old1, new1)
    fixes += 1
    print("Fix 1 done: duplicate imports removed")

# FIX 2: /debug endpoint add karo agar missing hai
if '"/debug"' not in code:
    debug_code = '''
@app.get("/debug")
def debug_check(key: str = Depends(verify_key)):
    import os
    return {
        "groq_key": bool(os.getenv("GROQ_API_KEY")),
        "github_token": bool(os.getenv("GITHUB_TOKEN")),
        "executor_exists": os.path.exists("tools/executor.py"),
        "internet_exists": os.path.exists("tools/internet.py"),
        "memory_exists": os.path.exists("tools/memory.py"),
        "db_exists": os.path.exists("ai_memory.db"),
    }
'''
    code = code.replace('if __name__ == "__main__":', debug_code + '\nif __name__ == "__main__":')
    fixes += 1
    print("Fix 2 done: /debug endpoint added back")

with open('api.py', 'w', encoding='utf-8') as f:
    f.write(code)

print(f"Total {fixes}/2 fixes applied!")

with open('api.py', 'r', encoding='utf-8') as f:
    code = f.read()

fixes = 0

# FIX 1: Duplicate TTLCache import hata do
duplicate = '\nfrom cachetools import TTLCache\nchat_history = TTLCache(maxsize=500, ttl=3600)'
correct   = '\nchat_history = TTLCache(maxsize=500, ttl=3600)'
if duplicate in code:
    code = code.replace(duplicate, correct)
    fixes += 1
    print("Fix 1 done: duplicate TTLCache import removed")

# FIX 2: rollback async -> sync
old2 = 'async def rollback('
new2 = 'def rollback('
if old2 in code:
    code = code.replace(old2, new2)
    fixes += 1
    print("Fix 2 done: rollback async removed")

with open('api.py', 'w', encoding='utf-8') as f:
    f.write(code)

print(f"Total {fixes}/2 fixes applied!")

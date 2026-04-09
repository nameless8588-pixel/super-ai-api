content = open('api.py', encoding='utf-8').read()
idx = content.find('uvicorn')
print(content[idx:idx+200])

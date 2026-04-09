req = open('requirements.txt').read()

add_these = [
    "langchain",
    "langchain-groq", 
    "langchain-openai",
    "openai-whisper",
    "pillow",
    "opencv-python-headless",
    "pandas",
    "matplotlib",
    "elevenlabs",
    "pytesseract",
    "numpy"
]

new_libs = []
for lib in add_these:
    base = lib.split("[")[0].split("==")[0].lower()
    if base not in req.lower():
        new_libs.append(lib)
        print(f"➕ Adding: {lib}")
    else:
        print(f"✅ Already exists: {lib}")

if new_libs:
    with open('requirements.txt', 'a') as f:
        f.write('\n' + '\n'.join(new_libs))
    print("\n✅ requirements.txt updated!")
else:
    print("\n✅ Sab already installed hai!")

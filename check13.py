for f in ['tools/ai_router.py', 'tools/internet.py', 'tools/memory.py']:
    print(f"\n{'='*50}")
    print(f"FILE: {f}")
    print('='*50)
    try:
        print(open(f).read()[:500])
    except:
        print("Read nahi hua")

content = open('api.py').read()
if 'slowapi' in content or 'limiter' in content:
    print("HAN - use ho raha hai")
    idx = content.find('limiter')
    print(content[idx:idx+200])
else:
    print("NAHI - use nahi ho raha")

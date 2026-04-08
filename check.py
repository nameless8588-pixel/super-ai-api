content = open('frontend.html', encoding='utf-8').read()
idx = content.find('async function handleCommand')
if idx != -1:
    print("FOUND at index:", idx)
    print(repr(content[idx:idx+300]))
else:
    print("handleCommand function hi nahi mila!")

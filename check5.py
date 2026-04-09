content = open('frontend.html', encoding='utf-8').read()
idx = content.find('async function handleCommand')
print(repr(content[idx:idx+1500]))

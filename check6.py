content = open('frontend.html', encoding='utf-8').read()
idx = content.find('commandMode = true')
print(repr(content[idx:idx+500]))

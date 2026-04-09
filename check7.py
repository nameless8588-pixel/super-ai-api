content = open('frontend.html', encoding='utf-8').read()
idx = content.find('const transcript')
print(repr(content[idx:idx+600]))

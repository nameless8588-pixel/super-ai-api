content = open('frontend.html', encoding='utf-8').read()
idx = content.find('recognition.onend')
print(repr(content[idx:idx+200]))

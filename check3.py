content = open('frontend.html', encoding='utf-8').read()
idx = content.find('startRecognition')
print(repr(content[idx:idx+2000]))

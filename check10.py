import os
# requirements.txt dekho
if os.path.exists('requirements.txt'):
    print(open('requirements.txt').read())
else:
    print("requirements.txt nahi mila!")

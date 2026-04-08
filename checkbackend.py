import os
for f in os.listdir('.'):
    if f.endswith('.py'):
        print(f)

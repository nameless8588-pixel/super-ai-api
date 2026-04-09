import os
tools_path = 'tools'
if os.path.exists(tools_path):
    for f in os.listdir(tools_path):
        print(f)
else:
    print("tools folder nahi mila")

import requests, os, base64
token = open('.env').read()
# GitHub se requirements.txt fetch karo
import subprocess
result = subprocess.run(['git', 'show', 'origin/main:requirements.txt'], capture_output=True, text=True)
print(result.stdout)

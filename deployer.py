import os
import requests
import base64

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_REPO = os.getenv("GITHUB_REPO")

def push_file(filename, content):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{filename}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    check = requests.get(url, headers=headers)
    data = {"message": f"AI ne banaya: {filename}", "content": base64.b64encode(content.encode()).decode()}
    if check.status_code == 200:
        data["sha"] = check.json()["sha"]
    requests.put(url, json=data, headers=headers)

def add_app_to_index(filename, emoji, title):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/index.html"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return
    content = base64.b64decode(r.json()["content"]).decode()
    if filename in content:
        return
    new_link = f'        <p><a href="apps/{filename}">{emoji} {title}</a></p>\n    <!-- END_APPS -->'
    content = content.replace('    <!-- END_APPS -->', new_link)
    data = {"message": f"Index update: {filename}", "content": base64.b64encode(content.encode()).decode(), "sha": r.json()["sha"]}
    requests.put(url, json=data, headers=headers)

def save_and_deploy(filename, code, emoji="rocket", title=None):
    if title is None:
        title = filename.replace('.html', '').replace('_', ' ').title()
    push_file(f"apps/{filename}", code)
    add_app_to_index(filename, emoji, title)
    return f"https://{GITHUB_USERNAME}.github.io/{GITHUB_REPO}/apps/{filename}"

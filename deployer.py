import os
import sys
import subprocess

base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_path, 'tools'))

def add_app_to_index(filename, emoji, title):
    index_path = os.path.join(base_path, 'index.html')
    with open(index_path, 'r') as f:
        content = f.read()
    if filename in content:
        return
    new_link = f'        <p><a href="apps/{filename}">{emoji} {title}</a></p>\n    <!-- END_APPS -->'
    content = content.replace('    <!-- END_APPS -->', new_link)
    with open(index_path, 'w') as f:
        f.write(content)

def save_and_deploy(filename, code, emoji="íº€", title=None):
    if title is None:
        title = filename.replace('.html', '').replace('_', ' ').title()
    app_path = os.path.join(base_path, 'apps', filename)
    os.makedirs(os.path.dirname(app_path), exist_ok=True)
    with open(app_path, 'w') as f:
        f.write(code)
    add_app_to_index(filename, emoji, title)
    os.chdir(base_path)
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', f'AI ne banaya: apps/{filename}'])
    subprocess.run(['git', 'push', '--force'])
    return f"https://{os.getenv('GITHUB_USERNAME')}.github.io/{os.getenv('GITHUB_REPO')}/apps/{filename}"

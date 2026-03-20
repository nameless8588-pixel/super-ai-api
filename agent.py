import os
import sys
import subprocess

base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(base_path, 'tools'))

def add_app_to_index(filename, emoji, title):
    index_path = os.path.join(base_path, 'index.html')
    
    with open(index_path, 'r') as f:
        content = f.read()
    
    # Check karo pehle se hai ya nahi
    if filename in content:
        print(f"⚠️ {filename} pehle se index mein hai!")
        return
    
    new_link = f'        <p><a href="apps/{filename}">{emoji} {title}</a></p>\n        <!-- END_APPS -->'
    content = content.replace('        <!-- END_APPS -->', new_link)
    
    with open(index_path, 'w') as f:
        f.write(content)
    
    print(f"✅ {title} index.html mein add ho gaya!")

def save_and_deploy(filename, code, emoji="🚀", title=None):
    if title is None:
        title = filename.replace('.html', '').replace('_', ' ').title()
    
    # File save karo
    app_path = os.path.join(base_path, 'apps', filename)
    with open(app_path, 'w') as f:
        f.write(code)
    print(f"✅ {filename} save ho gaya!")
    
    # Index update karo
    add_app_to_index(filename, emoji, title)
    
    # GitHub pe push karo
    os.chdir(base_path)
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', f'AI ne banaya: apps/{filename}'])
    subprocess.run(['git', 'push', '--force'])
    
    link = f"https://nameless8588-pixel.github.io/super-ai-api/apps/{filename}"
    print(f"\n🌍 LIVE LINK: {link}")
    return link

if __name__ == "__main__":
    print("Agent ready hai bhai! 🚀")
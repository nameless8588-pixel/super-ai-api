import json
import os

memory_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'memory.json')

def save_memory(task, code, success, error=""):
    memories = load_all()
    memories.append({
        "task": task,
        "code": code,
        "success": success,
        "error": error
    })
    with open(memory_file, 'w') as f:
        json.dump(memories, f, indent=2)

def load_all():
    if not os.path.exists(memory_file):
        return []
    with open(memory_file, 'r') as f:
        return json.load(f)

def get_similar(task, limit=3):
    memories = load_all()
    relevant = []
    for m in memories:
        if any(word in m['task'].lower() for word in task.lower().split()):
            relevant.append(m)
    return relevant[-limit:]

def get_mistakes():
    memories = load_all()
    return [m for m in memories if not m['success']][-5:]

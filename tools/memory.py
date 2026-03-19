import chromadb
import os

# Memory database setup
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
client = chromadb.PersistentClient(path=os.path.join(base_path, 'memory_db'))
collection = client.get_or_create_collection("ai_memory")

def save_memory(user_input, ai_response):
    """Conversation yaad rakho"""
    import time
    memory_id = str(int(time.time()))
    collection.add(
        documents=[f"User: {user_input}\nAI: {ai_response}"],
        ids=[memory_id]
    )
    print(f"✅ Memory saved!")

def get_memory(query, n=3):
    """Related memories dhundo"""
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n
        )
        if results['documents'][0]:
            return "\n".join(results['documents'][0])
    except:
        pass
    return ""

def clear_memory():
    """Sari memory delete karo"""
    collection.delete(where={"id": {"$ne": ""}})
    print("🗑️ Memory cleared!")
import sys
import os
import ollama
import pyttsx3

# --- Path Setup ---
base_path = os.path.dirname(os.path.abspath(__file__))
tools_path = os.path.join(base_path, 'tools')
sys.path.insert(0, tools_path)

# --- Voice Setup ---
engine = pyttsx3.init()
def speak(text):
    print(f"\nAI: {text}")
    engine.say(text)
    engine.runAndWait()

# --- Internet Tool ---
try:
    from internet import search_internet
    print("✅ Internet Active!")
except Exception as e:
    def search_internet(q): return "Search error."

# --- Memory Tool ---
try:
    from memory import save_memory, get_memory
    print("✅ Memory Active!")
except Exception as e:
    print(f"❌ Memory Error: {e}")
    def save_memory(u, a): pass
    def get_memory(q): return ""

# --- AI Setup ---
messages = [
    {'role': 'user', 'content': "Tu ek smart Indian dost hai. Hinglish mein short jawab de."},
    {'role': 'assistant', 'content': "Haan bhai, bol kya scene hai!"}
]

print("\n--- 🚀 World Wide Launch Active ---")

while True:
    user_input = input("\nAapka Sawal: ")
    if user_input.lower() in ['exit', 'bye']:
        speak("Chal bhai, phir milte hain!")
        break

    # Memory se related baatein dhundo
    past_memory = get_memory(user_input)
    memory_context = f"\nPast Memory:\n{past_memory}" if past_memory else ""

    # Internet check
    try:
        check = ollama.chat(model='gemma3:1b', messages=[
            {'role': 'user', 'content': f"Is '{user_input}' a greeting? If yes say NO. Need internet? YES/NO only"}
        ])
        context = ""
        if "YES" in check['message']['content'].upper():
            print("...Ruk bhai, net pe check kar raha hoon...")
            context = f"\nInternet Data: {search_internet(user_input)}"
    except:
        context = ""

    # Final jawab
    try:
        messages.append({'role': 'user', 'content': f"{user_input}{memory_context}{context}"})
        response = ollama.chat(model='gemma3:1b', messages=messages)
        reply = response['message']['content']
        messages.append({'role': 'assistant', 'content': reply})

        # Memory mein save karo
        save_memory(user_input, reply)
        
        speak(reply)
    except Exception as e:
        print(f"❌ Error: {e}")
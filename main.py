import sys
import os
import ollama
import pyttsx3

# --- Voice Setup ---
engine = pyttsx3.init()
def speak(text):
    print(f"\nAI: {text}")
    engine.say(text)
    engine.runAndWait()

# --- Path Setup ---
base_path = os.path.dirname(os.path.abspath(__file__))
tools_path = os.path.join(base_path, 'tools')
sys.path.insert(0, tools_path)

# --- Internet Tool ---
try:
    from internet import search_internet
    print("✅ Internet & Voice Active!")
except Exception as e:
    print(f"❌ Error: {e}")
    def search_internet(q): return "Search error."

# --- AI Setup ---
messages = [
    {'role': 'user', 'content': """Tu ek smart Indian dost hai.
1. Agar niche 'Internet Data' diya gaya hai, toh sirf usi ka use karke jawab dena.
2. Faltu ka gyaan mat dena.
3. Hinglish mein short aur seedha jawab dena."""},
    {'role': 'assistant', 'content': "Haan bhai, samajh gaya! Bol kya scene hai!"}
]

print("\n--- 🚀 World Wide Launch Active ---")

while True:
    user_input = input("\nAapka Sawal: ")
    if user_input.lower() in ['exit', 'bye']:
        speak("Chal bhai, phir milte hain!")
        break

    # Internet check
    try:
        check = ollama.chat(model='gemma3:4b', messages=[{'role': 'user', 'content': f"Does '{user_input}' need internet search? YES/NO only"}])
        context = ""
        if "YES" in check['message']['content'].upper():
            print("...Ruk bhai, net pe check kar raha hoon...")
            context = f"\nInternet Data: {search_internet(user_input)}"
    except:
        context = ""

    # Final jawab
    try:
        messages.append({'role': 'user', 'content': f"{user_input} {context}"})
        response = ollama.chat(model='gemma3:4b', messages=messages)
        reply = response['message']['content']
        messages.append({'role': 'assistant', 'content': reply})
        speak(reply)
    except Exception as e:
        print(f"❌ Error: {e}")
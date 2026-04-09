import os
from groq import Groq

def get_ai_response(prompt, system="", tools_context=""):
    """Smart AI router with tool awareness"""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # System prompt with all capabilities
    smart_system = """Tu CODELESS AI hai - ek powerful assistant.

TERI CAPABILITIES:
1. SECURITY: SSL check, port scan, XSS, SQL injection, full audit
2. SYSTEM: PC info, running processes, disk/RAM/CPU
3. CODE: Python code likhna, execute karna, fix karna  
4. WEB: Search, scraping, website analysis
5. CHAT: General conversation, questions, help

RULES:
- Agar koi domain/URL mention ho → security scan suggest karo
- Agar system info manga ho → agent tool use karo
- Agar code banana ho → /create endpoint use karo
- Hamesha Hinglish mein jawab do
- Short aur helpful raho
- Kabhi mat kaho "main nahi kar sakta"

""" + (system or "") + (f"\nExtra context: {tools_context}" if tools_context else "")

    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": smart_system},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        return r.choices[0].message.content
    except Exception as e1:
        # Fallback to Gemini
        try:
            from google import genai
            gc = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            r = gc.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=smart_system + "\n" + prompt
            )
            return r.text
        except Exception as e2:
            # Fallback to OpenRouter
            try:
                import requests
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"},
                    json={
                        "model": "meta-llama/llama-3.3-70b",
                        "messages": [
                            {"role": "system", "content": smart_system},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1000
                    },
                    timeout=20
                )
                return r.json()["choices"][0]["message"]["content"]
            except:
                return "Sab AI providers down hain, baad mein try karo."


def analyze_image(image_path):
    """Image analysis using AI"""
    try:
        import base64
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        with open(image_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        r = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}},
                    {"type": "text", "text": "Is image mein kya hai? Hinglish mein batao."}
                ]
            }],
            max_tokens=500
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Image analysis failed: {str(e)}"


def analyze_data(data, question):
    """Pandas data analysis"""
    try:
        import pandas as pd
        import io
        # CSV string se DataFrame
        df = pd.read_csv(io.StringIO(data))
        stats = df.describe().to_string()
        prompt = f"Data statistics:\n{stats}\n\nSawal: {question}\nHinglish mein analysis do."
        return get_ai_response(prompt)
    except Exception as e:
        return f"Data analysis failed: {str(e)}"


def transcribe_audio(audio_path):
    """Whisper se audio transcribe karo"""
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        with open(audio_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=f,
                language="hi"
            )
        return transcription.text
    except Exception as e:
        return f"Transcription failed: {str(e)}"

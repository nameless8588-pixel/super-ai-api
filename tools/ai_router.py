
def get_ai_response(prompt):
    try:
        from groq import Groq
        import os
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        r = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], max_tokens=1000)
        return r.choices[0].message.content
    except:
        pass
    try:
        import google.generativeai as genai, os
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model.generate_content(prompt).text
    except:
        pass
    return "AI unavailable"

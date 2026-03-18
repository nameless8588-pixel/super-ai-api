from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_web_app(task: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": """Tu ek expert web developer hai. 
Ek single HTML file banao jisme CSS aur JS sab andar ho.
Sirf HTML code do — koi explanation nahi.
File seedha browser mein kaam kare."""},
            {"role": "user", "content": f"Yeh banao: {task}"}
        ]
    )
    code = response.choices[0].message.content
    code = code.replace("```html", "").replace("```", "").strip()
    return code

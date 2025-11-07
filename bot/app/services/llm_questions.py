from groq import Groq
import os
import json
import re

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_mcq_question():
    prompt = """Створи одне технічне питання по Python.

ВАЖЛИВО: Відповідай ТІЛЬКИ у форматі JSON, без жодного іншого тексту, без markdown, без пояснень.

Формат:
{"question": "текст питання українською", "options": ["A", "B", "C", "D"], "correct_index": 0}

Приклад:
{"question": "Що таке список у Python?", "options": ["Змінювана колекція", "Незмінювана колекція", "Функція", "Клас"], "correct_index": 0}"""

    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        text = r.choices[0].message.content.strip()
        
        text = text.replace("```json", "").replace("```", "").strip()
        
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if json_match:
            text = json_match.group()
        
        data = json.loads(text)
        
        if not all(k in data for k in ["question", "options", "correct_index"]):
            raise ValueError("Missing required fields")
            
        if len(data["options"]) != 4:
            raise ValueError("Need exactly 4 options")
        
        return data

    except Exception as e:
        print("LLM error:", e)
        print("Response text:", text if 'text' in locals() else "No response")
        
        import random
        fallbacks = [
            {
                "question": "Що таке Python?",
                "options": ["Мова програмування", "Тварина", "База даних", "ОС"],
                "correct_index": 0
            },
            {
                "question": "Що таке список у Python?",
                "options": ["Змінювана колекція", "Незмінювана колекція", "Функція", "Клас"],
                "correct_index": 0
            },
            {
                "question": "Яка функція виводить текст?",
                "options": ["print()", "input()", "len()", "type()"],
                "correct_index": 0
            },
            {
                "question": "Що таке dict у Python?",
                "options": ["Словник", "Список", "Кортеж", "Множина"],
                "correct_index": 0
            }
        ]
        return random.choice(fallbacks)
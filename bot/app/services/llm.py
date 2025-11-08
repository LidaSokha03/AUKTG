import os
from typing import Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

client = None
if API_KEY:
    client = OpenAI(api_key=API_KEY)


def generate_cv_text(user_data: Dict) -> str:
    if client is None:
        return f"""
Ім'я: {user_data.get("name")}
Позиція: {user_data.get("position")}
Навички: {", ".join(user_data.get('skills', []))}
Досвід: {user_data.get("experience")}
Проєкти: {user_data.get("projects")}
        """

    prompt = f"""
Створи коротке IT-CV на українській мові на основі даних:

Ім'я: {user_data.get("name")}
Позиція: {user_data.get("position")}
Навички: {", ".join(user_data.get('skills', []))}
Досвід: {user_data.get("experience")}
Проєкти: {user_data.get("projects")}

Формат:
- Короткий опис кандидата
- Навички списком
- Досвід одним абзацом
- Проєкти списком
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"""
Ім'я: {user_data.get("name")}
Позиція: {user_data.get("position")}
Навички: {", ".join(user_data.get('skills', []))}
Досвід: {user_data.get("experience")}
Проєкти: {user_data.get("projects")}

Помилка генерації: {str(e)}
        """
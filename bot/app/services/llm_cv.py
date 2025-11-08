from groq import Groq
import os
import json
import re


client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def improve_cv_with_llm(cv_dict: dict) -> dict:
    """
    Покращує CV за допомогою LLM (Groq)
    """
    prompt = f"""You are a professional CV writer and career coach. Improve the following CV content while keeping all factual information accurate.
Make it more professional, concise, impactful, and ATS-friendly.

Current CV:
Name: {cv_dict.get('firstname', '')} {cv_dict.get('lastname', '')}
Email: {cv_dict.get('email', '')}
Phone: {cv_dict.get('phone', '')}

Experience:
{cv_dict.get('experience', 'Not provided')}

Education:
{cv_dict.get('education', 'Not provided')}

Courses and Languages:
{cv_dict.get('courses', 'Not provided')}

Skills:
{cv_dict.get('skills', 'Not provided')}

Please provide an improved version in the following JSON format:
{{
    "experience": "improved experience text with action verbs and achievements",
    "education": "improved education text with relevant details",
    "courses": "improved courses and languages text",
    "skills": "improved skills text, organized by category if possible"
}}

Guidelines:
- Use strong action verbs (Led, Developed, Implemented, Achieved, etc.)
- Quantify achievements where possible
- Keep the same factual information but present it professionally
- Make it ATS-friendly
- Keep the language clear and concise
- Return ONLY the JSON object, no additional text

Return only valid JSON without markdown code blocks."""
    
    try:
        # Викликаємо Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional CV writer. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",  # Або інша модель Groq
            temperature=0.7,
            max_tokens=2048,
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Очищення відповіді від markdown
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'^```\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)
        response_text = response_text.strip()
        
        # Парсимо JSON
        improved_data = json.loads(response_text)
        
        # Перевіряємо, чи всі необхідні ключі присутні
        required_keys = ['experience', 'education', 'courses', 'skills']
        for key in required_keys:
            if key not in improved_data:
                improved_data[key] = cv_dict.get(key, '')
        
        # Створюємо покращене CV
        improved_cv = cv_dict.copy()
        improved_cv.update({
            'experience': improved_data.get('experience', cv_dict.get('experience', '')),
            'education': improved_data.get('education', cv_dict.get('education', '')),
            'courses': improved_data.get('courses', cv_dict.get('courses', '')),
            'skills': improved_data.get('skills', cv_dict.get('skills', ''))
        })
        
        return improved_cv
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Response was: {response_text}")
        return cv_dict
    except Exception as e:
        print(f"Error improving CV with LLM: {e}")
        return cv_dict


def generate_cv_summary(cv_dict: dict) -> str:
    """
    Генерує професійне резюме (summary) для CV
    """
    prompt = f"""Based on the following CV information, write a compelling professional summary (2-3 sentences) that highlights key strengths and career objectives.

Experience: {cv_dict.get('experience', 'Not provided')}
Education: {cv_dict.get('education', 'Not provided')}
Skills: {cv_dict.get('skills', 'Not provided')}

Write a professional summary that is:
- Concise (2-3 sentences)
- Highlights key strengths
- Shows career focus
- Uses strong professional language

Return ONLY the summary text, nothing else."""
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=200,
        )
        
        summary = chat_completion.choices[0].message.content.strip()
        # Видаляємо лапки на початку і в кінці, якщо є
        summary = summary.strip('"\'')
        
        return summary
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return ""


def enhance_section(section_name: str, content: str) -> str:
    """
    Покращує конкретну секцію CV
    
    Args:
        section_name: Назва секції (experience, education, skills, courses)
        content: Поточний вміст секції
    
    Returns:
        Покращений вміст
    """
    prompts = {
        'experience': """Rewrite this work experience section to be more impactful and professional.
Use strong action verbs, quantify achievements where possible, and make it ATS-friendly.""",
        
        'education': """Improve this education section to be clear, concise, and professional.
Include relevant details like honors, relevant coursework, or achievements.""",
        
        'skills': """Organize and improve this skills section.
Group by category if possible (e.g., Technical Skills, Languages, Soft Skills).
Make it easy to scan.""",
        
        'courses': """Improve this courses and certifications section.
List relevant courses, certifications, and language proficiencies clearly."""
    }
    
    instruction = prompts.get(section_name, "Improve this text to be more professional.")
    
    prompt = f"""{instruction}

Current content:
{content}

Return ONLY the improved text, no additional commentary."""
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1024,
        )
        
        improved = chat_completion.choices[0].message.content.strip()
        return improved if improved else content
        
    except Exception as e:
        print(f"Error enhancing section {section_name}: {e}")
        return content
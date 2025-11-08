from groq import Groq
import os
import json
import re
import random

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DIFFICULTY_PROMPTS = {
    "easy": "Create a basic, beginner-level question suitable for someone new to programming.",
    "medium": "Create an intermediate-level question for someone with some programming experience.",
    "hard": "Create an advanced, challenging question for experienced developers."
}

CATEGORY_PROMPTS = {
    "python": "about Python programming language (syntax, features, standard library)",
    "javascript": "about JavaScript programming language (ES6+, async/await, DOM, etc)",
    "algorithms": "about algorithms and data structures (complexity, sorting, searching, trees, graphs)",
    "databases": "about databases (SQL, NoSQL, indexing, transactions, normalization)",
    "system_design": "about system design and architecture (scalability, patterns, distributed systems)",
    "mixed": "about any programming topic (Python, JavaScript, algorithms, databases, or general CS concepts)"
}

FALLBACK_QUESTIONS = {
    "easy": [
        {
            "question": "What is Python?",
            "options": ["Programming language", "Animal", "Database", "Operating system"],
            "correct_index": 0
        },
        {
            "question": "Which function prints text in Python?",
            "options": ["print()", "input()", "len()", "type()"],
            "correct_index": 0
        },
        {
            "question": "What symbol starts a comment in Python?",
            "options": ["#", "//", "/*", "<!--"],
            "correct_index": 0
        }
    ],
    "medium": [
        {
            "question": "What is a list in Python?",
            "options": ["Mutable collection", "Immutable collection", "Function", "Class"],
            "correct_index": 0
        },
        {
            "question": "What does 'async' keyword do in JavaScript?",
            "options": ["Creates asynchronous function", "Imports module", "Defines class", "Creates loop"],
            "correct_index": 0
        },
        {
            "question": "What is Big O notation used for?",
            "options": ["Measuring algorithm complexity", "Defining classes", "Memory allocation", "Error handling"],
            "correct_index": 0
        }
    ],
    "hard": [
        {
            "question": "What is the time complexity of QuickSort in average case?",
            "options": ["O(n log n)", "O(n²)", "O(log n)", "O(n)"],
            "correct_index": 0
        },
        {
            "question": "What is a closure in JavaScript?",
            "options": ["Function with access to outer scope", "Loop termination", "Class constructor", "Error handler"],
            "correct_index": 0
        },
        {
            "question": "What is ACID in databases?",
            "options": ["Transaction properties", "Query language", "Index type", "Backup method"],
            "correct_index": 0
        }
    ]
}


def generate_mcq_question(category="mixed", difficulty="medium"):
    """
    Генерує MCQ питання з заданою категорією та складністю.
    
    Args:
        category: python, javascript, algorithms, databases, system_design, mixed
        difficulty: easy, medium, hard
    
    Returns:
        dict з question, options (4 варіанти), correct_index
    """
    
    # Валідація параметрів
    if category not in CATEGORY_PROMPTS:
        category = "mixed"
    if difficulty not in DIFFICULTY_PROMPTS:
        difficulty = "medium"
    
    difficulty_instruction = DIFFICULTY_PROMPTS[difficulty]
    category_instruction = CATEGORY_PROMPTS[category]
    
    prompt = f"""Create one technical programming question {category_instruction}.

{difficulty_instruction}

IMPORTANT: Respond ONLY in JSON format, without any other text, markdown, or explanations.

Requirements:
- Question must be clear and unambiguous
- All options must be plausible but only one correct
- Avoid trick questions or overly obscure topics
- Question should be in English

Format:
{{"question": "question text", "options": ["A", "B", "C", "D"], "correct_index": 0}}

Example:
{{"question": "What is a list in Python?", "options": ["Mutable collection", "Immutable collection", "Function", "Class"], "correct_index": 0}}"""
    
    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=500
        )
        
        text = r.choices[0].message.content.strip()
        
        # Видаляємо markdown форматування
        text = text.replace("```json", "").replace("```", "").strip()
        
        # Шукаємо JSON об'єкт в тексті
        json_match = re.search(r'\{[^}]+\}', text, re.DOTALL)
        if json_match:
            text = json_match.group()
        
        # Парсимо JSON
        data = json.loads(text)
        
        # Валідація структури
        if not all(k in data for k in ["question", "options", "correct_index"]):
            raise ValueError("Missing required fields")
        
        if not isinstance(data["options"], list) or len(data["options"]) != 4:
            raise ValueError("Need exactly 4 options")
        
        if not isinstance(data["correct_index"], int) or data["correct_index"] not in [0, 1, 2, 3]:
            raise ValueError("correct_index must be 0, 1, 2, or 3")
        
        # Перевірка, що питання та опції не порожні
        if not data["question"] or not all(data["options"]):
            raise ValueError("Question or options are empty")
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Response text: {text if 'text' in locals() else 'No response'}")
    except Exception as e:
        print(f"LLM error: {e}")
        print(f"Response text: {text if 'text' in locals() else 'No response'}")
    
    # Fallback - повертаємо випадкове питання відповідної складності
    print(f"Using fallback question (category: {category}, difficulty: {difficulty})")
    
    fallback_pool = FALLBACK_QUESTIONS.get(difficulty, FALLBACK_QUESTIONS["medium"])
    return random.choice(fallback_pool)


def generate_question_batch(count=5, category="mixed", difficulty="medium"):
    """
    Генерує кілька питань за один раз (більш ефективно).
    
    Args:
        count: кількість питань
        category: категорія питань
        difficulty: рівень складності
    
    Returns:
        list з питаннями
    """
    questions = []
    
    for _ in range(count):
        try:
            question = generate_mcq_question(category, difficulty)
            questions.append(question)
        except Exception as e:
            print(f"Error generating question: {e}")
            # Додаємо fallback
            fallback_pool = FALLBACK_QUESTIONS.get(difficulty, FALLBACK_QUESTIONS["medium"])
            questions.append(random.choice(fallback_pool))
    
    return questions


def validate_question(question):
    """
    Перевіряє, чи питання валідне.
    
    Args:
        question: dict з питанням
    
    Returns:
        bool - True якщо валідне
    """
    try:
        # Перевірка структури
        if not isinstance(question, dict):
            return False
        
        required_keys = ["question", "options", "correct_index"]
        if not all(k in question for k in required_keys):
            return False
        
        # Перевірка options
        if not isinstance(question["options"], list) or len(question["options"]) != 4:
            return False
        
        # Перевірка correct_index
        if not isinstance(question["correct_index"], int):
            return False
        
        if question["correct_index"] not in [0, 1, 2, 3]:
            return False
        
        # Перевірка, що все не пусте
        if not question["question"].strip():
            return False
        
        if not all(opt.strip() for opt in question["options"]):
            return False
        
        return True
        
    except Exception:
        return False


# Тестування
if __name__ == "__main__":
    print("=== Testing question generation ===\n")
    
    # Тест 1: Easy Python
    print("1. Easy Python question:")
    q1 = generate_mcq_question("python", "easy")
    print(json.dumps(q1, indent=2))
    print(f"Valid: {validate_question(q1)}\n")
    
    # Тест 2: Hard Algorithms
    print("2. Hard Algorithms question:")
    q2 = generate_mcq_question("algorithms", "hard")
    print(json.dumps(q2, indent=2))
    print(f"Valid: {validate_question(q2)}\n")
    
    # Тест 3: Mixed Medium
    print("3. Mixed Medium question:")
    q3 = generate_mcq_question("mixed", "medium")
    print(json.dumps(q3, indent=2))
    print(f"Valid: {validate_question(q3)}\n")
    
    # Тест 4: Batch generation
    print("4. Generating batch of 3 questions:")
    batch = generate_question_batch(3, "javascript", "medium")
    for i, q in enumerate(batch, 1):
        print(f"\nQuestion {i}:")
        print(json.dumps(q, indent=2))
        print(f"Valid: {validate_question(q)}")
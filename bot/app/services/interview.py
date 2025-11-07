import json
import time
import os

HISTORY_DIR = "data/interviews"
os.makedirs(HISTORY_DIR, exist_ok=True)

def _file(user_id):
    return f"{HISTORY_DIR}/{user_id}.json"

def save_interview(user_id: int, answers: list, score: int):
    record = {
        "timestamp": int(time.time()),
        "score": score,
        "answers": answers
    }

    file_path = _file(user_id)

    # Завантажуємо стару історію або створюємо нову
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append(record)

    with open(file_path, "w") as f:
        json.dump(history, f, indent=2)

def load_history(user_id: int):
    file_path = _file(user_id)
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        return json.load(f)

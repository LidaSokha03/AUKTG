from app.db.session import interviews_collection
from datetime import datetime

def save_interview_result(user_id: int, score: int, total: int):
    record = {
        "user_id": user_id,
        "score": score,
        "total": total,
        "timestamp": datetime.now()
    }
    interviews_collection.insert_one(record)

def get_interview_history(user_id: int):
    records = list(interviews_collection.find({"user_id": user_id}))
    records.sort(key=lambda x: x.get("timestamp", datetime.min))
    return records

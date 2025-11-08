from app.db.session import interviews_collection
from datetime import datetime

def save_interview_result(user_id: int, score: int, total: int, questions: list = None):
    record = {
        "user_id": user_id,
        "score": score,
        "total": total,
        "questions": questions if questions else [],
        "timestamp": datetime.now()
    }
    interviews_collection.insert_one(record)

def get_interview_history(user_id: int):
    records = list(interviews_collection.find({"user_id": user_id}))
    records.sort(key=lambda x: x.get("timestamp", datetime.min))
    return records

def clear_interview_history(user_id: int):
    result = interviews_collection.delete_many({"user_id": user_id})
    return result.deleted_count
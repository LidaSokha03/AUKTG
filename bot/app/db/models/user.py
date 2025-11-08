from app.db.database import db

class User:
    def __init__(self, tg_id):
        self.tg_id = tg_id
        self.is_registered = False

    def save(self):
        db.users.insert_one({
            "tg_id": self.tg_id,
            "is_registered": False
        })

    def exists(self):
        user = db.users.find_one({"tg_id": self.tg_id})
        if user:
            return True
        return False

    def load(self):
        user = db.users.find_one({"tg_id": self.tg_id})
        if user:
            self.is_registered = user.get("is_registered", False)
        return user

    def registered(self):
        user = db.users.find_one({
            "tg_id": self.tg_id
        })
        if user:
            self.is_registered = user.get("is_registered", False)
        return self.is_registered

    def set_registered(self):
        db.users.update_one(
            {"tg_id": self.tg_id},
            {"$set": {"is_registered": True}}
        )
        self.is_registered = True

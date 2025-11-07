from pymongo import MongoClient
import os
import sys

# ✅ Додаємо можливість імпортувати config з рівня вище
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from config import MONGO_URI, MONGO_DB  # імпорт з bot/config.py

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# Collections
users_collection = db["users"]
profiles_collection = db["profiles"]
interviews_collection = db["interviews"]  # ✅ історія інтервʼю

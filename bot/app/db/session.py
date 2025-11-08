from pymongo import MongoClient
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from config import MONGO_URI, MONGO_DB 

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

users_collection = db["users"]
profiles_collection = db["profiles"]
interviews_collection = db["interviews"]

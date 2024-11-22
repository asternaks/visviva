import os

from pymongo import MongoClient

from config import get_mongo_uri

MONGO_URI = get_mongo_uri()
client = MongoClient(MONGO_URI)
db = client[os.getenv("MONGO_DB_NAME")]
users_collection = db['users']

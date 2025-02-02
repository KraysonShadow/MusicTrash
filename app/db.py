from pymongo import MongoClient

MONGO_URI = "mongodb://mongo:27017"
client = MongoClient(MONGO_URI)
DB_NAME = "form_db"
TEMPLATES_COLLECTION = "templates"

def get_session():
    db = client[DB_NAME]
    return db
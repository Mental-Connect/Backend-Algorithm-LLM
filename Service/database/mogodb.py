from pymongo import MongoClient

# Setup MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["Psycho_session"]
collection = db["Information"]

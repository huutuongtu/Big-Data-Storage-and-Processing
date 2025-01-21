from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["test_database"]

# collection = db["test_collection"]
result = db["coingecko_collection"].drop()

client.close()

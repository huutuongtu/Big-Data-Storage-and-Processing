from pymongo import MongoClient
import time
client = MongoClient("mongodb://localhost:27017/")
db = client["test_database"]
# collection = db["test_collection"]
collection = db["coingecko_collection"]
collection_x = db["test_collection"]

while True:
    documents = collection.find()
    for doc in documents:
        print(doc)

    print("-"*10)
    
    documents = collection_x.find()
    for doc in documents:
        print(doc)
    print("-"*10)
    time.sleep(10)
client.close()

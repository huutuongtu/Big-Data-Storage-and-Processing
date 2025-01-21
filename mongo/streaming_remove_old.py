import time
from pymongo import MongoClient
from datetime import datetime, timedelta

def delete_old_data():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["test_database"]
    collection = db["test_collection"]
    one_minute_ago = datetime.now() - timedelta(minutes=1)    
    result = collection.delete_many({
        "time": {"$lt": one_minute_ago.isoformat()} 
    })
    print(f"{datetime.now()} - Deleted {result.deleted_count} old documents.")

if __name__ == "__main__":
    while True:
        delete_old_data()
        time.sleep(20)  

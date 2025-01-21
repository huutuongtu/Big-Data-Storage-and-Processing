import csv
from confluent_kafka import Producer
import uuid

# Kafka configuration
conf = {
    'bootstrap.servers': 'localhost:9092',  # Kafka broker
    'client.id': 'python-producer'
}

# Create Producer instance
producer = Producer(conf)

# CSV file path
csv_file_path = '/home/tu/BigData/Big-Data-Project/test_bigdata/test.csv'

# Function to read CSV and send data to Kafka
def read_and_produce():
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            tweet_text = row['tweet_text']
            tweet_id = row['tweet_id']
            message = {
                'tweet_id': tweet_id,
                'tweet_text': tweet_text
            }
            producer.produce('tweets_topic', key=tweet_id, value=str(message))
            print(f"Produced: {tweet_text}")
    
    # Wait for any outstanding messages to be delivered
    producer.flush()

# Run the producer function
read_and_produce()

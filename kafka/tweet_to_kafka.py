import json
import random
import time
from kafka import KafkaProducer
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
)

cnt = 0
topic = 'tweets_coin'

f = open("/home/tu/BigData/Big-Data-Project/test_bigdata/kafka/tweet/sample.txt", "r", encoding="utf8").readlines()

def generate_tweet():
    now = datetime.now()
    global cnt
    tweet_id = cnt
    cnt = cnt + 1
    tweet_text = random.choice(f)
    return {'tweet_id': tweet_id, 'time': now.isoformat(), 'tweet_text': tweet_text}

# 0.5s push to kafka
while True:
    tweet = generate_tweet()
    tweet_json = json.dumps(tweet)  
    producer.send(topic, value=tweet_json.encode('utf-8'))  # Encode as bytes and send to Kafka
    print(f"Published: {tweet}")
    time.sleep(0.5)

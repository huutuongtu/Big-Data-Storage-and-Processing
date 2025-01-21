from binance_connector.binance_processor import crawl_binance_training_data
import json
import random
import time
from kafka import KafkaProducer
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
)

topic = 'coingecko_coin'


# 1-minute batch push to Kafka
while True:
    change = crawl_binance_training_data()
    for price_change in change:
        print(f"Published: {price_change}")
        producer.send(topic, value=json.dumps(price_change).encode('utf-8'))
    time.sleep(15)

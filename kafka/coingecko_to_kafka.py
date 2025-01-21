from coingecko.market import Market_service
import json
import random
import time
from kafka import KafkaProducer
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
)

topic = 'coingecko_coin'
market_service = Market_service()
mapping_id_to_name = market_service.list_all_coin_id_and_name()
coins_id = market_service.get_top_10_ids()


def generate_price_changes(id):
    res = market_service.get_change_percentage_for_bubble_by_id(id)
    return res

# 1-minute batch push to Kafka
while True:
    for id in coins_id:
        pc = generate_price_changes(id)
        price_change = {"id": id, "change": pc}
        print(f"Published: {price_change}")
        producer.send(topic, value=json.dumps(price_change).encode('utf-8'))
    time.sleep(60)

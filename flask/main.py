from flask import Flask, jsonify, render_template, Response
from flask_socketio import SocketIO, emit
import pandas as pd
import numpy as np
import threading
from pymongo import MongoClient
from collections import defaultdict
import re
import csv
import time
import json

app = Flask(__name__)
socketio = SocketIO(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["test_database"]
collection = db["test_collection"]
collection_coin = db["coingecko_collection"]


# hashtag and name of coin mapping
def load_coin_info(csv_file):
    coin_mapping = {}
    hashtag_mapping = {}
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            coin_mapping[row['name'].lower()] = row['name']
            hashtag_mapping["#" + row['symbol'].lower()] = row['name']
            hashtag_mapping["#" + row['name'].lower()] = row['name']
    return coin_mapping, hashtag_mapping

coin_mapping, hashtag_mapping = load_coin_info("/home/tu/BigData/Big-Data-Project/test_bigdata/kafka/coingecko/data/top_100.csv")


# For crypto Bubble
df = pd.DataFrame()

# For coingecko
# def init_bubble():
#     global df
#     data = collection_coin.find()
#     coin_data = []
#     for item in data:
#         if item.get('id') is not None:
#             coin_id = item.get('id')
#             [_token, _change_5m, _change_15m, _change_1h] = item.get('change', [None, None, None])  # Default to None if 'change' is not present
#             bubble_size = _change_5m*100
            
#             if coin_id and _change_5m is not None:
#                 coin_data.append({"Coin": coin_id, "Change_5m": _change_5m, "Bubble_Size": bubble_size})

#     new_df = pd.DataFrame(coin_data)
#     if not df.empty:
#         df.update(new_df)
#     else:
#         df = new_df
#     # ensure the position not re-init
#     if "X" not in df.columns:
#         df['X'] = np.random.uniform(0, 100, len(df))
#         df['Y'] = np.random.uniform(0, 100, len(df))
#         df['Vx'] = np.random.uniform(-0.2, 0.2, len(df))
#         df['Vy'] = np.random.uniform(-0.2, 0.2, len(df))
#     return df

# For binance
def init_bubble():
    global df
    data = collection_coin.find()
    coin_data = []
    for item in data:
        if item.get('id') is not None:
            coin_id = item.get('id')
            change_15m = float(item.get('change'))
            bubble_size = float(change_15m)*100
            
            if coin_id and change_15m is not None:
                coin_data.append({"Coin": coin_id, "Change_5m": change_15m, "Bubble_Size": bubble_size})

    new_df = pd.DataFrame(coin_data)
    if not df.empty:
        df.update(new_df)
    else:
        df = new_df
    # ensure the position not re-init
    if "X" not in df.columns:
        df['X'] = np.random.uniform(0, 100, len(df))
        df['Y'] = np.random.uniform(0, 100, len(df))
        df['Vx'] = np.random.uniform(-0.2, 0.2, len(df))
        df['Vy'] = np.random.uniform(-0.2, 0.2, len(df))
    return df

df = init_bubble()
print(df)

def generate_position_data():
    global df
    while True:
        # Increment positions based on velocities
        df['X'] += df['Vx']
        df['Y'] += df['Vy']

        # Reverse velocities if hitting the edge
        df['Vx'] = np.where((df['X'] <= 0) | (df['X'] >= 100), -df['Vx'], df['Vx'])
        df['Vy'] = np.where((df['Y'] <= 0) | (df['Y'] >= 100), -df['Vy'], df['Vy'])

        response_data = {
            'X': df['X'].tolist(),
            'Y': df['Y'].tolist(),
            'Bubble_Size': df['Bubble_Size'].tolist(),
            'Color': ['green' if float(change) > 0 else 'red' for change in df['Change_5m']],
            'Coin': df['Coin'].tolist(),
            'Change_5m': df['Change_5m'].tolist(),
        }

        # Emit data to client
        socketio.emit('update_bubble_data', response_data)
        
        # send streaming
        time.sleep(0.02)

# Function to simulate Change_5m updates every 10 seconds
def update_Change_5m():
    global df
    while True:
        df = init_bubble()
        response_data = {
            'X': df['X'].tolist(),
            'Y': df['Y'].tolist(),
            'Bubble_Size': df['Bubble_Size'].tolist(),
            'Color': ['green' if float(change) > 0 else 'red' for change in df['Change_5m']],
            'Coin': df['Coin'].tolist(),
            'Change_5m': df['Change_5m'].tolist(),
        }

        # print(response_data)
        # Emit data to the client
        socketio.emit('update_bubble_data', response_data)
        time.sleep(10)


# For sentiment analysis
def get_canonical_coin_name(coin):
    return coin_mapping.get(coin.lower(), None)

def get_canonical_coin_from_hashtag(coin):
    return hashtag_mapping.get(coin.lower(), None)

def detect_coins(text):
    # categorize a text belogn to which coin?
    detected_coins = set()
    hashtags = re.findall(r'#\w+', text)
    for hashtag in hashtags:
        canonical_name = get_canonical_coin_from_hashtag(hashtag)
        if canonical_name:
            detected_coins.add(canonical_name)
    
    for coin in coin_mapping.keys():
        if coin.lower() in text.lower():  # Case-insensitive match
            canonical_name = get_canonical_coin_name(coin)
            if canonical_name:
                detected_coins.add(canonical_name)
    
    return detected_coins

def analyze_and_group():
    # get top 5 most coin is mention from tweets
    tweets = collection.find()
    coin_mentions = defaultdict(lambda: {"positive": 0, "negative": 0})

    for tweet in tweets:
        text = tweet['text']
        sentiment = tweet['prediction']  # 1.0 for positive, 0.0 for negative/neutral
        detected_coins = detect_coins(text)

        for coin in detected_coins:
            if sentiment == 1.0:
                coin_mentions[coin]["positive"] += 1

            else:
                coin_mentions[coin]["negative"] += 1

    top_coins = sorted(coin_mentions.items(), key=lambda x: x[1]["positive"] + x[1]["negative"], reverse=True)[:5]
    return top_coins

# auto reset each 20s
@app.route('/stream_data')
def stream_data():
    def generate():
        while True:
            top_coins = analyze_and_group()
            coins = [coin for coin, _ in top_coins]
            positive_counts = [coin_data["positive"] for _, coin_data in top_coins]
            negative_counts = [coin_data["negative"] for _, coin_data in top_coins]
            data = {
                "coins": coins,
                "positive_counts": positive_counts,
                "negative_counts": negative_counts
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(20)

    return Response(generate(), content_type='text/event-stream')

@app.route('/sentiment')
def index():
    return render_template('./sentiment.html')

@app.route('/bubble')
def bubble():
    return render_template('./bubble.html')

if __name__ == "__main__":
    threading.Thread(target=generate_position_data, daemon=True).start()
    threading.Thread(target=update_Change_5m, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=5000)

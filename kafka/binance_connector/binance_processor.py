import pandas as pd
from binance.spot import Spot
from .utils import *
import json

spot_client = Spot()

def crawl_binance_training_data():
    crawl_data = []
    ticker_set = get_binance_listed_asset()
    print("crawling")
    for i in range(50):
        ticker = ticker_set[i]
        if(ticker == 'DAI' or 'USD' in ticker):
            continue
        data = get_binance_historical_data(spot_client, ticker+'USDT', '1m', 20)
        close_last = float(data[-16]['close'])
        latest_close = float(data[-1]['close'])
        percentage_change = 100*(latest_close - close_last)/close_last
        if percentage_change==0: # for draw coin no change
            percentage_change = 0.01
        data = {'id': ticker, 'change': percentage_change}
        crawl_data.append(data)
    return crawl_data

def get_binance_listed_asset():
    global spot_client
    exchange_info = spot_client.exchange_info()
    listed_asset = [
        symbol['baseAsset'] for symbol in exchange_info['symbols'] if
        symbol['quoteAsset'] == 'USDT'
        and symbol['isSpotTradingAllowed']
        and symbol['isMarginTradingAllowed']
    ]
    print(len(listed_asset))
    return listed_asset

def get_binance_historical_data(binance_client, symbol, interval, lookback):
    klines = binance_client.klines(symbol=symbol, interval=interval, limit=lookback)
    fields = [
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ]
    field_included = [
        'timestamp', 'open', 'high', 'low', 'close'
    ]
    field_indices = [fields.index(field) for field in field_included]
    data = [
        {field: (format_timestamp(row[i]) if field == "timestamp" else row[i])
        for field, i in zip(field_included, field_indices)}
        for row in klines
    ]
    return data


# print(crawl_binance_training_data())

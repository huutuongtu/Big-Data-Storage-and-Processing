import math
from datetime import datetime

RSI_LENGTH = 14
EMA_LENGTH = 9
WMA_LENGTH = 45

def compare_symbol(symbol1, symbol2):
    upper_symbol = symbol1.upper()
    return upper_symbol == symbol2 or '1M'+ upper_symbol == symbol2 or '1000'+upper_symbol == symbol2

def get_valid_value(value):
    if value is not None and not (isinstance(value, float) and math.isnan(value)):
        return value
    return 0

def format_timestamp(ts):
    return datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d %H:%M:%S')

def get_start_end_by_lookback_and_interval(interval, lookback):
    end = int(datetime.now().timestamp())
    start = end - lookback*interval
    return start, end

def validate_text(text, ticker, name):
    return text.upper() == ticker.upper() or text.upper() == name.upper()
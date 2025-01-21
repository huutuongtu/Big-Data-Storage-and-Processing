import requests
import pandas as pd
from pycoingecko import CoinGeckoAPI
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tqdm import tqdm

class Market_service():

    def __init__(self, currency='usd'):
        self.coingecko = CoinGeckoAPI(demo_api_key = '')
        self.currency = currency
        # only need to run once to track top 100 coin
        # self.log_top_100_coin()
       
        self.coin_infos = pd.read_csv("/home/tu/BigData/Big-Data-Project/test_bigdata/kafka/coingecko/data/top_100.csv")
        self.ids_to_name = {}
        for i in range(len(self.coin_infos)):
            self.ids_to_name[self.coin_infos['id'][i]] = self.coin_infos['name'][i]

    # return dictionary contain coin ids and name of that coin
    def list_all_coin_id_and_name(self,):
        return self.ids_to_name

    def get_top_10_ids(self,):
        top_10 = self.coin_infos['id'][:13]
        # delete usdt and usdc cuz it always 1, delete steth because the same price as eth
        del top_10[8]
        del top_10[7]
        del top_10[2]
        return list(top_10)

    # get top 100 market cap and write to file
    def log_top_100_coin(self, ):
        f = open("/home/tu/BigData/Big-Data-Project/test_bigdata/kafka/coingecko/data/top_100.csv", "a", encoding="utf8")
        f.write("id,symbol,name,market_cap_rank\n")
        respond = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc').json()
        for coin_data in tqdm(respond):
            coin_info = coin_data['id'] + "," + coin_data['symbol'] + "," + coin_data['name'] + "," + str(coin_data['market_cap_rank']) + "\n"
            f.write(coin_info)


    # step is one hours => 720 values
    def get_coin_info_by_id_30days(self, id):
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        now_unix = str(now.timestamp())
        thirty_days_ago_unix = str(thirty_days_ago.timestamp())
        ohlc = self.coingecko.get_coin_market_chart_range_by_id(id = id, vs_currency = 'usd', from_timestamp=thirty_days_ago_unix, to_timestamp=now_unix)
        df = pd.DataFrame(ohlc)
        return df
    
    # step is 5 minutes => 12 values, time, values with 3 cols
    def get_change_percentage_for_bubble_by_id(self, id):
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        now_unix = str(now.timestamp())
        one_hour_ago_unix = str(one_hour_ago.timestamp())
        ohlc = self.coingecko.get_coin_market_chart_range_by_id(id = id, vs_currency = 'usd', from_timestamp=one_hour_ago_unix, to_timestamp=now_unix)
        df = pd.DataFrame(ohlc)
        result = {}
        latest_value = df['prices'].iloc[-1][1]
        earlier_value = df['prices'].iloc[-2][1]
        fifteen_minute_value = df['prices'].iloc[-4][1]
        result['token'] = id
        percentage_change = ((latest_value - earlier_value) / earlier_value) * 100
        result['change_percent_five_min'] = percentage_change
        percentage_change = ((latest_value - fifteen_minute_value) / fifteen_minute_value) * 100
        result['change_percent_fifteen_min'] = percentage_change
        one_hour_value = df['prices'].iloc[0][1]
        percentage_change = ((latest_value - one_hour_value) / one_hour_value) * 100
        result['change_percent_one_hour'] = percentage_change
    
        return result

    def get_change_percentage(self, id):
        now = datetime.now()
        one_hour_ago = now - timedelta(minutes=1)
        now_unix = str(now.timestamp())
        one_hour_ago_unix = str(one_hour_ago.timestamp())
        ohlc = self.coingecko.get_coin_market_chart_range_by_id(id = id, vs_currency = 'usd', from_timestamp=one_hour_ago_unix, to_timestamp=now_unix)
        # df = pd.DataFrame(ohlc)
        # print(df)
    

    # This will get data last 30 days and draw the chart by providing id of coin
    # def get_chart_coin_by_id_30days(self, id):
    #     df = self.get_coin_info_by_id_30days(id)
    #     prices = pd.DataFrame(df['prices'].tolist(), columns=['timestamp', 'price'])
    #     prices['datetime'] = pd.to_datetime(prices['timestamp'], unit='ms')
    #     plt.figure(figsize=(12, 6))
    #     plt.plot(prices['datetime'], prices['price'], label='Ethereum Price (USD)', color='blue')
    #     plt.title(f"{self.ids_to_name[id]} Price over the Last 30 Days", fontsize=16)
    #     plt.xlabel("Date", fontsize=12)
    #     plt.ylabel("Price (USD)", fontsize=12)
    #     plt.xticks(rotation=45)
    #     plt.grid(True)
    #     plt.legend()
    #     plt.tight_layout()
    #     plt.savefig(f'/home/tu/BigData/Big-Data-Project/test_bigdata/coingecko/{self.ids_to_name[id]}.png')
    #     return f'/home/tu/BigData/Big-Data-Project/test_bigdata/coingecko/{self.ids_to_name[id]}.png'
    

market = Market_service()
print(market.get_change_percentage("ethereum"))

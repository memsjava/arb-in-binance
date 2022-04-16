from time import time

from binance.client import Client
import gasykamanja.kajy as kj
import gasykamanja.binansaRehetra as br
import json


class grand_arbirtrage():

    def __init__(self):
        f = open("settings.json")
        config = json.load(f)
        self.client = Client(config['API_SECRET'], config['API_PUBLIC'])
        self.start_coin = config['start_coin']
        self.capital = float(config['capital']) if config['capital'] != "" else br.get_balance(
            self.client, self.start_coin)
        self.live_trade = config['live_trade']

    def get_data(self):
        res = br.get_all_data(self.client)
        return res

    def get_triplet(self, start_coin, data):
        res = kj.get_all_triplet(start_coin, data)
        return res

    def my_arbitrage(self, data, triplet, capital, start_coin="USDT"):
        res = kj.my_arbitrage(self.client, data, triplet,
                              capital, start_coin="USDT")
        return res

    def run(self):
        data = self.get_data()
        break_ = False
        start_coin = self.start_coin
        triplets = self.get_triplet(start_coin, data)
        capital = self.capital
        for triplet in triplets:
            # triplet looks like this ["BTCUSDT", "ETHBTC", 'ETHUSDT']
            if not break_:
                res = self.my_arbitrage(data, triplet, capital, start_coin)
                if self.live_trade:
                    br.handleTrade(self.client, capital, triplet, data, res)
                    if res:
                        break_ = True


ge = grand_arbirtrage()
ge.run()

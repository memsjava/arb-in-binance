import asyncio
from time import time

from binance.client import Client
import gasykamanja.kajy as kj
import gasykamanja.binansaRehetra as br
from gasykamanja.database import dbManager
import json


class grand_arbirtrage():

    def __init__(self):
        f = open("settings.json")
        config = json.load(f)
        self.client = Client(config['API_PUBLIC'], config['API_SECRET'])
        self.start_coin = config['start_coin']
        self.capital = float(
            config['capital']) if config['capital'] != "" else br.get_balance(
                self.client, self.start_coin)
        self.live_trade = config['live_trade']
        self.interest = config['interest']
        self.sell_dust = config['sell_dust']

    def get_data(self):
        res = br.get_all_data(self.client)
        return res

    def get_triplet(self, start_coin, data):
        res = kj.get_all_triplet(start_coin, data)
        return res

    def my_arbitrage(self, data, triplet, capital, start_coin="USDT"):
        res, interest = kj.my_arbitrage(self.client, data, triplet, capital,
                                        start_coin)
        return res, interest

    async def main(self):
        db_ = dbManager()
        if db_.check_written_db():
            a, b = db_.getActiveOrder()
            if a:
                while True:
                    car = input(
                        "There is a data in previous arb, continue \"C\" or skip current arb \"R\": "
                    )
                    if car.capitalize() == "C":
                        # br.getAndSendOrder(self.client)
                        break
                    if car.capitalize() == "R":
                        pair, err = db_.ignore_current_arb()
                        if pair:
                            br.close_active_order(self.client, pair)
                        break

        while True:
            try:
                await self.run()
                await asyncio.sleep(300)
            except Exception as e:
                print(e)
                await asyncio.sleep(30)

    def isFollowOrder(self):
        db_ = dbManager()
        if db_.check_written_db():
            a, b = db_.getActiveOrder()
            if a:
                br.getAndSendOrder(self.client, self.sell_dust)
                return True
        return False

    def execute(self):
        print("-------------\n")
        triplets, data, break_, start_coin = [], [], False, self.start_coin
        data = self.get_data()
        triplets = self.get_triplet(start_coin, data)
        if triplets:
            capital = self.capital
            for triplet in triplets:
                # triplet looks like this ["BTCUSDT", "ETHBTC", 'ETHUSDT']
                if not break_:
                    res, interest = self.my_arbitrage(data, triplet, capital,
                                                      start_coin)
                    if interest:
                        if self.live_trade and interest > self.interest:
                            res = br.handleTrade(self.client, capital, triplet,
                                                 data, res)
                            if res:
                                break_ = True
        else:
            print("> no result, please change the start_coin\n")

    async def run(self):
        if not self.isFollowOrder():
            self.execute()


ge = grand_arbirtrage()
asyncio.run(ge.main())

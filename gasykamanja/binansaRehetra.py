import math
from os import symlink
from regex import E
import requests

from urllib3 import Retry
from gasykamanja.database import dbManager


def get_buy_info(client, symbol_, price_, amount_):
    precision_price, precision_qty = get_symbol_precision(client, symbol_)
    price = float_precision(price_, precision_price)
    amount_ = float_precision(amount_ / price, precision_qty)
    return price, amount_


def get_sell_info(client, symbol_, price_, amount_):
    precision_price, precision_qty = get_symbol_precision(client, symbol_)
    price = float_precision(price_, precision_price)
    amount_ = float_precision(amount_, precision_qty)
    return price, amount_


def float_precision(f, n):
    # f = round_step_size(f, n)
    precision = int(round(-math.log(n, 10), 0))
    f = math.floor(float(f) * (10**precision))
    f = f / ((10**precision))
    # f = round(f,n)
    #new_qty = "{:0.0{}f}".format(f , n)
    return f  # float(new_qty)


def get_balance(client, currency):
    return float(client.get_asset_balance(asset=currency)['free'])


def to_btc(client, asset, amount):
    res, err = None, None
    if asset == "BTC":
        res = float(amount)
    else:
        symbol = asset + "BTC"
        try:
            res = float(
                client.get_avg_price(symbol=symbol)['price']) * float(amount)
        except Exception as e:
            if 'Invalid symbol' in e.message:
                symbol = "BTC" + asset
                try:
                    res = float(client.get_avg_price(symbol=symbol)['price'])
                    res = 1 / res * float(amount)
                except:
                    pass
            err = e
    return res


def get_dust_amount(client):
    res, err = None, None
    try:
        res = client.get_avg_price(symbol='BTCUSDT')['price']
        res = 1 / float(res)
    except Exception as e:
        err = e
    return res


def get_and_transfert_dust(client):
    balances = client.get_account()['balances']
    dust = get_dust_amount(client)
    dust_assets = []
    for balance in balances:
        if float(balance['free']) > 0.0:
            avg = to_btc(client, balance['asset'], balance['free'])
            if avg:
                if avg < dust:
                    dust_assets.append(balance['asset'])
    if len(dust_assets):
        dust_assets = ','.join(dust_assets)
        client.transfer_dust(asset=dust_assets)
        print("all dust is converting in BNB right now ...")


def get_symbol_precision(client, _symbol):
    market_data = client.get_symbol_info(_symbol)

    for market in market_data['filters']:
        if market['filterType'] == 'LOT_SIZE':
            precision_qty = float(market['stepSize'])
        elif market['filterType'] == 'PRICE_FILTER':
            precision_price = float(market['tickSize'])

    return precision_price, precision_qty


def reduce_amount(amount, precision_qty, precision):
    # print(precision)
    amount = math.floor(float(amount) * (10**precision))
    amount = amount / ((10**precision))
    # amount = float_precision(amount, precision_qty)
    return amount


def sendLmtOrder(client, side, symbol_, amount, price):
    order = None
    try:
        if side == "buy":
            # print("amount before", amount)
            price, amount = get_buy_info(client, symbol_, price, amount)
            # print(price, amount)
            if amount and price:
                order = client.order_limit_buy(symbol=symbol_,
                                               quantity=amount,
                                               price=price)
        else:

            price, amount = get_sell_info(client, symbol_, price, amount)
            if amount and price:
                order = client.order_limit_sell(
                    symbol=symbol_,
                    quantity=amount,
                    price=price,
                )
        print(price, amount)
    except Exception as e:
        print("order exception", e, amount, symbol_)
        if "Account has insufficient balance" in str(e.message):
            precision_price, precision_qty = get_symbol_precision(
                client, symbol_)

            precision = 5
            notStop = True
            while notStop:
                precision -= 1
                amount_ = reduce_amount(amount, precision_qty, precision)
                if amount_ and price and precision > 0:
                    print(price, amount_)
                    try:
                        if side == "buy":
                            order = client.order_limit_buy(symbol=symbol_,
                                                           quantity=amount_,
                                                           price=price)
                        else:
                            order = client.order_limit_sell(symbol=symbol_,
                                                            quantity=amount_,
                                                            price=price)
                        # print(order)
                        notStop = False
                        break
                    except Exception as err:
                        print(err)
                else:
                    notStop = False

    return order


def getStatusOrder(client, symbol_, orderId_):
    res = None
    orderId_ = int(orderId_)
    currentOrder = client.get_order(symbol=symbol_, orderId=orderId_)
    if currentOrder['status'] == 'FILLED':
        res = currentOrder['executedQty']
        res = float(res)
    return res


def getAndSendOrder(client, sell_dust):
    dbManage = dbManager()
    pair, err = dbManage.getActiveOrder()
    capital = getStatusOrder(client, pair.paire, pair.order_id)
    # print("getAndSendOrder", capital)
    if capital:
        print("order %s: %s %s @ %s is ok" %
              (pair.order_id, pair.side, pair.paire, pair.price))
        new_pair, err = dbManage.updateAndSwitchOrder()
        # update amount with the real amount bought or sold
        pair.amount = capital
        pair.is_succeed = True
        pair.save()
        is_last = dbManage.closeLastOrder()
        if is_last and sell_dust:
            get_and_transfert_dust(client)
        if new_pair:
            fee = capital * 0.1 / 100
            amount = capital - fee
            if not isValidPrice(new_pair.paire, new_pair.price):
                return None
            order = sendLmtOrder(client, new_pair.side, new_pair.paire, amount,
                                 new_pair.price)
            # print("order", order)
            if order:
                pair.is_active = False
                pair.save()

                new_pair.is_active = True
                new_pair.order_id = str(order['orderId'])
                new_pair.save()
        else:
            print(err)
    else:
        print("order %s: %s %s %s @ %s still not filled" %
              (pair.order_id, pair.side, pair.amount, pair.paire, pair.price))


def handleTrade(client, capital, triplet, data, way):
    res = None
    to_store = []
    try:
        a1 = data[triplet[0]]
        a2 = data[triplet[1]]
        a3 = data[triplet[2]]
        if way == 'way1':
            side = 'buy'
            symbol_ = triplet[0]
            fee = capital * 0.1 / 100
            amount = capital - fee
            price = float(a1["b"])
            if not isValidPrice(symbol_, price):
                return None
            order = sendLmtOrder(client, side, symbol_, amount, price)
            # capital = getStatusOrder(client, symbol_, order['orderId'])

            to_store.append({
                "paire": symbol_,
                "side": side,
                "price": price,
                "amount": amount
            })

            side = 'buy'
            symbol_ = triplet[1]
            # fee = capital * 0.1 / 100
            # amount = capital - fee
            price = float(a2["b"])
            # order = sendLmtOrder(client, side, symbol_, amount, price)
            # capital = getStatusOrder(client, symbol_, order['orderId'])
            to_store.append({
                "paire": symbol_,
                "side": side,
                "price": price,
                "amount": 0
            })

            side = 'sell'
            symbol_ = triplet[2]
            # fee = capital * 0.1 / 100
            # amount = capital - fee
            price = float(a3["a"])
            # order = sendLmtOrder(client, side, symbol_, amount, price)
            # capital = getStatusOrder(client, symbol_, order['orderId'])
            # res = capital
            to_store.append({
                "paire": symbol_,
                "side": side,
                "price": price,
                "amount": 0
            })

        elif way == 'way2':
            print(way)
            side = 'buy'
            symbol_ = triplet[0]
            fee = capital * 0.1 / 100
            amount = capital - fee
            price = float(a3["b"])

            if not isValidPrice(symbol_, price):
                return None

            order = sendLmtOrder(client, side, symbol_, amount, price)
            # capital = getStatusOrder(client, symbol_, order['orderId'])
            to_store.append({
                "paire": symbol_,
                "side": side,
                "price": price,
                "amount": amount
            })

            side = 'sell'
            symbol_ = triplet[1]
            fee = capital * 0.1 / 100
            # amount = capital - fee
            price = float(a2["a"])
            # order = sendLmtOrder(client, side, symbol_, amount, price)
            # capital = getStatusOrder(client, symbol_, order['orderId'])
            to_store.append({
                "paire": symbol_,
                "side": side,
                "price": price,
                "amount": 0
            })

            side = 'sell'
            symbol_ = triplet[2]
            # fee = capital * 0.1 / 100
            # amount = capital - fee
            price = float(a1["a"])
            # order = sendLmtOrder(client, side, symbol_, amount, price)
            # capital = getStatusOrder(client, symbol_, order['orderId'])
            # res = capital
            to_store.append({
                "paire": symbol_,
                "side": side,
                "price": price,
                "amount": 0
            })
        if order:
            dbManage = dbManager()
            tahiry_, error = dbManage.set_orders(to_store)
            if not error:
                tahiry_.voalohany_.is_active = True
                tahiry_.voalohany_.order_id = str(order['orderId'])
                tahiry_.voalohany_.save()

    except:
        pass

    return res


def isValidPrice(symbol, price):
    res = False
    a = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=" +
                     symbol)
    if abs(
        (float(a.json()['price']) - float(price)) / float(price) * 100) < 10:
        res = True
    return res


def get_all_data(client):
    res = {}
    try:
        data = client.get_orderbook_tickers()
        for ticker in data:
            pair = ticker['symbol']
            ask = float(ticker['askPrice'])
            bid = float(ticker['bidPrice'])

            res[pair] = {"b": bid, "a": ask}

    except Exception as e:
        print(e)
        pass
    return res


def close_active_order(client, pair):
    result = client.cancel_order(symbol=pair.paire, orderId=pair.order_id)
    return result
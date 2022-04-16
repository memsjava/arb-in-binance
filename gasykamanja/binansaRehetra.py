import math
from binance.helpers import round_step_size
import time


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
    f = round_step_size(f, n)
    # f = round(f,n)
    #new_qty = "{:0.0{}f}".format(f , n)
    return f  # float(new_qty)


def get_balance(client, currency):
    return float(client.get_asset_balance(asset=currency)['free'])


def get_symbol_precision(client, _symbol):
    market_data = client.get_symbol_info(_symbol)

    for market in market_data['filters']:
        if market['filterType'] == 'LOT_SIZE':
            precision_qty = float(market['stepSize'])
        elif market['filterType'] == 'PRICE_FILTER':
            precision_price = float(market['tickSize'])

    return precision_price, precision_qty


def sendLmtOrder(client, side, symbol_, amount, price):
    order = None
    try:
        if side == "buy":
            price, amount = get_buy_info(client, symbol_, price, amount)
            print(price, amount)
            order = client.order_limit_buy(
                symbol=symbol_,
                quantity=amount,
                price=price
            )

        else:
            price, amount = get_sell_info(client, symbol_, price, amount)
            print(amount)
            order = client.order_limit_sell(
                symbol=symbol_,
                quantity=amount,
                price=price,
            )
        print(price, amount)
    except Exception as e:
        print("order exception", e)
    return order


def getStatusOrder(client, symbol_, orderId_):
    res = None
    while True:
        currentOrder = client.get_order(symbol=symbol_, orderId=orderId_)
        if currentOrder['status'] == 'FILLED':
            res = currentOrder['executedQty']
            break
        time.sleep(10)
    print(res)
    return res


def handleTrade(client, capital, triplet, data, way):
    res = None
    try:
        a1 = data[triplet[0]]
        a2 = data[triplet[1]]
        a3 = data[triplet[2]]
        if way == 'way1':
            side = 'buy'
            symbol_ = triplet[0]
            fee = capital * 0.1/100
            amount = capital - fee
            price = float(a1["b"])
            order = sendLmtOrder(client, side, symbol_, amount, price)
            capital = getStatusOrder(client, symbol_, order['orderId'])

            side = 'buy'
            symbol_ = triplet[1]
            fee = capital * 0.1/100
            amount = capital - fee
            price = float(a2["b"])
            order = sendLmtOrder(client, side, symbol_, amount, price)
            capital = getStatusOrder(client, symbol_, order['orderId'])

            side = 'sell'
            symbol_ = triplet[2]
            fee = capital * 0.1/100
            amount = capital - fee
            price = float(a3["a"])
            order = sendLmtOrder(client, side, symbol_, amount, price)
            capital = getStatusOrder(client, symbol_, order['orderId'])

            res = capital

        elif way == 'way2':
            print(way)
            side = 'buy'
            symbol_ = triplet[0]
            fee = capital * 0.1/100
            amount = capital - fee
            price = float(a3["b"])
            order = sendLmtOrder(client, side, symbol_, amount, price)
            capital = getStatusOrder(client, symbol_, order['orderId'])

            side = 'sell'
            symbol_ = triplet[1]
            fee = capital * 0.1/100
            amount = capital - fee
            price = float(a2["a"])
            order = sendLmtOrder(client, side, symbol_, amount, price)
            capital = getStatusOrder(client, symbol_, order['orderId'])

            side = 'sell'
            symbol_ = triplet[2]
            fee = capital * 0.1/100
            amount = capital - fee
            price = float(a1["a"])
            order = sendLmtOrder(client, side, symbol_, amount, price)
            capital = getStatusOrder(client, symbol_, order['orderId'])

            res = capital
    except:
        pass

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

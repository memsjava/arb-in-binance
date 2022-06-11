# arb-in-binance
Crypto arbitrage only in binance

## Installation
1. clone this repo
```bash
git clone 'https://github.com/memsjava/arb-in-binance.git'
```
2. install requirement.
```bash
py install -r requirements.txt
```
3. sign up and get your api key in binance exchange
4. update the setting file
5. run

python main.py
```bash
start: USDT 50.0

DEXEUSDT : 8.53846153846154 @ 5.85

DEXEBUSD  : 50.1559476923077 @ 5.88

USDT  : 50.10078116544093 @ 0.9999

way2: 0.20156233088185616%
```

## Example:
way2 means 

buy DEXE from USDT => 
sell DEXE to BUSD  => 
and sell BSUD to USDT 

begin with 50usdt and end with 50.1 usdt. You get 0.2% of your 50 usdt. Enjoy :)
the order will wait as we use limit order so be carefull.

## Binance orders error:
1. To avoid Failures in order, we have to respect all filters like bellow:  
```
    'filters': [
        {'filterType': 'PRICE_FILTER', 'minPrice': '0.01000000', 'maxPrice': '10000.00000000', 'tickSize': '0.01000000'}, 
        {'filterType': 'PERCENT_PRICE', 'multiplierUp': '5', 'multiplierDown': '0.2', 'avgPriceMins': 5}, 
        {'filterType': 'LOT_SIZE', 'minQty': '0.01000000', 'maxQty': '90000.00000000', 'stepSize': '0.01000000'}, 
        {'filterType': 'MIN_NOTIONAL', 'minNotional': '10.00000000', 'applyToMarket': True, 'avgPriceMins': 5}, 
        {'filterType': 'ICEBERG_PARTS', 'limit': 10}, 
        {'filterType': 'MARKET_LOT_SIZE', 'minQty': '0.00000000', 'maxQty': '5545.10094641', 'stepSize': '0.00000000'}, 
        {'filterType': 'TRAILING_DELTA', 'minTrailingAboveDelta': 10, 'maxTrailingAboveDelta': 2000, 'minTrailingBelowDelta': 10,'maxTrailingBelowDelta': 2000}, 
        {'filterType': 'MAX_NUM_ORDERS', 'maxNumOrders': 200}, 
        {'filterType': 'MAX_NUM_ALGO_ORDERS', 'maxNumAlgoOrders': 5}],
```
2. In case you have error, your have to continue manually. 
Check the sqlite database to see the pairs and price and whether buy/sell

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

## Example explanation:
way2 means 

buy DEXE from USDT => 
sell DEXE to BUSD  => 
and sell BSUD to USDT 

begin with 50usdt and end with 50.1 usdt. You get 0.2% of your 50 usdt. Enjoy :)
the order will wait as we use limit order so be carefull.
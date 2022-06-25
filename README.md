# arb-in-binance
Crypto arbitrage only in binance

## Installation
1. clone this repo
```bash
git clone 'https://github.com/memsjava/arb-in-binance.git'
```
2. install requirement.
```bash
pip install -r requirements.txt
```
3. sign up and get your api key in binance exchange
4. update the json setting file

- "API_PUBLIC": "",     // your api key
-  "API_SECRET": "",    // your secret api key
- "start_coin": "USDT", // base coin 
- "interest": 0.3,      // minimum interest per arb. Sometimes there is dust
- "live_trade": true,   // true or false
- "capital": ""         // "" if you want to use balance of base coin above, or put any amount.

5. run

```bash
python main.py

start: USDT 50.0
DEXEUSDT : 8.53846153846154 @ 5.85
DEXEBUSD  : 50.1559476923077 @ 5.88
USDT  : 50.10078116544093 @ 0.9999
way2: 0.20156233088185616%
```

## Output:
The output will be 2 ways :


1- way1: buy -> buy -> sell

2- way2: buy -> sell -> sell

example:
Buy DEXE from USDT => 
sell DEXE to BUSD  => 
sell BSUD to USDT 

begin with 50usdt and end with 50.1 usdt. You get 0.2% of your 50 usdt. Enjoy :)
the order will wait as we use limit order so be carefull.


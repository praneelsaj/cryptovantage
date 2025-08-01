import os
import ccxt
from dotenv import load_dotenv

load_dotenv()
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

# Initialize Binance exchange
exchange = ccxt.binanceus({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET_KEY,
})

# Retrieve account balances
try:
    balance = exchange.fetch_balance()
    print("Account balances (BTC and ETH only):")
    for asset in ['BTC', 'ETH']:
        amount = balance['total'].get(asset)
        if amount is not None and amount > 0:
            print(f"{asset}: {amount}")
        else:
            print(f"{asset}: 0")
except Exception as e:
    print("Could not fetch account balances:", e)

# Retrieve live market prices for BTC and ETH (USD)
try:
    btc_ticker = exchange.fetch_ticker('BTC/USDT')
    eth_ticker = exchange.fetch_ticker('ETH/USDT')
    print(f"Bitcoin price (BTC/USDT): ${btc_ticker['last']}")
    print(f"Ethereum price (ETH/USDT): ${eth_ticker['last']}")
except Exception as e:
    print("Could not fetch market prices:", e)


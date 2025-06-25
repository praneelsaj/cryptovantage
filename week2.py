import ccxt

api_key="RvsiWCgdichqRk6oVcUSKxJEsOZoDHhH3QwItRanHtRES0Ss18ARuH09fP6ejL4A"
secret_key="iv29pxso7pW1RSuQBNWmfplXIk5uRCvpz8cSbEb1nGVBpwOJJMwwkFTSanSsr6e3"

# Create a new instance of the ccxt binanceus class
exchange = ccxt.binanceus({
    'apiKey': api_key,
    'secret': secret_key,
})
# Fetch the current price of LTC/BTC
symbol = 'LTC/BTC'
ticker = exchange.fetch_ticker(symbol)
# Print the current price
print(f"The current price of {symbol} is {ticker['last']}")
# Fetch and print account balance
balance = exchange.fetch_balance()
# Get the LTC and BTC balances from the account
ltc_balance = balance['total'].get('LTC', 0)
btc_balance = balance['total'].get('BTC', 0)
print(f"LTC balance: {ltc_balance}")
print(f"BTC balance: {btc_balance}")
# Get the USD balance from the account
# Note: The balance may not be available in USD, so we check for its presence
usd_balance = balance['total'].get('USD', 0)
print(f"USD balance: {usd_balance}")

# Fetch and print live market prices for ETH/USD and BTC/USD
symbols = ['ETH/USD', 'BTC/USD']
for sym in symbols:
    try:
        ticker = exchange.fetch_ticker(sym)
        print(f"The current price of {sym} is {ticker['last']}")
    except Exception as e:
        print(f"Could not fetch price for {sym}: {e}")

# Print all available balances (non-zero)
print("Account balances:")
for coin, amount in balance['total'].items():
    if amount and amount != 0:
        print(f"{coin}: {amount}")

# Example: Place a market buy order for 0.001 BTC (uncomment to use)
# order = exchange.create_market_buy_order('BTC/USD', 0.001)
# print("Buy order result:", order)

# Example: Place a market sell order for 0.001 BTC (uncomment to use)
# order = exchange.create_market_sell_order('BTC/USD', 0.001)
# print("Sell order result:", order)

# Example: Withdraw (uncomment and fill in address and amount to use)
# withdrawal = exchange.withdraw('BTC', 0.001, 'your_btc_address_here')
# print("Withdrawal result:", withdrawal)

# Example: Deposit address (fetch deposit address for BTC)
# deposit_address = exchange.fetch_deposit_address('BTC')
# print("BTC deposit address:", deposit_address['address'])

# Simulate market buy and sell orders (no real orders placed)
def simulate_market_order(order_type, symbol, amount):
    print(f"Simulating {order_type} order for {amount} {symbol.split('/')[0]} at market price...")
    try:
        ticker = exchange.fetch_ticker(symbol)
        price = ticker['last']
        if order_type == 'buy':
            cost = amount * price
            print(f"Would BUY {amount} {symbol.split('/')[0]} at {price} {symbol.split('/')[1]} (Total cost: {cost} {symbol.split('/')[1]})")
        elif order_type == 'sell':
            proceeds = amount * price
            print(f"Would SELL {amount} {symbol.split('/')[0]} at {price} {symbol.split('/')[1]} (Total proceeds: {proceeds} {symbol.split('/')[1]})")
        else:
            print("Unknown order type.")
    except Exception as e:
        print(f"Simulation failed: {e}")

# Simulate a market buy order for 0.01 LTC
simulate_market_order('buy', 'LTC/USD', 0.01)

# Simulate a market sell order for 0.01 LTC
simulate_market_order('sell', 'LTC/USD', 0.01)

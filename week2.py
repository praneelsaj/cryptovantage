import ccxt

api_key="oGH1SeQzUhNWAJe7sYWNdUWIKVkzo5L45kFcGJuPxrjaSgqIBfD6bxba9TUkxEPB"
secret_key="SEgi5MWboiJiDkgOjyXqPvdez9lhd9M635YfKHOKnlbrqvjjVfa55tGOK2RVSKsT"

exchange = ccxt.binanceus({
    'apiKey': api_key,
    'secret': secret_key,
})



balance = exchange.fetch_balance()

print("Account balances:")
for coin, amount in balance['total'].items():
    if amount and amount != 0:
        print(f"{coin}: {amount}")
# nothing shows up; unsure if intentional so, just added these to be sure
# ltc and btc balance
eth_balance = balance['total'].get('ETH', 0)
btc_balance = balance['total'].get('BTC', 0)
print(f"ETH balance: {eth_balance}")
print(f"BTC balance: {btc_balance}")
#balance in usd
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

# Initialize balance
sim_balance = 500
trade_amount = 20

# Simulated ticker data
ticker = {'symbol': 'BTC', 'last': 9500}
ticker2 = {'symbol': 'ETH', 'last': 2200}

# Function to simulate a trade decision
def simulate_trade(ticker_data, threshold):
    global sim_balance
    symbol = ticker_data['symbol']
    price = ticker_data['last']

    if price < threshold:
        print(f"Buying ${trade_amount} of {symbol}")
        sim_balance -= trade_amount
    elif price > threshold:
        print(f"Selling ${trade_amount} of {symbol}")
        sim_balance += trade_amount
    else:
        print(f"Holding {symbol}, price is at threshold")

# Display initial balance
print(f"Initial Balance: ${sim_balance}")

# Run trade simulations
simulate_trade(ticker, 10500)
simulate_trade(ticker2, 2000)

# Display updated balance
print(f"Post-Trade Balance: ${sim_balance}")

# Withdraw all funds
print("Withdrawing balance from account...")
sim_balance = 0
print(f"Final Balance: ${sim_balance}")

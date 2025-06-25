import ccxt

api_key="RvsiWCgdichqRk6oVcUSKxJEsOZoDHhH3QwItRanHtRES0Ss18ARuH09fP6ejL4A"
secret_key="iv29pxso7pW1RSuQBNWmfplXIk5uRCvpz8cSbEb1nGVBpwOJJMwwkFTSanSsr6e3"

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


#buy
#buy_order = exchange.create_market_buy_order('BTC/USD', 0.001)
#print("Buy order result:", buy_order)

#sell
#sell_order = exchange.create_market_sell_order('BTC/USD', 0.001)
#print("Sell order result:", sell_order)



#withdraw
# withdrawal = exchange.withdraw('BTC', 0.001, 'your_btc_address_here')
# print("Withdrawal result:", withdrawal)


#deposit
#address = exchange.get_deposit_address(coin='BTC')
#deposit_address = exchange.fetch_deposit_address('BTC')
#print("BTC deposit address:", deposit_address['address'])

#simulation
def simulate_market_order(order_type, symbol, amount):
    print(f"Simulating {order_type} order for {amount} {symbol.split('/')[0]} at market price...")
    try:
        #asks for binance for latest price info for the trading pair
        ticker = exchange.fetch_ticker(symbol)
        #last is the latest price
        price = ticker['last']
        #buy
        if order_type == 'buy':
            cost = amount * price
            print(f"Would BUY {amount} {symbol.split('/')[0]} at {price} {symbol.split('/')[1]} (Total cost: {cost} {symbol.split('/')[1]})")
        #sell
        elif order_type == 'sell':
            proceeds = amount * price
            print(f"Would SELL {amount} {symbol.split('/')[0]} at {price} {symbol.split('/')[1]} (Total proceeds: {proceeds} {symbol.split('/')[1]})")
        else:
            print("Unknown order type.")
    #error
    except Exception as e:
        print(f"Simulation failed: {e}")

# simulated buy for ETH
simulate_market_order('buy', 'ETH/USD', 0.001)

# simulated sell for ETH
simulate_market_order('sell', 'ETH/USD', 0.001)

# simulated buy for BTC
simulate_market_order('buy', 'BTC/USD', 0.001)
# simulated sell for BTC
simulate_market_order('sell', 'BTC/USD', 0.001)

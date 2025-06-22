import ccxt
import transformers
import vaderSentiment
import pandas
import numpy
import python
import dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Connect to Binance
    binance = ccxt.binance({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,  # helps prevent hitting rate limits
    })

    # Load markets (required before many operations)
    binance.load_markets()

    # 1. Retrieve account balances
    try:
        balances = binance.fetch_balance()
        logging.info("Account Balances:")
        for currency, balance in balances['total'].items():
            if balance > 0:
                logging.info(f"{currency}: {balance}")
    except Exception as e:
        logging.error(f"Error fetching balances: {e}")

    # 2. Retrieve live market prices (ticker)
    symbol = 'BTC/USDT'  # Example trading pair
    try:
        ticker = binance.fetch_ticker(symbol)
        last_price = ticker['last']
        logging.info(f"Current {symbol} price: {last_price} USDT")
    except Exception as e:
        logging.error(f"Error fetching ticker: {e}")

    # 3. Simulate market orders
    # Note: We won't place real orders here; just simulate order creation & log it.
    def simulate_market_order(side, amount, symbol):
        logging.info(f"Simulating {side.upper()} order for {amount} {symbol}")
        # Here you could add checks or pretend to send order
        # Just logging to confirm simulation
        logging.info(f"{side.capitalize()} order for {amount} {symbol} simulated successfully.")

    simulate_market_order('buy', 0.001, symbol)
    simulate_market_order('sell', 0.001, symbol)

if __name__ == "__main__":
    main()

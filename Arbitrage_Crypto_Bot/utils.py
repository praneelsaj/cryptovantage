import pandas as pd
import ccxt

# Trading thresholds by coin
thresholds = {
    "BTC": {"buy_dip": -0.8, "sell_gain": 0.8, "pos_sent": 0.5, "neg_sent": 0.3},
    "ETH": {"buy_dip": -1.0, "sell_gain": 1.0, "pos_sent": 0.25, "neg_sent": -0.4}
}

# Sentiment classification logic
def classify_sentiment(score, coin):
    t = thresholds.get(coin, thresholds["BTC"])
    if score == 0:
        return "Neutral"
    elif score > t["pos_sent"]:
        return "Positive"
    elif score < t["neg_sent"]:
        return "Negative"
    return "Neutral"

# Binance price fetch with fallback
exchange = ccxt.binanceus()

def get_price_with_fallback(symbol, date_str):
    try:
        since = pd.to_datetime(date_str).tz_localize('UTC')
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', since=int(since.timestamp() * 1000), limit=4)
        closes = [row[4] for row in ohlcv]
        if len(closes) >= 3:
            return closes[-3], closes[-2], closes[-1]
    except Exception:
        return None, None, None
    return None, None, None

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from news.news import fetch_rss_articles
from logs.logger import setup_logger
from utils.helpers import classify_sentiment, get_price_with_fallback, thresholds

setup_logger()

# Fetch and combine news from feeds
feeds = [
    "https://www.coindesk.com/arc/outboundfeeds/rss",
    "https://cointelegraph.com/rss"
]
all_articles = []
for url in feeds:
    all_articles.extend(fetch_rss_articles(url, limit=20))

csv_path = os.path.join(os.path.dirname(__file__), "every_summarized_news.csv")
try:
    existing_df = pd.read_csv(csv_path)
    new_df = pd.DataFrame(all_articles)
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df.to_csv(csv_path, index=False)
except FileNotFoundError:
    pd.DataFrame(all_articles).to_csv(csv_path, index=False)

# Load data and aggregate sentiment
df = pd.read_csv(csv_path)
avg_df = df.groupby(["timestamp", "coin"], as_index=False)["sentiment_score"].mean()
avg_df = avg_df.rename(columns={"sentiment_score": "avg_sentiment_score"})
avg_df["sentiment_class"] = avg_df.apply(
    lambda row: classify_sentiment(row["avg_sentiment_score"], row["coin"]), axis=1
)
avg_df.to_csv("averaged_sentiment_by_date_coin.csv", index=False)

# Generate signals
results = []
for _, row in avg_df.iterrows():
    date = pd.to_datetime(row["timestamp"], errors="coerce").strftime("%Y-%m-%d")
    coin = row["coin"]
    symbol = "BTC/USDT" if coin == "BTC" else "ETH/USDT"
    sentiment_class = row["sentiment_class"]
    prev_close, curr_close, next_close = get_price_with_fallback(symbol, date)
    t = thresholds.get(coin, thresholds["BTC"])
    if None in (prev_close, curr_close, next_close):
        action = "No price data"
        price_dip_pct, backtest_price_dip_pct = None, None
    else:
        price_dip_pct = ((curr_close - prev_close) / prev_close) * 100
        backtest_price_dip_pct = ((next_close - curr_close) / curr_close) * 100
        if price_dip_pct < t["buy_dip"] and sentiment_class == "Positive":
            action = "Buy"
        elif price_dip_pct > t["sell_gain"] and sentiment_class == "Negative":
            action = "Sell or Hold"
        else:
            action = "Hold / Monitor"
    results.append({
        "date": date,
        "coin": coin,
        "classification": sentiment_class,
        "price_dip_pct": price_dip_pct,
        "backtest_price_dip_pct": backtest_price_dip_pct,
        "action": action
    })

pd.DataFrame(results).to_csv("trade_signals.csv", index=False)

# Backtest signal quality
def backtest_signal_quality(csv_path, output_csv, start_date, end_date):
    signal_df = pd.read_csv(csv_path)
    signal_df["date"] = pd.to_datetime(signal_df["date"])
    signal_df = signal_df[(signal_df["date"] >= start_date) & (signal_df["date"] <= end_date)]
    all_dates = pd.date_range(start=start_date, end=end_date)
    full_index = pd.MultiIndex.from_product([all_dates, ["BTC", "ETH"]], names=["date", "coin"])
    signal_df.set_index(["date", "coin"], inplace=True)
    signal_df = signal_df.reindex(full_index, fill_value=np.nan).reset_index()
    signal_df["classification"].fillna("Neutral", inplace=True)
    signal_df["action"].fillna("Hold", inplace=True)
    signal_df["price_dip_pct"].fillna(0, inplace=True)

    balance = {"BTC": 500, "ETH": 500}
    score_log = []
    for _, row in signal_df.iterrows():
        date = row["date"].strftime("%Y-%m-%d")
        coin = row["coin"]
        action = row["action"]
        backtest_dip = row.get("backtest_price_dip_pct", 0)
        movement = "Up" if backtest_dip > 0 else "Down" if backtest_dip < 0 else "Flat"
        if action == "Buy":
            score = 20 if movement == "Up" else -20
        elif action == "Sell or Hold":
            score = 20 if movement == "Down" else -20
        else:
            score = 0
        balance[coin] += score
        score_log.append({
            "Date": date,
            "Coin": coin,
            "Market Movement": movement,
            "Decision": action,
            "Score": score,
            "New Balance": balance[coin]
        })
    pd.DataFrame(score_log).to_csv(output_csv, index=False)
    print(f"✅ Backtest scores saved to {output_csv}")

# Run backtest
backtest_signal_quality("trade_signals.csv", "signal_backtest_score.csv", "2025-07-01", "2025-07-25")

# Plot results
score_df = pd.read_csv("signal_backtest_score.csv")
score_df["Date"] = pd.to_datetime(score_df["Date"])
pivot_df = score_df.pivot(index="Date", columns="Coin", values="New Balance").ffill()

plt.figure(figsize=(10, 6))
plt.plot(pivot_df.index, pivot_df["BTC"], label="BTC Balance", color

# 📦 Module Imports
import os  # For path and file operations
import feedparser  # RSS feed parsing
import pandas as pd  # DataFrame handling
from transformers import pipeline  # Hugging Face pipeline for summarization
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # Sentiment scoring
import numpy as np  # Numerical operations
from dotenv import load_dotenv  # Environment variable loading
import logging  # Logging for diagnostics
import ccxt  # Crypto exchange interface
import matplotlib.pyplot as plt  # Visualization
import seaborn as sns  # Enhanced plot styling

# 🧾 Configure Logging
logging.basicConfig(filename="trade_signal.log", level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")

# 🧠 Load Summarization Model
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    print("❌ Failed to load summarizer:", e)
    summarizer = None

# 📰 Define RSS Feeds
feeds = [
    "https://www.coindesk.com/arc/outboundfeeds/rss",
    "https://cointelegraph.com/rss"
]

# 🔍 Keywords for filtering relevant articles
keywords = ["bitcoin", "btc", "ethereum", "eth"]

# 🪙 Determine coin symbol based on text content
def detect_coin(text):
    text = text.lower()
    if "ethereum" in text or "eth" in text:
        return "ETH"
    elif "bitcoin" in text or "btc" in text:
        return "BTC"
    else:
        return "UNKNOWN"

# 📝 Summarize news text using BART
def summarize_content(text):
    try:
        summary = summarizer(text[:1024], max_length=60, min_length=25, do_sample=False)[0]['summary_text']
    except Exception as e:
        summary = "Error summarizing: " + str(e)
    return summary

# 🔬 Initialize VADER Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

# 📊 Define dynamic thresholds for trading logic
thresholds = {
    "BTC": {"buy_dip": -0.8, "sell_gain": 0.8, "pos_sent": 0.5, "neg_sent": 0.3},
    "ETH": {"buy_dip": -1.0, "sell_gain": 1.0, "pos_sent": 0.25, "neg_sent": -0.4}
}

# 🗞️ Fetch and process articles from RSS feed
def fetch_rss_articles(feed_url, limit=20):
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries[:limit]:
        title = entry.get("title", "")
        content = entry.get("summary", "") or entry.get("description", "")
        full_text = f"{title} {content}"
        if any(k in full_text.lower() for k in keywords):
            coin = detect_coin(full_text)
            timestamp = entry.get("published", "")
            summary = summarize_content(full_text)
            sentiment_input = f"{title} {summary}"
            sentiment_score = analyzer.polarity_scores(sentiment_input)["compound"]
            articles.append({
                "timestamp": timestamp,
                "title": title,
                "coin": coin,
                "summary": summary,
                "sentiment_score": sentiment_score
            })
    return articles

# 🧹 Aggregate news from all feeds
all_articles = []
for url in feeds:
    all_articles.extend(fetch_rss_articles(url, limit=20))

# 💾 Save to CSV (append mode)
csv_path = os.path.join(os.path.dirname(__file__), "every_summarized_news.csv")
try:
    existing_df = pd.read_csv(csv_path)
    new_df = pd.DataFrame(all_articles)
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df.to_csv(csv_path, index=False)
except FileNotFoundError:
    pd.DataFrame(all_articles).to_csv(csv_path, index=False)

# 📂 Load data for sentiment averaging
df = pd.read_csv(csv_path)

# 📈 Calculate average sentiment score per day and coin
avg_df = (
    df.groupby(["timestamp", "coin"], as_index=False)["sentiment_score"]
    .mean()
    .rename(columns={"sentiment_score": "avg_sentiment_score"})
)

# 💾 Save sentiment averages
avg_csv_path = os.path.join(os.path.dirname(__file__), "averaged_sentiment_by_date_coin.csv")
avg_df.to_csv(avg_csv_path, index=False)
print("Averaged sentiment scores saved to:", avg_csv_path)

# 🧮 Load averaged data for classification
avg_df = pd.read_csv(avg_csv_path)

# 🟦 Classify sentiment into Positive / Neutral / Negative
def classify_sentiment(score, coin):
    t = thresholds.get(coin, thresholds["BTC"])
    if score == 0:
        return "Neutral"
    elif score > t["pos_sent"]:
        return "Positive"
    elif score < t["neg_sent"]:
        return "Negative"
    else:
        return "Neutral"

avg_df["sentiment_class"] = avg_df.apply(
    lambda row: classify_sentiment(row["avg_sentiment_score"], row["coin"]), axis=1
)

# 🧑‍💻 Initialize BinanceUS for price fetching
exchange = ccxt.binanceus()

# 📉 Get historical close prices with fallback
def get_price_with_fallback(symbol, date_str):
    try:
        since = pd.to_datetime(date_str).tz_localize('UTC')
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', since=int(since.timestamp() * 1000), limit=4)
        closes = [row[4] for row in ohlcv]
        if len(closes) >= 3:
            return closes[-3], closes[-2], closes[-1]  # prev, curr, next
        else:
            return None, None, None
    except Exception as e:
        logging.error(f"Price fetch error for {symbol} on {date_str}: {e}")
        return None, None, None

# 📤 Generate trade signals
results = []
for _, row in avg_df.iterrows():
    timestamp = pd.to_datetime(row["timestamp"], errors="coerce")
    if pd.isnull(timestamp):
        logging.warning(f"Invalid timestamp: {row['timestamp']}")
        continue
    date = timestamp.strftime("%Y-%m-%d")
    coin = row["coin"]
    sentiment_class = row["sentiment_class"]
    symbol = "BTC/USDT" if coin == "BTC" else "ETH/USDT"
    try:
        prev_close, curr_close, next_close = get_price_with_fallback(symbol, date)
        t = thresholds.get(coin, thresholds["BTC"])
        if None in (prev_close, curr_close, next_close):
            price_dip_pct = None
            backtest_price_dip_pct = None
            action = "No price data"
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
        logging.info(f"{date} {coin}: {sentiment_class}, dip {price_dip_pct}, action {action}")
    except Exception as e:
        logging.error(f"Error processing {date} {coin}: {e}")

# 💾 Save trade signals to CSV
trade_csv_path = os.path.join(os.path.dirname(__file__), "trade_signals.csv")
pd.DataFrame(results).to_csv(trade_csv_path, index=False)
print("Trade signals saved to:", trade_csv_path)

# 🔁 Backtesting signal accuracy
def backtest_signal_quality(csv_path, output_csv="signal_backtest_score.csv", start_date="2025-07-01", end_date="2025-07-25"):
    signal_df = pd.read_csv(csv_path)
    signal_df["date"] = pd.to_datetime(signal_df["date"])
    signal_df = signal_df[(signal_df["date"] >= start_date) & (signal_df["date"] <= end_date)]
    all_dates = pd.date_range(start=start_date, end=end_date)
    coin_list = ["BTC", "ETH"]
    full_index = pd.MultiIndex.from_product([all_dates, coin_list], names=["date", "coin"])
    signal_df.set_index(["date", "coin"], inplace=True)
    signal_df = signal_df.reindex(full_index, fill_value=np.nan).reset_index()
    signal_df["classification"].fillna("Neutral", inplace=True)
    signal_df["action"].fillna("Hold", inplace=True)
    signal_df["price_dip_pct"].fillna(0, inplace=True)
    balance_tracker = {"BTC": 500, "ETH": 500}
    score_log = []

    # 🧮 Score signal effectiveness and track balances
    for _, row in signal_df.iterrows():
        date = row["date"].strftime("%Y-%m-%d")
        coin = row["coin"]
        sentiment = row["classification"]
        action = row["action"]
        backtest_dip = row.get("backtest_price_dip_pct", 0)

        # 🪙 Define market movement category
        market_movement = "Up" if backtest_dip > 0 else "Down" if backtest_dip < 0 else "Flat"

        # 🧠 Apply rule-based scoring based on action vs outcome
        if action == "Buy":
            score = 20 if market_movement == "Up" else -20
        elif action == "Sell or Hold":
            score = 20 if market_movement == "Down" else -20
        else:
            score = 0  # Hold / Monitor or no signal

        # 💰 Update simulated balance
        balance_tracker[coin] += score

        # 📜 Log results
        score_log.append({
            "Date": date,
            "Coin": coin,
            "Market Movement": market_movement,
            "Decision": action,
            "Score": score,
            "New Balance": balance_tracker[coin]
        })

    # 💾 Save the backtest results to CSV
    pd.DataFrame(score_log).to_csv(output_csv, index=False)
    print(f"✅ Backtest scores saved to {output_csv}")

# 🚀 Run the backtest function with defined date range
backtest_signal_quality(
    csv_path=trade_csv_path,
    output_csv="signal_backtest_score.csv",
    start_date="2025-07-01",
    end_date="2025-07-25"
)

# 📂 Load backtest results
score_df = pd.read_csv("signal_backtest_score.csv")
score_df["Date"] = pd.to_datetime(score_df["Date"])

# 🔁 Reshape data for time series plotting
pivot_df = score_df.pivot(index="Date", columns="Coin", values="New Balance")
pivot_df = pivot_df.ffill()  # Forward fill to handle missing days

# 📈 Plot balance evolution
plt.figure(figsize=(10, 6))
plt.plot(pivot_df.index, pivot_df["BTC"], label="BTC Balance", color="gold", marker='o')
plt.plot(pivot_df.index, pivot_df["ETH"], label="ETH Balance", color="purple", marker='s')

# 🖼️ Plot Visuals
plt.title("💰 BTC & ETH Signal Score Over Time")
plt.xlabel("Date")
plt.ylabel("Balance")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("btc_eth_score_over_time.png")  # 💾 Save chart as PNG
plt.show()  # 👀 Display chart)


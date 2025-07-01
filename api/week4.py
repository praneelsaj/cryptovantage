import pandas as pd
import feedparser
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize summarizer (using BART model)
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    print("❌ Failed to load summarizer:", e)
    summarizer = None

# Initialize sentiment analyzer (VADER)
analyzer = SentimentIntensityAnalyzer()

def fetch_rss_articles(feed_url, limit=5):
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries[:limit]:
        articles.append({
            "title": entry.get("title", ""),
            "content": entry.get("summary", "")
        })
    return articles

def summarize_text(text):
    if summarizer:
        try:
            result = summarizer(text[:1024], max_length=60, min_length=25, do_sample=False)
            return result[0]["summary_text"]
        except Exception as e:
            print("⚠️ Summarization failed:", e)
            return text
    return text

def analyze_sentiment(text):
    return analyzer.polarity_scores(text)["compound"]

def classify_sentiment(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def generate_trade_signal(label):
    if label == "Positive":
        return "Consider Buying"
    elif label == "Negative":
        return "Reduce Exposure / Avoid Entry"
    else:
        return "Hold / Monitor"

# Example RSS feeds
feeds = [
    "https://www.coindesk.com/markets/2025/06/30/bitcoin-carries-crypto-markets-in-2025s-first-half-as-altcoins-crumble-whats-next",
    "https://cointelegraph.com/news/bitcoin-new-all-time-high-now-inevitable-btc-price-liquidity-109k"
]

# Pull and process articles
all_articles = []
for feed_url in feeds:
    all_articles.extend(fetch_rss_articles(feed_url, limit=3))

df = pd.DataFrame(all_articles)
df["summary"] = df["content"].apply(summarize_text)
df["compound"] = df["summary"].apply(analyze_sentiment)
df["sentiment_label"] = df["compound"].apply(classify_sentiment)
df["trade_signal"] = df["sentiment_label"].apply(generate_trade_signal)
df["timestamp"] = pd.Timestamp.now().isoformat()

df.to_csv("crypto_news_recommendations.csv", index=False)
print("✅ Sentiment analysis and trade signals saved to crypto_news_recommendations.csv")

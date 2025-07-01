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
    """
    Parses articles from the given RSS feed URL.
    Returns a list of dicts with 'title' and 'content'.
    """
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries[:limit]:
        articles.append({
            "title": entry.get("title", ""),
            "content": entry.get("summary", "")  # Use 'description' if needed
        })
    return articles

def summarize_text(text):
    """
    Summarizes input text using a pretrained transformer model.
    Falls back to original text if summarizer is unavailable or fails.
    """
    if summarizer:
        try:
            result = summarizer(text[:1024], max_length=60, min_length=25, do_sample=False)
            return result[0]["summary_text"]
        except Exception as e:
            print("⚠️ Summarization failed:", e)
            return text
    return text

def analyze_sentiment(text):
    """
    Returns the compound sentiment score using VADER.
    """
    return analyzer.polarity_scores(text)["compound"]
# Example RSS feeds
feeds = [
    "https://www.coindesk.com/markets/2025/06/30/bitcoin-carries-crypto-markets-in-2025s-first-half-as-altcoins-crumble-whats-next",
    "https://cointelegraph.com/news/bitcoin-new-all-time-high-now-inevitable-btc-price-liquidity-109k"
]

# Pull and combine articles
all_articles = []
for feed_url in feeds:
    all_articles.extend(fetch_rss_articles(feed_url, limit=3))

# Create DataFrame
df = pd.DataFrame(all_articles)

# Summarize and analyze
df["summary"] = df["content"].apply(summarize_text)
df["sentiment"] = df["summary"].apply(analyze_sentiment)
df["timestamp"] = pd.Timestamp.now().isoformat()

# Save to CSV
df.to_csv("crypto_news_summary.csv", index=False)
print("✅ Pulled live crypto news, summarized, and saved to crypto_news_summary.csv")

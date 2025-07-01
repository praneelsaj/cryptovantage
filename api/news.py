from utils import fetch_rss_articles, summarize_text, analyze_sentiment
import pandas as pd

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

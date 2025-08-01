import feedparser
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

keywords = ["bitcoin", "btc", "ethereum", "eth"]

# Try loading the BART summarizer
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception:
    summarizer = None

analyzer = SentimentIntensityAnalyzer()

def detect_coin(text):
    text = text.lower()
    if "ethereum" in text or "eth" in text:
        return "ETH"
    elif "bitcoin" in text or "btc" in text:
        return "BTC"
    return "UNKNOWN"

def summarize_content(text):
    try:
        return summarizer(text[:1024], max_length=60, min_length=25, do_sample=False)[0]['summary_text']
    except Exception as e:
        return "Error summarizing: " + str(e)

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

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

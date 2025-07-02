#for making and managing data frame
import pandas as pd
#for looking over RSS feeds
import feedparser
#to load a pre-trained summarization model
from transformers import pipeline
#providing sentiment scores based off of the text
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# initializes summarization; uzes BART model by META that's trained off of CNN articles
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    print("Failed to load summarizer:", e)
    summarizer = None

#initializes sentiment analyzer (VADER)
analyzer = SentimentIntensityAnalyzer()

def fetch_rss_articles(feed_url, limit=5):
    """
    parses articles from the given RSS feed URL.
    returns a list of dictionaries with 'title' and 'content'.
    loops through the first limit entries, and adds their title and summary content to a list.
    """
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries[:limit]:
        articles.append({
            "title": entry.get("title", ""),
            "content": entry.get("summary", "")
        })
    return articles

def summarize_text(text):
    """
    summarizes input text using a pretrained transformer model.
    falls back to original text if summarizer is unavailable or fails.
    """
    if summarizer:
        try:
            #1024 is BART max limit for text (truncates if exceeding); lengths are for summarizers (25-60 is generally sufficient), do_sample=False keeps deterministic output
            result = summarizer(text[:1024], max_length=60, min_length=25, do_sample=False)
            return result[0]["summary_text"]
        except Exception as e:
            print("Summarization failed:", e)
            return text
    return text

def analyze_sentiment(text):
    """
    returns the compound sentiment score (-1 to 1) using VADER.
    """
    return analyzer.polarity_scores(text)["compound"]
#-0.05 - 0.05 is neutral, below -0.05 (-0.05 to -1) is negative, above 0.05 (0.05 to 1) is positive
def classify_sentiment(score):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"
#
def generate_trade_signal(label):
    if label == "Positive":
        return "Consider Buying"
    elif label == "Negative":
        return "Reduce Exposure / Avoid Entry"
    else:
        return "Hold / Monitor"

#example RSS feeds
feeds = [
    "https://www.coindesk.com/arc/outboundfeeds/rss",
    "https://cointelegraph.com/rss"
]

#pull and combine articles; gets 3 articles
all_articles = []
for feed_url in feeds:
    all_articles.extend(fetch_rss_articles(feed_url, limit=3))

#creates dataframe
df = pd.DataFrame(all_articles)

#sumarize and analyze; sentiment meaning and trade signal/action; timestamp in isoformat (YYYY)
df["summary"] = df["content"].apply(summarize_text)
df["compound"] = df["summary"].apply(analyze_sentiment)
df["sentiment_label"] = df["compound"].apply(classify_sentiment)
df["trade_signal"] = df["sentiment_label"].apply(generate_trade_signal)
df["timestamp"] = pd.Timestamp.now().isoformat()

#saves to csv
df.to_csv("crypto_news_recommendations.csv", index=False)
print("Sentiment analysis and trade signals saved to crypto_news_recommendations.csv")

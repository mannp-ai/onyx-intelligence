import yfinance as yf
from textblob import TextBlob
import datetime

def fetch_and_analyze_news(ticker: str) -> dict:
    """
    Fetches recent news headlines for the given ticker using yfinance.
    Analyzes the sentiment of each headline using TextBlob.
    Returns an aggregated sentiment score and a list of headlines.
    """
    try:
        # Using yf.Search is much faster and thread-safe for news than calling yf.Ticker() concurrently
        search = yf.Search(ticker, max_results=10)
        news_items = search.news
        
        if not news_items:
            # Fallback to Ticker if Search fails
            stock = yf.Ticker(ticker)
            news_items = stock.news
            
        if not news_items:
            return {
                "sentiment_label": "Neutral",
                "average_polarity": 0.0,
                "headlines": ["No recent news found for this company."]
            }

        analyzed_headlines = []
        total_polarity = 0.0
        
        # Analyze up to the top 10 recent articles
        for item in news_items[:10]:
            content = item.get("content", item)
            title = content.get("title", "")
            if not title:
                continue
                
            # Perform Lexical Sentiment Analysis
            blob = TextBlob(title)
            # Polarity ranges from -1.0 (Highly Negative) to 1.0 (Highly Positive)
            polarity = blob.sentiment.polarity
            total_polarity += polarity
            
            # Format date if available
            pub_date = "Recent"
            if "pubDate" in content:
                pub_date = content["pubDate"][:10]
            elif "providerPublishTime" in item:
                dt = datetime.datetime.fromtimestamp(item["providerPublishTime"])
                pub_date = dt.strftime("%Y-%m-%d")
                
            link = content.get("canonicalUrl", {}).get("url") or item.get("link", "#")
                
            analyzed_headlines.append({
                "title": title,
                "date": pub_date,
                "polarity": round(polarity, 2),
                "url": link
            })

        if not analyzed_headlines:
             return {
                "sentiment_label": "Neutral",
                "average_polarity": 0.0,
                "headlines": ["Could not parse news headlines."]
            }

        # Calculate Average Polarity
        avg_polarity = total_polarity / len(analyzed_headlines)
        
        # Determine Label based on Aggregated Score
        if avg_polarity > 0.15:
            label = "Bullish"
        elif avg_polarity < -0.15:
            label = "Bearish"
        else:
            label = "Neutral"

        return {
            "sentiment_label": label,
            "average_polarity": round(avg_polarity, 2),
            "headlines": analyzed_headlines
        }

    except Exception as e:
        print(f"Error analyzing news for {ticker}: {e}")
        return {
            "sentiment_label": "Unknown",
            "average_polarity": 0.0,
            "headlines": [f"Error fetching news: {str(e)}"]
        }

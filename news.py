from newsapi import NewsApiClient
from dotenv import load_dotenv
import os, json
from datetime import datetime, timedelta
from utils import speak

today = datetime.today()
yesterday = today - timedelta(days=1)
today = today.strftime('%Y-%m-%d')
yesterday = yesterday.strftime('%Y-%m-%d')

load_dotenv("config.env")
API_KEY = os.getenv("NEWS_API")
newsapi = NewsApiClient(api_key=API_KEY)

CACHE_FILE = "news_cache.json"

def get_headlines(n: int = 10) -> list[str]:
    try:
        all_articles = newsapi.get_everything(
            q='india',
            from_param=yesterday,
            to=today,
            language='en',
            sort_by='popularity',
        )
        news = [article["title"] for article in all_articles["articles"][:n]]

        # Save to cache
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"news": news, "timestamp": datetime.now().isoformat()}, f)

        for i, headline in enumerate(news, start=1):
            speak(f"Headline {i}: {headline}")

        return news
    except Exception:
        # If offline or API fails, load cached news
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
            return cached.get("news", ["No news available."])
        else:
            return ["No news available."]
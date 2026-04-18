import feedparser
from typing import List, Dict


def fetch_articles(sources: List[Dict]) -> List[Dict]:
    articles = []
    for source in sources:
        try:
            feed = feedparser.parse(source["rss"])
            if feed.bozo and not feed.entries:
                print(f"[SKIP] {source['name']}: {feed.bozo_exception}")
                continue
            for entry in feed.entries:
                articles.append({
                    "title": entry.title,
                    "url": entry.link,
                    "content": entry.get("summary", entry.get("description", "")),
                    "source": source["name"],
                })
        except Exception as e:
            print(f"[ERROR] {source['name']}: {e}")
    return articles

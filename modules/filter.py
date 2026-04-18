from typing import List, Dict
from modules.db import Database


def filter_articles(articles: List[Dict], keywords: List[str], db: Database) -> List[Dict]:
    seen_urls = set()
    result = []
    for article in articles:
        url = article["url"]
        if url in seen_urls or db.is_sent(url):
            continue
        text = (article["title"] + " " + article["content"]).lower()
        if any(kw.lower() in text for kw in keywords):
            seen_urls.add(url)
            result.append(article)
    return result

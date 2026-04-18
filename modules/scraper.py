import logging

import feedparser
from typing import List, Dict

logger = logging.getLogger(__name__)


def fetch_articles(sources: List[Dict]) -> List[Dict]:
    articles = []
    for source in sources:
        try:
            feed = feedparser.parse(source["rss"])
            if feed.bozo and not feed.entries:
                logger.warning("[SKIP] %s: %s", source['name'], feed.bozo_exception)
                continue
            for entry in feed.entries:
                try:
                    articles.append({
                        "title": entry.title,
                        "url": entry.link,
                        "content": entry.get("summary", entry.get("description", "")),
                        "source": source["name"],
                    })
                except AttributeError:
                    continue
        except Exception as e:
            logger.error("[ERROR] %s: %s", source['name'], e)
    return articles

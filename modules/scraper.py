import logging
from calendar import timegm
from datetime import datetime, timezone

import feedparser
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def _parse_published(entry) -> Optional[datetime]:
    t = getattr(entry, "published_parsed", None)
    if t is None:
        return None
    try:
        return datetime.fromtimestamp(timegm(t), tz=timezone.utc)
    except Exception:
        return None


def fetch_articles(sources: List[Dict]) -> List[Dict]:
    articles = []
    for source in sources:
        try:
            feed = feedparser.parse(source["rss"])
            if feed.bozo and not feed.entries:
                logger.warning("[SKIP] %s: %s", source["name"], feed.bozo_exception)
                continue
            for entry in feed.entries:
                try:
                    articles.append({
                        "title": entry.title,
                        "url": entry.link,
                        "content": entry.get("summary", entry.get("description", "")),
                        "source": source["name"],
                        "published_at": _parse_published(entry),
                    })
                except AttributeError:
                    continue
        except Exception as e:
            logger.error("[ERROR] %s: %s", source["name"], e)
    return articles

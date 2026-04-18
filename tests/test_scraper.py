# tests/test_scraper.py
import pytest
from unittest.mock import patch, MagicMock
from modules.scraper import fetch_articles

MOCK_ENTRY = MagicMock()
MOCK_ENTRY.title = "Google Core Update April 2026"
MOCK_ENTRY.link = "https://searchengineland.com/google-core-update-april"
MOCK_ENTRY.get.return_value = "Google released a major core update..."
MOCK_ENTRY.published = "Sat, 18 Apr 2026 08:00:00 +0000"

MOCK_FEED = MagicMock()
MOCK_FEED.entries = [MOCK_ENTRY]
MOCK_FEED.bozo = False

def test_fetch_articles_returns_list():
    sources = [{"name": "SEL", "rss": "https://searchengineland.com/feed"}]
    with patch("modules.scraper.feedparser.parse", return_value=MOCK_FEED):
        articles = fetch_articles(sources)
    assert isinstance(articles, list)
    assert len(articles) == 1

def test_fetch_articles_article_has_required_fields():
    sources = [{"name": "SEL", "rss": "https://searchengineland.com/feed"}]
    with patch("modules.scraper.feedparser.parse", return_value=MOCK_FEED):
        articles = fetch_articles(sources)
    article = articles[0]
    assert "title" in article
    assert "url" in article
    assert "content" in article
    assert "source" in article

def test_fetch_articles_skips_failed_feed():
    broken_feed = MagicMock()
    broken_feed.bozo = True
    broken_feed.bozo_exception = Exception("Connection failed")
    broken_feed.entries = []

    sources = [
        {"name": "Broken", "rss": "https://broken.com/feed"},
        {"name": "SEL", "rss": "https://searchengineland.com/feed"},
    ]
    with patch("modules.scraper.feedparser.parse", side_effect=[broken_feed, MOCK_FEED]):
        articles = fetch_articles(sources)
    assert len(articles) == 1
    assert articles[0]["source"] == "SEL"

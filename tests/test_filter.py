# tests/test_filter.py
import os
import pytest
from modules.db import Database
from modules.filter import filter_articles

TEST_DB = "data/test_filter.db"

KEYWORDS = ["seo", "google update", "algorithm", "ranking"]

ARTICLES = [
    {"title": "Google Core Algorithm Update 2026", "url": "https://a.com/1", "content": "...", "source": "SEL"},
    {"title": "Best Recipes for Summer", "url": "https://a.com/2", "content": "Cook pasta", "source": "Food"},
    {"title": "How to improve SEO rankings", "url": "https://a.com/3", "content": "...", "source": "MOZ"},
    {"title": "Google Update Confirmed", "url": "https://a.com/1", "content": "...", "source": "SEL"},  # ซ้ำ URL กับข้อ 1
]

@pytest.fixture(autouse=True)
def clean_db():
    os.makedirs("data", exist_ok=True)
    db = Database(TEST_DB)
    db.init()
    yield db
    db.close()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_filter_keeps_keyword_match(clean_db):
    result = filter_articles(ARTICLES[:1], KEYWORDS, clean_db)
    assert len(result) == 1

def test_filter_removes_no_keyword_match(clean_db):
    result = filter_articles(ARTICLES[1:2], KEYWORDS, clean_db)
    assert len(result) == 0

def test_filter_removes_already_sent(clean_db):
    clean_db.mark_sent("https://a.com/1", "Article 1")
    result = filter_articles(ARTICLES[:1], KEYWORDS, clean_db)
    assert len(result) == 0

def test_filter_removes_duplicate_in_batch(clean_db):
    # ข้อ 1 และข้อ 4 มี URL เดียวกัน ควรได้แค่ 1
    batch = [ARTICLES[0], ARTICLES[3]]
    result = filter_articles(batch, KEYWORDS, clean_db)
    assert len(result) == 1

def test_filter_returns_multiple_matches(clean_db):
    result = filter_articles([ARTICLES[0], ARTICLES[2]], KEYWORDS, clean_db)
    assert len(result) == 2

def test_filter_matches_keyword_in_content(clean_db):
    # keyword only in content, not in title
    article = {"title": "Summer Tips", "url": "https://a.com/99", "content": "improve your seo today", "source": "MOZ"}
    result = filter_articles([article], KEYWORDS, clean_db)
    assert len(result) == 1

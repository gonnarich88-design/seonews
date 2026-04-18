# tests/test_db.py
import os
import pytest
from modules.db import Database

TEST_DB = "data/test_history.db"

@pytest.fixture(autouse=True)
def clean_db():
    os.makedirs("data", exist_ok=True)
    db = Database(TEST_DB)
    db.init()
    yield db
    db.close()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_init_creates_table(clean_db):
    import sqlite3
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sent_articles'")
    assert cursor.fetchone() is not None
    conn.close()

def test_is_sent_returns_false_for_new_url(clean_db):
    assert clean_db.is_sent("https://example.com/article-1") is False

def test_mark_sent_and_is_sent(clean_db):
    url = "https://example.com/article-1"
    clean_db.mark_sent(url, "Article Title")
    assert clean_db.is_sent(url) is True

def test_mark_sent_duplicate_does_not_raise(clean_db):
    url = "https://example.com/article-1"
    clean_db.mark_sent(url, "Title")
    clean_db.mark_sent(url, "Title")  # should not raise
    assert clean_db.is_sent(url) is True

import sqlite3
from datetime import datetime


class Database:
    def __init__(self, path: str = "data/history.db"):
        self.path = path
        self.conn = None

    def init(self):
        import os
        os.makedirs("data", exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sent_articles (
                url TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                sent_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def is_sent(self, url: str) -> bool:
        cursor = self.conn.execute(
            "SELECT 1 FROM sent_articles WHERE url = ?", (url,)
        )
        return cursor.fetchone() is not None

    def mark_sent(self, url: str, title: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO sent_articles (url, title, sent_at) VALUES (?, ?, ?)",
            (url, title, datetime.utcnow().isoformat())
        )
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()

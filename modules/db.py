import os
import sqlite3
from datetime import datetime, timezone


class Database:
    def __init__(self, path: str = "data/history.db"):
        self.path = path
        self.conn = None

    def init(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
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
            (url, title, datetime.now(timezone.utc).isoformat())
        )
        self.conn.commit()

    def cleanup_old(self, days: int = 60):
        self.conn.execute(
            "DELETE FROM sent_articles WHERE sent_at < datetime('now', ?)",
            (f"-{days} days",)
        )
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

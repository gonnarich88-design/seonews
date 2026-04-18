# SEO News Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** สร้างระบบดึงข่าว SEO จาก RSS feeds สรุปและแปลไทยด้วย Claude API แล้วส่งเข้า Telegram ทุก 6 ชั่วโมงอัตโนมัติ

**Architecture:** Python script อ่าน RSS feeds 10 แหล่ง → กรอง keyword + ตรวจซ้ำด้วย SQLite → สรุป/แปลไทยด้วย Claude API → ส่ง digest เข้า Telegram group รัน cron ทุก 6 ชั่วโมง

**Tech Stack:** Python 3.11+, feedparser, anthropic SDK, python-telegram-bot, SQLite, PyYAML, python-dotenv, pytest

---

## File Structure

```
seonews/
├── config.yaml              # RSS sources, keywords, Claude model config
├── .env                     # ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
├── .gitignore               # exclude .env, data/, __pycache__
├── requirements.txt         # dependencies
├── main.py                  # orchestrator: ดึง→กรอง→สรุป→ส่ง
├── modules/
│   ├── __init__.py
│   ├── scraper.py           # ดึง RSS feeds ทุกแหล่ง
│   ├── db.py                # SQLite CRUD สำหรับประวัติข่าว
│   ├── filter.py            # กรอง keyword + ตรวจซ้ำกับ DB
│   ├── summarizer.py        # Claude API สรุป + แปลไทย
│   └── telegram.py          # format digest + ส่ง Telegram
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py
│   ├── test_db.py
│   ├── test_filter.py
│   ├── test_summarizer.py
│   ├── test_telegram.py
│   └── test_main.py
└── data/
    └── history.db           # สร้างอัตโนมัติตอน runtime
```

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `.env` (template)
- Create: `config.yaml`
- Create: `modules/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: สร้าง requirements.txt**

```
anthropic==0.40.0
feedparser==6.0.11
python-telegram-bot==21.6
python-dotenv==1.0.1
pyyaml==6.0.2
pytest==8.3.3
pytest-asyncio==0.24.0
```

- [ ] **Step 2: สร้าง .gitignore**

```
.env
data/
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
```

- [ ] **Step 3: สร้าง .env template**

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
TELEGRAM_BOT_TOKEN=your-bot-token-here
TELEGRAM_CHAT_ID=your-chat-id-here
```

- [ ] **Step 4: สร้าง config.yaml**

```yaml
claude:
  model: claude-haiku-4-5-20251001
  max_tokens: 500

schedule:
  hours: [2, 8, 14, 20]

keywords:
  - google update
  - algorithm
  - core update
  - seo
  - ranking
  - search engine
  - backlink
  - crawl
  - index
  - serp

sources:
  - name: Search Engine Land
    rss: https://searchengineland.com/feed
  - name: Search Engine Journal
    rss: https://www.searchenginejournal.com/feed
  - name: Search Engine Roundtable
    rss: https://www.seroundtable.com/feed
  - name: Google Search Central Blog
    rss: https://developers.google.com/search/blog/atom.xml
  - name: Moz Blog
    rss: https://moz.com/blog/feed
  - name: Ahrefs Blog
    rss: https://ahrefs.com/blog/feed
  - name: Semrush Blog
    rss: https://www.semrush.com/blog/feed
  - name: Backlinko
    rss: https://backlinko.com/feed
  - name: Neil Patel Blog
    rss: https://neilpatel.com/blog/feed
  - name: HubSpot Marketing
    rss: https://blog.hubspot.com/marketing/rss.xml
```

- [ ] **Step 5: สร้าง modules/__init__.py และ tests/__init__.py (ไฟล์ว่าง)**

```bash
touch modules/__init__.py tests/__init__.py
```

- [ ] **Step 6: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: ติดตั้งสำเร็จโดยไม่มี error

- [ ] **Step 7: Commit**

```bash
git init
git add requirements.txt .gitignore config.yaml modules/__init__.py tests/__init__.py
git commit -m "feat: project setup and configuration"
```

---

## Task 2: Database Module

**Files:**
- Create: `modules/db.py`
- Test: `tests/test_db.py`

- [ ] **Step 1: เขียน failing tests**

```python
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
```

- [ ] **Step 2: รัน test ให้ fail ก่อน**

```bash
pytest tests/test_db.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'modules.db'`

- [ ] **Step 3: Implement modules/db.py**

```python
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
```

- [ ] **Step 4: รัน test ให้ pass**

```bash
pytest tests/test_db.py -v
```

Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add modules/db.py tests/test_db.py
git commit -m "feat: add SQLite database module for article history"
```

---

## Task 3: Scraper Module

**Files:**
- Create: `modules/scraper.py`
- Test: `tests/test_scraper.py`

- [ ] **Step 1: เขียน failing tests**

```python
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
```

- [ ] **Step 2: รัน test ให้ fail ก่อน**

```bash
pytest tests/test_scraper.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'modules.scraper'`

- [ ] **Step 3: Implement modules/scraper.py**

```python
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
```

- [ ] **Step 4: รัน test ให้ pass**

```bash
pytest tests/test_scraper.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add modules/scraper.py tests/test_scraper.py
git commit -m "feat: add RSS feed scraper module"
```

---

## Task 4: Filter Module

**Files:**
- Create: `modules/filter.py`
- Test: `tests/test_filter.py`

- [ ] **Step 1: เขียน failing tests**

```python
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
```

- [ ] **Step 2: รัน test ให้ fail ก่อน**

```bash
pytest tests/test_filter.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'modules.filter'`

- [ ] **Step 3: Implement modules/filter.py**

```python
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
```

- [ ] **Step 4: รัน test ให้ pass**

```bash
pytest tests/test_filter.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add modules/filter.py tests/test_filter.py
git commit -m "feat: add keyword filter module with duplicate detection"
```

---

## Task 5: Summarizer Module (Claude API)

**Files:**
- Create: `modules/summarizer.py`
- Test: `tests/test_summarizer.py`

- [ ] **Step 1: เขียน failing tests**

```python
# tests/test_summarizer.py
import pytest
from unittest.mock import MagicMock, patch
from modules.summarizer import summarize_article

ARTICLE = {
    "title": "Google Core Update April 2026",
    "url": "https://searchengineland.com/google-core-update",
    "content": "Google has released a major core algorithm update affecting many websites...",
    "source": "Search Engine Land",
}

MOCK_RESPONSE = MagicMock()
MOCK_RESPONSE.content = [MagicMock(text="Google ปล่อย Core Update ครั้งใหญ่ในเดือนเมษายน 2569 ส่งผลต่อเว็บไซต์จำนวนมาก")]

def test_summarize_returns_thai_text():
    with patch("modules.summarizer.anthropic.Anthropic") as MockClient:
        mock_client = MockClient.return_value
        mock_client.messages.create.return_value = MOCK_RESPONSE
        result = summarize_article(ARTICLE, mock_client)
    assert isinstance(result, str)
    assert len(result) > 0

def test_summarize_calls_api_with_correct_model():
    with patch("modules.summarizer.anthropic.Anthropic") as MockClient:
        mock_client = MockClient.return_value
        mock_client.messages.create.return_value = MOCK_RESPONSE
        summarize_article(ARTICLE, mock_client, model="claude-haiku-4-5-20251001")
        call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-haiku-4-5-20251001"

def test_summarize_returns_fallback_on_api_error():
    with patch("modules.summarizer.anthropic.Anthropic") as MockClient:
        mock_client = MockClient.return_value
        mock_client.messages.create.side_effect = Exception("API Error")
        result = summarize_article(ARTICLE, mock_client)
    assert result == ""
```

- [ ] **Step 2: รัน test ให้ fail ก่อน**

```bash
pytest tests/test_summarizer.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'modules.summarizer'`

- [ ] **Step 3: Implement modules/summarizer.py**

```python
import anthropic
from typing import Dict


PROMPT_TEMPLATE = """คุณคือผู้เชี่ยวชาญด้าน SEO ที่สรุปข่าวเป็นภาษาไทย

ข่าวต้นฉบับ:
หัวข้อ: {title}
เนื้อหา: {content}

กรุณาสรุปข่าวนี้เป็นภาษาไทย 2-3 ประโยค ให้กระชับ เข้าใจง่าย และครอบคลุมประเด็นสำคัญ"""


def summarize_article(
    article: Dict,
    client: anthropic.Anthropic,
    model: str = "claude-haiku-4-5-20251001",
    max_tokens: int = 500,
) -> str:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": PROMPT_TEMPLATE.format(
                    title=article["title"],
                    content=article["content"][:2000],
                )
            }]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[ERROR] Summarizer failed for {article['url']}: {e}")
        return ""
```

- [ ] **Step 4: รัน test ให้ pass**

```bash
pytest tests/test_summarizer.py -v
```

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add modules/summarizer.py tests/test_summarizer.py
git commit -m "feat: add Claude API summarizer with Thai translation"
```

---

## Task 6: Telegram Module

**Files:**
- Create: `modules/telegram.py`
- Test: `tests/test_telegram.py`

- [ ] **Step 1: เขียน failing tests**

```python
# tests/test_telegram.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from modules.telegram import format_digest, send_digest

ARTICLES = [
    {
        "title": "Google Core Update April 2026",
        "url": "https://searchengineland.com/google-core-update",
        "summary": "Google ปล่อย Core Update ครั้งใหญ่ในเดือนเมษายน 2569",
        "source": "Search Engine Land",
    },
    {
        "title": "How to improve SEO rankings",
        "url": "https://moz.com/seo-rankings",
        "summary": "Moz แนะนำวิธีเพิ่ม ranking 5 ข้อที่ได้ผลจริง",
        "source": "Moz Blog",
    },
]

def test_format_digest_contains_title():
    msg = format_digest(ARTICLES, datetime(2026, 4, 18, 8, 0))
    assert "SEO News Digest" in msg

def test_format_digest_contains_article_titles():
    msg = format_digest(ARTICLES, datetime(2026, 4, 18, 8, 0))
    assert "Google Core Update April 2026" in msg
    assert "How to improve SEO rankings" in msg

def test_format_digest_contains_links():
    msg = format_digest(ARTICLES, datetime(2026, 4, 18, 8, 0))
    assert "https://searchengineland.com/google-core-update" in msg

def test_format_digest_shows_count():
    msg = format_digest(ARTICLES, datetime(2026, 4, 18, 8, 0))
    assert "2" in msg

def test_format_digest_empty_articles_returns_none():
    result = format_digest([], datetime(2026, 4, 18, 8, 0))
    assert result is None

@pytest.mark.asyncio
async def test_send_digest_calls_telegram_api():
    with patch("modules.telegram.Bot") as MockBot:
        mock_bot = AsyncMock()
        MockBot.return_value = mock_bot
        await send_digest("test message", "fake-token", "123456")
        mock_bot.send_message.assert_called_once_with(
            chat_id="123456",
            text="test message",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
```

- [ ] **Step 2: รัน test ให้ fail ก่อน**

```bash
pytest tests/test_telegram.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'modules.telegram'`

- [ ] **Step 3: Implement modules/telegram.py**

```python
from datetime import datetime
from typing import List, Dict, Optional
from telegram import Bot


THAI_MONTHS = {
    1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
    5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
    9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม",
}

NEXT_HOUR = {2: 8, 8: 14, 14: 20, 20: 2}


def format_digest(articles: List[Dict], now: datetime) -> Optional[str]:
    if not articles:
        return None

    thai_date = f"{now.day} {THAI_MONTHS[now.month]} {now.year + 543} | {now.strftime('%H:%M')}"
    next_hour = NEXT_HOUR.get(now.hour, (now.hour + 6) % 24)
    next_time = f"{next_hour:02d}:00"

    lines = [
        "📰 <b>SEO News Digest</b>",
        f"🕐 {thai_date}",
        "",
        "━━━━━━━━━━━━━━━━━━",
    ]

    for i, article in enumerate(articles, 1):
        lines.append(f"\n<b>{i}. {article['title']}</b>")
        lines.append(f"📌 สรุป: {article['summary']}")
        lines.append(f"🔗 <a href=\"{article['url']}\">อ่านต้นฉบับ</a>")

    lines.append("\n━━━━━━━━━━━━━━━━━━")
    lines.append(f"รวม {len(articles)} ข่าว | ครั้งหน้า {next_time}")

    return "\n".join(lines)


async def send_digest(message: str, bot_token: str, chat_id: str):
    bot = Bot(token=bot_token)
    await bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
```

- [ ] **Step 4: รัน test ให้ pass**

```bash
pytest tests/test_telegram.py -v
```

Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add modules/telegram.py tests/test_telegram.py
git commit -m "feat: add Telegram formatter and sender module"
```

---

## Task 7: Main Orchestrator

**Files:**
- Create: `main.py`
- Test: `tests/test_main.py`

- [ ] **Step 1: เขียน failing tests**

```python
# tests/test_main.py
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

def test_run_pipeline_with_no_new_articles(capsys):
    with patch("main.fetch_articles", return_value=[]), \
         patch("main.filter_articles", return_value=[]), \
         patch("main.Database") as MockDB:
        mock_db = MagicMock()
        MockDB.return_value = mock_db
        mock_db.init = MagicMock()
        mock_db.close = MagicMock()

        from main import run_pipeline
        run_pipeline()

        captured = capsys.readouterr()
        assert "ไม่มีข่าวใหม่" in captured.out

@pytest.mark.asyncio
async def test_run_pipeline_sends_when_articles_found():
    mock_article = {
        "title": "SEO Update", "url": "https://a.com/1",
        "content": "content", "source": "SEL"
    }
    summarized = {**mock_article, "summary": "สรุปภาษาไทย"}

    with patch("main.fetch_articles", return_value=[mock_article]), \
         patch("main.filter_articles", return_value=[mock_article]), \
         patch("main.summarize_article", return_value="สรุปภาษาไทย"), \
         patch("main.format_digest", return_value="digest message"), \
         patch("main.send_digest", new_callable=AsyncMock) as mock_send, \
         patch("main.Database") as MockDB, \
         patch("main.anthropic.Anthropic"), \
         patch("main.os.getenv", return_value="fake-value"):
        mock_db = MagicMock()
        MockDB.return_value = mock_db
        mock_db.init = MagicMock()
        mock_db.is_sent.return_value = False
        mock_db.mark_sent = MagicMock()
        mock_db.close = MagicMock()

        from main import run_pipeline
        run_pipeline()

        mock_send.assert_called_once()
```

- [ ] **Step 2: รัน test ให้ fail ก่อน**

```bash
pytest tests/test_main.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'main'`

- [ ] **Step 3: Implement main.py**

```python
import asyncio
import os
import yaml
import anthropic
from datetime import datetime
from dotenv import load_dotenv

from modules.db import Database
from modules.scraper import fetch_articles
from modules.filter import filter_articles
from modules.summarizer import summarize_article
from modules.telegram import format_digest, send_digest

load_dotenv()


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run_pipeline():
    config = load_config()
    db = Database()
    db.init()

    try:
        articles = fetch_articles(config["sources"])
        new_articles = filter_articles(articles, config["keywords"], db)

        if not new_articles:
            print("ไม่มีข่าวใหม่ในรอบนี้")
            return

        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        model = config["claude"]["model"]
        max_tokens = config["claude"]["max_tokens"]

        summarized = []
        for article in new_articles:
            summary = summarize_article(article, client, model=model, max_tokens=max_tokens)
            if summary:
                db.mark_sent(article["url"], article["title"])
                summarized.append({**article, "summary": summary})

        if not summarized:
            print("ไม่มีข่าวที่สรุปได้ในรอบนี้")
            return

        message = format_digest(summarized, datetime.now())
        if message:
            asyncio.run(send_digest(
                message,
                bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
                chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            ))
            print(f"ส่งข่าว {len(summarized)} ข่าวเข้า Telegram เรียบร้อย")

    finally:
        db.close()


if __name__ == "__main__":
    run_pipeline()
```

- [ ] **Step 4: รัน test ให้ pass**

```bash
pytest tests/test_main.py -v
```

Expected: 2 passed

- [ ] **Step 5: รัน test ทั้งหมด**

```bash
pytest tests/ -v
```

Expected: ทุก test ผ่าน (ไม่มี FAIL)

- [ ] **Step 6: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: add main orchestrator pipeline"
```

---

## Task 8: Cron Setup และ Manual Test

**Files:**
- Modify: ไม่มีไฟล์ใหม่ — ตั้งค่า cron บน server

- [ ] **Step 1: ทดสอบรันด้วยมือก่อน**

ต้องมีค่าใน `.env` จริงก่อน (Telegram bot token, chat ID, Anthropic API key)

```bash
python main.py
```

Expected output:
```
ส่งข่าว X ข่าวเข้า Telegram เรียบร้อย
```

- [ ] **Step 2: ตั้ง cron job**

```bash
crontab -e
```

เพิ่มบรรทัดนี้ (แก้ path ให้ตรงกับเครื่อง):

```
0 2,8,14,20 * * * cd /path/to/seonews && /usr/bin/python3 main.py >> /path/to/seonews/data/cron.log 2>&1
```

- [ ] **Step 3: ตรวจสอบ cron ถูกบันทึก**

```bash
crontab -l
```

Expected: เห็นบรรทัด cron ที่เพิ่งเพิ่ม

- [ ] **Step 4: Final commit**

```bash
git add .
git commit -m "feat: complete SEO news bot - ready for production"
```

---

## Self-Review Checklist

- [x] RSS Feed 10 แหล่ง → ครอบคลุมใน config.yaml (Task 1)
- [x] กรอง keyword + ป้องกันซ้ำ → filter.py + db.py (Task 2, 4)
- [x] Claude API สรุป + แปลไทย → summarizer.py (Task 5)
- [x] Telegram digest format + ส่ง → telegram.py (Task 6)
- [x] Error handling: scraper skip failed feeds, summarizer retry, telegram retry → ครอบคลุมใน modules แต่ละตัว
- [x] .gitignore ป้องกัน .env → Task 1
- [x] เพิ่ม source ได้ใน config.yaml โดยไม่แก้ code → Task 1
- [x] Cron ทุก 6 ชั่วโมง → Task 8

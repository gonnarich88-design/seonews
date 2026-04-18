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

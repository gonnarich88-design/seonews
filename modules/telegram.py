import html
import logging
from datetime import datetime
from typing import List, Dict, Optional
from telegram import Bot

logger = logging.getLogger(__name__)

THAI_MONTHS = {
    1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
    5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
    9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม",
}

_HASHTAG_RULES = [
    ("#CoreUpdate",      ["core update"]),
    ("#AlgorithmUpdate", ["algorithm"]),
    ("#TechnicalSEO",    ["crawl", "index", "schema", "structured data", "core web vitals", "page speed", "technical seo"]),
    ("#LinkBuilding",    ["backlink", "link building"]),
    ("#ContentSEO",      ["helpful content", "e-e-a-t", "eeat"]),
    ("#KeywordResearch", ["keyword research"]),
    ("#SERPFeature",     ["featured snippet", "ai overview", "ai search", "serp"]),
    ("#SearchConsole",   ["search console"]),
]


def _classify_hashtag(article: Dict) -> str:
    text = (article.get("title", "") + " " + article.get("summary", "")).lower()
    for tag, keywords in _HASHTAG_RULES:
        if any(kw in text for kw in keywords):
            return tag
    return "#SEONews"


def format_digest(articles: List[Dict], now: datetime) -> Optional[str]:
    if not articles:
        return None

    thai_date = f"{now.day} {THAI_MONTHS[now.month]} {now.year + 543} | {now.strftime('%H:%M')}"

    lines = [
        "📰 <b>SEO News Digest</b>",
        f"🕐 {thai_date}",
        "",
        "━━━━━━━━━━━━━━━━━━",
    ]

    for i, article in enumerate(articles, 1):
        tag = _classify_hashtag(article)
        lines.append(f"\n<b>{i}. {html.escape(article.get('title', ''))}</b>")
        lines.append(f"🏷 {tag}")
        lines.append(f"📌 สรุป: {html.escape(article.get('summary', ''))}")
        lines.append(f"🔗 <a href=\"{html.escape(article.get('url', ''), quote=False)}\">อ่านต้นฉบับ</a>")

    lines.append("\n━━━━━━━━━━━━━━━━━━")
    lines.append(f"รวม {len(articles)} ข่าว | ครั้งหน้าพรุ่งนี้ 08:00")

    return "\n".join(lines)


TELEGRAM_MAX_LEN = 4096


def _split_messages(message: str) -> List[str]:
    if len(message) <= TELEGRAM_MAX_LEN:
        return [message]

    chunks = []
    lines = message.split("\n")
    current = ""
    for line in lines:
        candidate = current + line + "\n"
        if len(candidate) > TELEGRAM_MAX_LEN:
            if current:
                chunks.append(current.rstrip())
            current = line + "\n"
        else:
            current = candidate
    if current:
        chunks.append(current.rstrip())
    return chunks


async def send_digest(message: str, bot_token: str, chat_id: str):
    bot = Bot(token=bot_token)
    for chunk in _split_messages(message):
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=chunk,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.error("Failed to send Telegram message: %s", e)
            raise

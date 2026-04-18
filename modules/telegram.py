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

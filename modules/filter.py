import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

from modules.db import Database

logger = logging.getLogger(__name__)

BKK_OFFSET = timedelta(hours=7)


def _yesterday_range_utc() -> tuple[datetime, datetime]:
    """คืน (start, end) ของ "เมื่อวาน" ตาม Bangkok time แปลงเป็น UTC"""
    now_bkk = datetime.now(timezone.utc) + BKK_OFFSET
    yesterday_bkk = now_bkk.date() - timedelta(days=1)
    start = datetime(yesterday_bkk.year, yesterday_bkk.month, yesterday_bkk.day,
                     tzinfo=timezone.utc) - BKK_OFFSET
    end = start + timedelta(days=1)
    return start, end


def _is_yesterday(published_at: Optional[datetime]) -> bool:
    if published_at is None:
        return False
    start, end = _yesterday_range_utc()
    return start <= published_at < end


def _rank_by_gpt(articles: List[Dict], client, model: str, max_articles: int) -> List[Dict]:
    """ให้ GPT เลือก max_articles ข่าวที่สำคัญที่สุด ส่งแค่หัวข้อ ประหยัด token"""
    import openai
    import anthropic

    numbered = "\n".join(f"{i+1}. {a['title']}" for i, a in enumerate(articles))
    prompt = (
        f"คุณคือบรรณาธิการข่าว SEO เลือก {max_articles} ข่าวที่สำคัญและน่าสนใจที่สุด"
        f"สำหรับนักทำ SEO จากรายการด้านล่าง\n\n{numbered}\n\n"
        f"ตอบเป็น JSON array ของ index (เริ่มจาก 0) เรียงจากสำคัญสุด เช่น [2,0,4]"
    )

    try:
        if isinstance(client, openai.OpenAI):
            resp = client.chat.completions.create(
                model=model,
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.choices[0].message.content.strip()
        elif isinstance(client, anthropic.Anthropic):
            resp = client.messages.create(
                model=model,
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.content[0].text.strip()
        else:
            return articles[:max_articles]

        # parse JSON array จาก response
        start = raw.find("[")
        end = raw.rfind("]") + 1
        indices = json.loads(raw[start:end])
        selected = [articles[i] for i in indices if 0 <= i < len(articles)]
        return selected[:max_articles]

    except Exception as e:
        logger.warning("GPT ranking failed, falling back to recency: %s", e)
        return articles[:max_articles]


def filter_articles(
    articles: List[Dict],
    keywords: List[str],
    db: Database,
    client=None,
    model: str = "gpt-4o-mini",
    max_articles: int = 5,
) -> List[Dict]:
    seen_urls = set()
    candidates = []

    for article in articles:
        url = article["url"]
        if url in seen_urls or db.is_sent(url):
            continue
        seen_urls.add(url)

        if not _is_yesterday(article.get("published_at")):
            continue

        text = (article["title"] + " " + article.get("content", "")).lower()
        if any(kw.lower() in text for kw in keywords):
            candidates.append(article)

    # เรียงใหม่สุดก่อน
    candidates.sort(key=lambda a: a.get("published_at") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    if len(candidates) <= max_articles:
        return candidates

    logger.info("มีข่าวผ่านกรอง %d ข่าว เกินกว่า %d → ให้ AI เลือก", len(candidates), max_articles)
    if client is not None:
        return _rank_by_gpt(candidates, client, model, max_articles)
    return candidates[:max_articles]

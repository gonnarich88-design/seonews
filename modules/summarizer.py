import logging
import anthropic
import openai
from typing import Dict

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """คุณคือผู้เชี่ยวชาญด้าน SEO ที่สรุปข่าวเป็นภาษาไทย

ข่าวต้นฉบับ:
หัวข้อ: {title}
เนื้อหา: {content}

สรุปข่าวนี้เป็นภาษาไทย 2-3 ประโยค โดย:
1. บอกว่าเกิดอะไรขึ้น
2. ส่งผลต่อ SEO อย่างไร
3. นักทำ SEO ควรทำอะไรต่อ (ถ้ามี)

กระชับ เข้าใจง่าย ตรงประเด็น"""


def summarize_article(
    article: Dict,
    client,
    model: str = "claude-haiku-4-5-20251001",
    max_tokens: int = 500,
) -> str:
    prompt = PROMPT_TEMPLATE.format(
        title=article.get("title", ""),
        content=article.get("content", "")[:2000],
    )
    try:
        if isinstance(client, anthropic.Anthropic):
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            if not response.content:
                return ""
            return response.content[0].text.strip()

        elif isinstance(client, openai.OpenAI):
            response = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error("Summarizer failed for %s: %s", article.get("url", "unknown"), e)
    return ""

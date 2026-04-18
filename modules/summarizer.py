import logging
import anthropic
from typing import Dict

logger = logging.getLogger(__name__)

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
                    title=article.get("title", ""),
                    content=article.get("content", "")[:2000],
                )
            }]
        )
        if not response.content:
            logger.error("Empty response from Claude API for %s", article.get("url", "unknown"))
            return ""
        return response.content[0].text.strip()
    except Exception as e:
        logger.error("Summarizer failed for %s: %s", article.get("url", "unknown"), e)
        return ""

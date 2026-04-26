import asyncio
import logging
import os
import yaml
import anthropic
import openai
from datetime import datetime
from dotenv import load_dotenv

from modules.db import Database
from modules.scraper import fetch_articles
from modules.filter import filter_articles
from modules.summarizer import summarize_article
from modules.telegram import format_digest, send_digest

load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Required environment variable {name} is not set")
    return value


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


async def run_pipeline():
    config = load_config()
    bot_token = _require_env("TELEGRAM_BOT_TOKEN")
    chat_id = _require_env("TELEGRAM_CHAT_ID")
    db = Database()
    db.init()
    db.cleanup_old(days=60)

    try:
        provider = config.get("provider", "claude")
        if provider == "openai":
            openai_key = _require_env("OPENAI_API_KEY")
            client = openai.OpenAI(api_key=openai_key)
            model = config["openai"]["model"]
            max_tokens = config["openai"]["max_tokens"]
        else:
            anthropic_key = _require_env("ANTHROPIC_API_KEY")
            client = anthropic.Anthropic(api_key=anthropic_key)
            model = config["claude"]["model"]
            max_tokens = config["claude"]["max_tokens"]

        max_articles = config.get("max_articles", 5)
        articles = fetch_articles(config["sources"])
        new_articles = filter_articles(
            articles, config["keywords"], db,
            client=client, model=model, max_articles=max_articles,
        )

        if not new_articles:
            print("ไม่มีข่าวใหม่เมื่อวานนี้")
            return

        summarized = []
        for article in new_articles:
            summary = summarize_article(article, client, model=model, max_tokens=max_tokens)
            if summary:
                summarized.append({**article, "summary": summary})

        if not summarized:
            print("ไม่มีข่าวที่สรุปได้ในรอบนี้")
            return

        message = format_digest(summarized, datetime.now())
        if message:
            await send_digest(message, bot_token=bot_token, chat_id=chat_id)
            for article in summarized:
                db.mark_sent(article["url"], article["title"])
            print(f"ส่งข่าว {len(summarized)} ข่าวเข้า Telegram เรียบร้อย")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_pipeline())

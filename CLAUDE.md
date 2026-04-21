# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# รันทดสอบทั้งหมด
python3 -m pytest tests/ -v

# รันทดสอบเฉพาะไฟล์
python3 -m pytest tests/test_filter.py -v

# รันระบบจริง (ต้องมี .env ครบ)
python3 main.py
```

## Environment

คัดลอก `.env.example` เป็น `.env` แล้วใส่ค่าจริง:
```
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

## Architecture

Pipeline ใน `main.py` ไหลตามลำดับนี้:

```
fetch_articles()  →  filter_articles()  →  summarize_article()  →  send_digest()
   scraper.py            filter.py           summarizer.py          telegram.py
                            │
                         db.py (SQLite dedup)
```

**Provider switching** — ควบคุมด้วย `provider: openai|claude` ใน `config.yaml` ไม่ต้องแก้ code ระบบสร้าง client ที่ถูกต้องใน `main.py` แล้วส่งไปทุก module ที่ต้องการ

**filter.py** — module ที่ซับซ้อนที่สุด มี 3 ขั้นตอน:
1. กรองเฉพาะข่าวที่ published เมื่อวาน (Bangkok time UTC+7) — ข่าวที่ไม่มี `published_at` ถูก skip ทั้งหมด
2. กรอง keyword จาก `config.yaml`
3. ถ้าผ่านเกิน `max_articles` → เรียก AI ranking โดยส่งแค่หัวข้อ (ประหยัด token) แล้ว fallback เป็น recency ถ้า API ล้มเหลว

**summarizer.py** — detect ประเภท client ด้วย `isinstance()` แล้วเรียก API ให้ถูก format (Anthropic vs OpenAI schema ต่างกัน)

**telegram.py** — `_split_messages()` แบ่งข้อความอัตโนมัติถ้าเกิน 4096 ตัวอักษร (Telegram limit)

## Config

ค่าสำคัญที่ปรับบ่อยใน `config.yaml`:
- `provider` — `openai` หรือ `claude`
- `max_articles` — จำนวนข่าวสูงสุดต่อวัน (default 5)
- `schedule.hours` — ชั่วโมงที่รัน (ปัจจุบัน `[8]` = วันละครั้ง 08:00)
- `sources` — เพิ่ม/ลด RSS feed ได้โดยไม่ต้องแก้ code

## Cron

```
0 8 * * * cd /Users/wolfy/works/seonews && /usr/bin/python3 main.py >> data/cron.log 2>&1
```

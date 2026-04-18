# SEO News Bot — Design Spec
Date: 2026-04-18

## Overview

ระบบดึงข่าว SEO จากแหล่งข้อมูลชั้นนำอัตโนมัติ สรุปและแปลเป็นภาษาไทยด้วย Claude API แล้วส่งเข้ากลุ่ม Telegram ทุก 6 ชั่วโมง

---

## Architecture

```
RSS Feeds (10 แหล่ง)
       │
       ▼
Scraper Module       — ดึง RSS feeds ทั้งหมด
       │
       ▼
Filter Module        — กรอง keyword + ตรวจสอบประวัติซ้ำ
       │
       ▼
Summarizer Module    — Claude API (haiku-4-5) สรุป + แปลไทย
       │
       ▼
Telegram Module      — ส่ง digest เข้ากลุ่ม
       │
       ▼
SQLite Database      — บันทึกประวัติข่าวที่ส่งแล้ว
```

---

## Schedule

- Cron: `0 2,8,14,20 * * *`
- ส่งเวลา 02:00, 08:00, 14:00, 20:00 ทุกวัน

---

## RSS Feed Sources

### กลุ่ม 1 — ข่าว SEO & Google Update (หลัก)
| เว็บ | RSS Feed URL |
|---|---|
| Search Engine Land | `https://searchengineland.com/feed` |
| Search Engine Journal | `https://www.searchenginejournal.com/feed` |
| Search Engine Roundtable | `https://www.seroundtable.com/feed` |
| Google Search Central Blog | `https://developers.google.com/search/blog/atom.xml` |

### กลุ่ม 2 — SEO Strategy & Tips
| เว็บ | RSS Feed URL |
|---|---|
| Moz Blog | `https://moz.com/blog/feed` |
| Ahrefs Blog | `https://ahrefs.com/blog/feed` |
| Semrush Blog | `https://www.semrush.com/blog/feed` |
| Backlinko | `https://backlinko.com/feed` |

### กลุ่ม 3 — Digital Marketing (เกี่ยวข้อง)
| เว็บ | RSS Feed URL |
|---|---|
| Neil Patel Blog | `https://neilpatel.com/blog/feed` |
| HubSpot Marketing | `https://blog.hubspot.com/marketing/rss.xml` |

เพิ่มแหล่งใหม่ได้ใน `config.yaml` โดยไม่ต้องแก้ code

---

## Keyword Filter

ข่าวต้องมี keyword อย่างน้อย 1 คำจากรายการนี้ (case-insensitive):

```
google update, algorithm, core update, seo, ranking,
search engine, backlink, crawl, index, serp
```

---

## Claude API

- **Model:** `claude-haiku-4-5-20251001` (เร็ว ราคาถูก เหมาะกับการสรุปข่าว)
- **Task:** รับ title + content ของแต่ละข่าว → สรุปกระชับ 2-3 ประโยค + แปลเป็นภาษาไทย
- **Upgrade path:** เปลี่ยนเป็น `claude-sonnet-4-6` ใน config.yaml ถ้าต้องการคุณภาพสูงขึ้น

---

## Telegram Message Format

```
📰 SEO News Digest
🕐 18 เมษายน 2569 | 08:00

━━━━━━━━━━━━━━━━━━
1. Google ปล่อย Core Update เมษายน 2569
📌 สรุป: Google อัปเดต algorithm ครั้งใหญ่ส่งผลต่อเว็บที่มีเนื้อหาคุณภาพต่ำ...
🔗 อ่านต้นฉบับ: https://searchengineland.com/...

2. วิธีเพิ่ม E-E-A-T ให้เว็บไซต์ในปี 2569
📌 สรุป: Ahrefs แนะนำ 5 วิธีสร้างความน่าเชื่อถือให้เว็บ...
🔗 อ่านต้นฉบับ: https://ahrefs.com/...
━━━━━━━━━━━━━━━━━━
รวม 8 ข่าว | ครั้งหน้า 14:00
```

---

## Error Handling

- RSS feed ใดดาวน์หรือ timeout → ข้ามไปแหล่งถัดไป ไม่หยุดทั้งระบบ
- Claude API error → retry 1 ครั้ง ถ้ายังล้มเหลว skip ข่าวนั้น
- Telegram error → retry 3 ครั้ง แล้ว log error

---

## Database

SQLite ตาราง `sent_articles`:
- `url` (primary key) — URL ต้นฉบับ
- `title` — หัวข้อข่าว
- `sent_at` — timestamp ที่ส่ง
- ตรวจสอบ URL ก่อนส่งทุกครั้งเพื่อป้องกันซ้ำ

---

## Project Structure

```
seonews/
├── config.yaml          # sources, keywords, schedule, model
├── main.py              # entry point, orchestrator
├── modules/
│   ├── scraper.py       # ดึง RSS feeds
│   ├── filter.py        # กรอง keyword + ตรวจสอบซ้ำ
│   ├── summarizer.py    # Claude API สรุป + แปลไทย
│   └── telegram.py      # ส่งข้อความเข้ากลุ่ม
├── data/
│   └── history.db       # SQLite
├── .env                 # ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
├── .gitignore           # exclude .env, data/, __pycache__
├── requirements.txt
└── docs/
    └── superpowers/specs/
        └── 2026-04-18-seonews-bot-design.md
```

---

## Environment Variables (.env)

```
ANTHROPIC_API_KEY=sk-ant-...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

---

## Dependencies (requirements.txt)

```
anthropic
feedparser
python-telegram-bot
python-dotenv
pyyaml
schedule
```

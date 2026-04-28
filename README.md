# SEO News Bot

ระบบดึงข่าว SEO จาก RSS feeds อัตโนมัติ สรุปและแปลเป็นภาษาไทยด้วย AI แล้วส่งเข้า Telegram ทุกวัน 08:00

---

## ฟีเจอร์

- ดึงข่าว SEO จาก **9 แหล่งชั้นนำ** ผ่าน RSS feed
- **กรองด้วย 19 keyword** ครอบคลุม technical SEO, content, AI search
- **ป้องกันข่าวซ้ำ** ด้วย SQLite (เก็บประวัติ 60 วัน)
- **สรุปเป็นภาษาไทย** พร้อมบอกผลกระทบ SEO และสิ่งที่ควรทำ
- **ติด hashtag อัตโนมัติ** ตามประเภทข่าว (#CoreUpdate, #TechnicalSEO ฯลฯ)
- รองรับทั้ง **Claude API** และ **OpenAI API** — สลับได้ใน `config.yaml`
- **Deploy บน EasyPanel** ด้วย Docker — รันอัตโนมัติไม่ต้องกดเอง

---

## แหล่งข้อมูล RSS (9 แหล่ง)

| กลุ่ม | เว็บไซต์ |
|---|---|
| ข่าว SEO & Google Update | Search Engine Land, Search Engine Journal, Search Engine Roundtable, Google Search Central Blog |
| SEO Strategy & Tips | Moz Blog, Ahrefs Blog, Semrush Blog, Backlinko |
| Digital Marketing | Neil Patel Blog |

---

## ตัวอย่างข้อความ Telegram

```
📰 SEO News Digest
🕐 27 เมษายน 2569 | 08:00

━━━━━━━━━━━━━━━━━━

1. Google ปล่อย Core Update เมษายน 2569
🏷 #CoreUpdate
📌 สรุป: Google อัปเดต algorithm ครั้งใหญ่ ส่งผลต่อเว็บที่มีเนื้อหาคุณภาพต่ำ
นักทำ SEO ควรตรวจสอบ Search Console และเน้นเนื้อหาที่มีคุณค่า
🔗 อ่านต้นฉบับ

2. วิธีเพิ่ม E-E-A-T ให้เว็บไซต์
🏷 #ContentSEO
📌 สรุป: Ahrefs แนะนำ 5 วิธีสร้างความน่าเชื่อถือ ควรเพิ่ม author bio และ cite แหล่งอ้างอิง
🔗 อ่านต้นฉบับ

━━━━━━━━━━━━━━━━━━
รวม 5 ข่าว | ครั้งหน้าพรุ่งนี้ 08:00
```

---

## โครงสร้างโปรเจค

```
seonews/
├── main.py              # entry point หลัก
├── config.yaml          # sources, keywords, model config
├── Dockerfile           # สำหรับ deploy บน EasyPanel
├── entrypoint.sh        # dump env vars ให้ cron อ่านได้
├── .env                 # API keys (ไม่ commit ขึ้น git)
├── .env.example         # template สำหรับ .env
├── requirements.txt     # Python dependencies
├── modules/
│   ├── db.py            # SQLite — ประวัติข่าว + cleanup 60 วัน
│   ├── scraper.py       # ดึง RSS feeds
│   ├── filter.py        # กรอง keyword + วันที่ + GPT ranking
│   ├── summarizer.py    # AI สรุปภาษาไทย + actionable insight
│   └── telegram.py      # hashtag + format digest + ส่ง Telegram
├── tests/               # unit tests
└── data/
    └── history.db       # SQLite database (สร้างอัตโนมัติ)
```

---

## การติดตั้ง (รันบนเครื่องตัวเอง)

### 1. ติดตั้ง dependencies

```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า environment variables

```bash
cp .env.example .env
```

แก้ไข `.env`:

```
OPENAI_API_KEY=sk-...               # จาก platform.openai.com
ANTHROPIC_API_KEY=sk-ant-...        # จาก console.anthropic.com (ถ้าใช้ Claude)
TELEGRAM_BOT_TOKEN=...              # จาก @BotFather ใน Telegram
TELEGRAM_CHAT_ID=...                # ID ของกลุ่ม Telegram
```

#### วิธีหา TELEGRAM_CHAT_ID
1. เพิ่ม bot เข้ากลุ่ม Telegram
2. ส่งข้อความในกลุ่ม
3. เปิด `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. หาค่า `chat.id` ในผลลัพธ์

### 3. รันด้วยมือ

```bash
python3 main.py
```

---

## Deploy บน EasyPanel

1. สร้าง App → Source: GitHub repo นี้ → Build: **Dockerfile**
2. เพิ่ม Environment Variables: `OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
3. เพิ่ม Volume Mount: `/app/data` (เก็บ SQLite ไม่ให้หายเมื่อ restart)
4. Deploy → ระบบรันอัตโนมัติทุก **08:00 Bangkok time**

ดู log: `tail -f /app/data/cron.log`

---

## ปรับแต่ง

แก้ไข `config.yaml` — ไม่ต้องแก้ code:

```yaml
provider: openai          # เปลี่ยนเป็น claude ได้
max_articles: 5           # จำนวนข่าวสูงสุดต่อวัน
keywords:                 # เพิ่ม/ลด keyword ได้เลย
  - google update
  - ...
sources:                  # เพิ่มแหล่งข้อมูลใหม่ได้เลย
  - name: ชื่อเว็บ
    rss: https://example.com/feed
```

---

## การทดสอบ

```bash
python3 -m pytest tests/ -v
```

---

## Tech Stack

| ส่วน | Library |
|---|---|
| RSS Fetching | feedparser |
| AI Summarizer | openai / anthropic |
| Telegram | python-telegram-bot |
| Database | SQLite (built-in) |
| Config | PyYAML |
| Testing | pytest + pytest-asyncio |

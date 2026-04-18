# SEO News Bot

ระบบดึงข่าว SEO จาก RSS feeds อัตโนมัติ สรุปและแปลเป็นภาษาไทยด้วย Claude API แล้วส่งเข้ากลุ่ม Telegram ทุก 6 ชั่วโมง

---

## ฟีเจอร์

- ดึงข่าว SEO จาก **10 แหล่งชั้นนำ** ผ่าน RSS feed
- **กรองข่าวด้วย keyword** ที่เกี่ยวข้องกับ SEO
- **ป้องกันข่าวซ้ำ** ด้วย SQLite
- **สรุปและแปลเป็นภาษาไทย** ด้วย Claude API (claude-haiku-4-5-20251001)
- ส่ง **digest รูปแบบ HTML** เข้ากลุ่ม Telegram
- **เพิ่มแหล่งข้อมูลใหม่ได้** โดยแก้แค่ `config.yaml`

---

## แหล่งข้อมูล RSS

| กลุ่ม | เว็บไซต์ |
|---|---|
| ข่าว SEO & Google Update | Search Engine Land, Search Engine Journal, Search Engine Roundtable, Google Search Central Blog |
| SEO Strategy & Tips | Moz Blog, Ahrefs Blog, Semrush Blog, Backlinko |
| Digital Marketing | Neil Patel Blog, HubSpot Marketing |

---

## โครงสร้างโปรเจค

```
seonews/
├── main.py              # entry point หลัก
├── config.yaml          # ตั้งค่า sources, keywords, Claude model
├── .env                 # API keys (ไม่ commit ขึ้น git)
├── .env.example         # template สำหรับ .env
├── requirements.txt     # Python dependencies
├── pytest.ini           # pytest config
├── modules/
│   ├── db.py            # SQLite — เก็บประวัติข่าวที่ส่งแล้ว
│   ├── scraper.py       # ดึง RSS feeds
│   ├── filter.py        # กรอง keyword + ตรวจซ้ำ
│   ├── summarizer.py    # Claude API สรุป + แปลไทย
│   └── telegram.py      # format digest + ส่ง Telegram
├── tests/               # unit tests (25 tests)
└── data/
    └── history.db       # SQLite database (สร้างอัตโนมัติ)
```

---

## การติดตั้ง

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
ANTHROPIC_API_KEY=sk-ant-...        # จาก console.anthropic.com
TELEGRAM_BOT_TOKEN=...              # จาก @BotFather ใน Telegram
TELEGRAM_CHAT_ID=...                # ID ของกลุ่ม Telegram
```

#### วิธีหา TELEGRAM_CHAT_ID
1. เพิ่ม bot เข้ากลุ่ม Telegram
2. ส่งข้อความในกลุ่ม
3. เปิด `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. หาค่า `chat.id` ในผลลัพธ์

---

## การใช้งาน

### รันด้วยมือ

```bash
python main.py
```

### ตั้ง Cron Job (ทุก 6 ชั่วโมง)

```bash
crontab -e
```

เพิ่มบรรทัดนี้ (แก้ path ให้ตรง):

```
0 2,8,14,20 * * * cd /path/to/seonews && /usr/bin/python3 main.py >> data/cron.log 2>&1
```

ส่งเวลา **02:00, 08:00, 14:00, 20:00** ทุกวัน

---

## ตัวอย่างข้อความ Telegram

```
📰 SEO News Digest
🕐 18 เมษายน 2569 | 08:00

━━━━━━━━━━━━━━━━━━
1. Google ปล่อย Core Update เมษายน 2569
📌 สรุป: Google อัปเดต algorithm ครั้งใหญ่ส่งผลต่อเว็บไซต์ที่มีเนื้อหาคุณภาพต่ำ...
🔗 อ่านต้นฉบับ

2. วิธีเพิ่ม E-E-A-T ให้เว็บไซต์ในปี 2569
📌 สรุป: Ahrefs แนะนำ 5 วิธีสร้างความน่าเชื่อถือให้เว็บ...
🔗 อ่านต้นฉบับ
━━━━━━━━━━━━━━━━━━
รวม 8 ข่าว | ครั้งหน้า 14:00
```

---

## เพิ่มแหล่งข้อมูลใหม่

แก้ไข `config.yaml` — ไม่ต้องแก้ code:

```yaml
sources:
  - name: ชื่อเว็บ
    rss: https://example.com/feed
```

---

## การทดสอบ

```bash
python -m pytest tests/ -v
```

ครอบคลุม 25 tests ทุก module

---

## Tech Stack

| ส่วน | Library |
|---|---|
| RSS Fetching | feedparser |
| AI Summarizer | anthropic (Claude API) |
| Telegram | python-telegram-bot |
| Database | SQLite (built-in) |
| Config | PyYAML |
| Testing | pytest + pytest-asyncio |

# SEO News Bot — สถานะโปรเจกต์

## ทำอะไรไปแล้ว

- [x] สร้างโครงสร้างโปรเจกต์ทั้งหมด
- [x] `modules/db.py` — SQLite เก็บประวัติข่าวที่ส่งแล้ว (ป้องกันซ้ำ)
- [x] `modules/scraper.py` — ดึง RSS feeds จาก 10 แหล่ง + เก็บ `published_at`
- [x] `modules/filter.py` — กรอง keyword + วันที่ (เฉพาะเมื่อวาน) + จำกัด 5 ข่าว + GPT ranking
- [x] `modules/summarizer.py` — สรุป + แปลไทย รองรับทั้ง Claude และ OpenAI
- [x] `modules/telegram.py` — format digest HTML + ส่ง Telegram (แบ่งข้อความอัตโนมัติ)
- [x] `main.py` — orchestrator รวมทุก module
- [x] `tests/` — 25 unit tests ผ่านทั้งหมด
- [x] `config.yaml` — RSS sources, keywords, Claude/OpenAI model config
- [x] README.md — คู่มือการใช้งานครบ
- [x] ทดสอบรันจริงสำเร็จ — ส่งข่าวเข้า Telegram ได้แล้ว

## Logic การคัดข่าว (ปัจจุบัน)

1. ดึงข่าวจาก RSS 10 แหล่ง
2. กรองเฉพาะข่าวที่ **published เมื่อวาน** (Bangkok time) — ข่าวที่ไม่มีวันที่ถูก skip
3. กรอง keyword SEO
4. ป้องกันข่าวซ้ำด้วย SQLite
5. ถ้าผ่านกรอง ≤ 5 ข่าว → เอาหมด
6. ถ้าผ่านกรองเกิน 5 → ให้ GPT เลือก 5 ข่าวสำคัญสุด (ส่งแค่หัวข้อ ประหยัด token)
7. สรุปเนื้อหาเป็นภาษาไทย → ส่ง Telegram

## Config สำคัญ (config.yaml)

- `provider: openai` — ใช้ OpenAI (เปลี่ยนเป็น `claude` เมื่อเติมเครดิต)
- `max_articles: 5` — จำนวนข่าวสูงสุดต่อวัน
- `schedule.hours: [8]` — ส่งทุกวัน 08:00 (วันละครั้ง)

## เหลือทำ

- [ ] ตั้ง cron job ให้รันวันละครั้ง 08:00

```bash
crontab -e
```

เพิ่มบรรทัด:
```
0 8 * * * cd /Users/wolfy/works/seonews && /usr/bin/python3 main.py >> data/cron.log 2>&1
```

- [ ] เติม credit Anthropic แล้วเปลี่ยน `provider: claude` ใน config.yaml

## ทดสอบ

```bash
python3 -m pytest tests/ -v   # 25 tests ผ่านทั้งหมด
python3 main.py               # รันจริง
```

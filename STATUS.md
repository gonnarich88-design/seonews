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
- [x] `README.md` — คู่มือการใช้งานครบ
- [x] ทดสอบรันจริงสำเร็จ — ส่งข่าวเข้า Telegram ได้แล้ว
- [x] ผูก GitHub repo: https://github.com/gonnarich88-design/seonews.git
- [x] `Dockerfile` + `.dockerignore` + `entrypoint.sh` — deploy บน EasyPanel พร้อม env vars ส่งเข้า cron
- [x] Deploy บน EasyPanel สำเร็จ (2026-04-23) — รันอัตโนมัติไม่ต้องกดเอง
- [x] `config.yaml` — ปรับ keyword เป็น 19 คำ ครอบคลุม technical SEO, content, AI search
- [x] `modules/telegram.py` — เพิ่ม hashtag classification (9 ประเภท) + แก้ข้อความ "ครั้งหน้า"
- [x] `modules/db.py` — เพิ่ม cleanup_old() ลบ record เก่าเกิน 60 วัน
- [x] `modules/summarizer.py` — ปรับ prompt ให้บอกผลกระทบ SEO + สิ่งที่ควรทำ

## Logic การคัดข่าว (ปัจจุบัน)

1. ดึงข่าวจาก RSS **9 แหล่ง** (ตัด HubSpot ออก)
2. กรองเฉพาะข่าวที่ **published เมื่อวาน** (Bangkok time) — ข่าวที่ไม่มีวันที่ถูก skip
3. กรอง **19 keyword** SEO (google update, core web vitals, e-e-a-t, ai overview ฯลฯ)
4. ป้องกันข่าวซ้ำด้วย SQLite (เก็บประวัติ 60 วัน)
5. ถ้าผ่านกรอง ≤ 5 ข่าว → เอาหมด
6. ถ้าผ่านกรองเกิน 5 → ให้ GPT เลือก 5 ข่าวสำคัญสุด (ส่งแค่หัวข้อ ประหยัด token)
7. สรุปเนื้อหาเป็นภาษาไทย (เกิดอะไร → ผลต่อ SEO → ควรทำอะไร) → ติด hashtag → ส่ง Telegram

## Config สำคัญ (config.yaml)

- `provider: openai` — ใช้ OpenAI (เปลี่ยนเป็น `claude` เมื่อเติมเครดิต Anthropic)
- `max_articles: 5` — จำนวนข่าวสูงสุดต่อวัน
- `schedule.hours: [8]` — ส่งทุกวัน 08:00 (วันละครั้ง)

## เหลือทำ

- [ ] เติม credit Anthropic แล้วเปลี่ยน `provider: claude` ใน config.yaml

## Deployment

- **Platform**: EasyPanel
- **Build**: Dockerfile (cron 08:00 Bangkok time)
- **Volume**: `/app/data` — เก็บ SQLite ป้องกันข้อมูลหายเมื่อ restart
- **Log**: `tail -f /app/data/cron.log`

## ทดสอบ

```bash
python3 -m pytest tests/ -v   # 25 tests ผ่านทั้งหมด
python3 main.py               # รันจริง
```

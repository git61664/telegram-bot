# Telegram Bot — Slayd/Mustaqil ish/PDF generatori (Kengaytirilgan)

## ✨ Yangi imkoniyatlar
- 🤖 **AI matn**: Har bir bo'lim uchun Claude API orqali to'liq, mazmunli matn yoziladi
- 🎨 **Rasmlar**: Slaydlarga avtomatik dekorativ rasm qo'shiladi
- 🌐 **3 til**: O'zbek, rus, ingliz tillarida ishlaydi
- 📚 **Tarix**: `/history` buyrug'i orqali oldingi yaratilgan fayllarni ko'rish (SQLite)

## Bot qanday ishlaydi?
1. `/start` — til tanlanadi (uz/ru/en)
2. Fayl turi tanlanadi (PPTX / DOCX / PDF)
3. Mavzu kiritiladi
4. Bo'limlar kiritiladi (har biri yangi qatorda)
5. AI har bir bo'lim uchun matn yozadi, slaydlarga rasm qo'shiladi
6. Tayyor fayl yuboriladi va tarixga saqlanadi

## O'rnatish qadamlari

### 1. Python 3.9+ borligini tekshiring
```bash
python3 --version
```

### 2. Kutubxonalarni o'rnating
```bash
pip install -r requirements.txt
```

### 3. Kerakli tokenlarni sozlang

**Telegram bot tokeni (majburiy)** — BotFather'dan oling:
```bash
export BOT_TOKEN="123456:ABC-yourTokenHere"
```

**Anthropic API kaliti (ixtiyoriy, lekin tavsiya etiladi)** — AI matn yozish uchun:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```
> ⚠️ Agar bu kalitni bermasangiz, bot ishlayveradi, lekin AI matn o'rniga oddiy shablon matn ishlatiladi.

Kalitni console.anthropic.com saytidan olishingiz mumkin.

### 4. Botni ishga tushiring
```bash
python bot.py
```
"Bot ishga tushdi..." xabarini ko'rsangiz — tayyor! Telegram'da botni oching va `/start` bosing.

## Fayl tuzilishi
| Fayl | Vazifasi |
|---|---|
| `bot.py` | Asosiy bot logikasi (aiogram, FSM, buyruqlar) |
| `generators.py` | PPTX/DOCX/PDF yaratish (AI matn + rasm bilan) |
| `ai_helper.py` | Claude API orqali matn generatsiyasi |
| `image_helper.py` | Slaydlar uchun dekorativ rasm chizish (Pillow) |
| `locales.py` | 3 tildagi UI matnlari (uz/ru/en) |
| `database.py` | SQLite: foydalanuvchi tili va fayl tarixi |
| `requirements.txt` | Kerakli kutubxonalar |

Ishga tushirilgach avtomatik yaratiladigan papkalar:
- `generated_files/` — yaratilgan PPTX/DOCX/PDF fayllar
- `generated_images/` — slaydlar uchun rasmlar
- `bot_database.db` — SQLite ma'lumotlar bazasi

## Buyruqlar
- `/start` — yangi fayl yaratishni boshlash
- `/history` — oldingi yaratilgan fayllar ro'yxati
- `/help` — yordam

## Keyingi qadamlar (ixtiyoriy)
- Slayd rasmlarini haqiqiy suratlar bilan almashtirish (masalan, Unsplash API)
- Foydalanuvchilar sonini cheklash / to'lov tizimi qo'shish (webhook + to'lov provayderi)
- Botni serverga (VPS, Railway, Render) joylashtirish — 24/7 ishlashi uchun
- Yaratilgan fayllarni bulutga (Google Drive) avtomatik saqlash

## Muammo yuzaga kelsa
| Muammo | Yechim |
|---|---|
| `ModuleNotFoundError` | `pip install -r requirements.txt` ni qayta ishga tushiring |
| Bot javob bermayapti | `BOT_TOKEN` to'g'ri kiritilganini tekshiring |
| AI matn o'rniga shablon matn chiqyapti | `ANTHROPIC_API_KEY` o'rnatilganini tekshiring |
| Rasm slaydga qo'shilmayapti | `Pillow` o'rnatilganini tekshiring: `pip install Pillow` |
| `/history` bo'sh chiqyapti | Hali birorta fayl yaratmagansiz — avval `/start` bosing |

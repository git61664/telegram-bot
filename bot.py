# -*- coding: utf-8 -*-
"""
Telegram Bot - Slayd (PPTX), Mustaqil ish (DOCX) va PDF generatori
====================================================================
KENGAYTIRILGAN VERSIYA:
  ✅ AI (Claude API) orqali har bir bo'lim uchun to'liq matn yozish
  ✅ Slaydlarga avtomatik dekorativ rasm qo'shish
  ✅ 3 tilda ishlash: o'zbek / rus / ingliz
  ✅ SQLite orqali foydalanuvchi tarixini saqlash (/history)

O'rnatish:
    pip install -r requirements.txt

Kerakli environment o'zgaruvchilari:
    BOT_TOKEN         - Telegram bot tokeni (BotFather'dan)
    ANTHROPIC_API_KEY - (ixtiyoriy) AI matn yozish uchun. Bo'lmasa, shablon matn ishlatiladi.

Ishga tushirish:
    python bot.py
"""

import os
import logging
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from generators import create_pptx, create_docx, create_pdf
from locales import t
import database as db

logging.basicConfig(level=logging.INFO)

# ============ SOZLAMALAR ============
BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_TOKENINGIZ_BU_YERGA")
OUTPUT_DIR = "generated_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ============ HOLATLAR (FSM) ============
class Form(StatesGroup):
    choosing_language = State()
    choosing_type = State()
    waiting_topic = State()
    waiting_points = State()


# ============ /start ============
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        ]
    )
    await state.set_state(Form.choosing_language)
    await message.answer(t("uz", "choose_lang"), reply_markup=kb)


# ============ Tilni tanlash ============
@dp.callback_query(F.data.startswith("lang_"))
async def choose_language(callback: CallbackQuery, state: FSMContext):
    language = callback.data.split("_")[1]  # uz / ru / en
    db.set_user_language(callback.from_user.id, language)
    await state.update_data(language=language)
    await state.set_state(Form.choosing_type)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(language, "btn_pptx"), callback_data="type_pptx")],
            [InlineKeyboardButton(text=t(language, "btn_docx"), callback_data="type_docx")],
            [InlineKeyboardButton(text=t(language, "btn_pdf"), callback_data="type_pdf")],
        ]
    )
    await callback.message.answer(t(language, "welcome"), reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


# ============ Fayl turini tanlash ============
@dp.callback_query(F.data.startswith("type_"))
async def choose_type(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", db.get_user_language(callback.from_user.id))

    file_type = callback.data.split("_")[1]  # pptx / docx / pdf
    await state.update_data(file_type=file_type, language=language)
    await state.set_state(Form.waiting_topic)
    await callback.message.answer(t(language, "ask_topic"))
    await callback.answer()


# ============ Mavzuni qabul qilish ============
@dp.message(Form.waiting_topic)
async def get_topic(message: Message, state: FSMContext):
    data = await state.get_data()
    language = data.get("language", "uz")

    await state.update_data(topic=message.text)
    await state.set_state(Form.waiting_points)
    await message.answer(t(language, "ask_points"))


# ============ Nuqtalarni qabul qilish va fayl yaratish ============
@dp.message(Form.waiting_points)
async def get_points(message: Message, state: FSMContext):
    data = await state.get_data()
    file_type = data["file_type"]
    topic = data["topic"]
    language = data.get("language", "uz")
    points = [p.strip() for p in message.text.split("\n") if p.strip()]

    await message.answer(t(language, "generating"))

    safe_name = "".join(c for c in topic if c.isalnum() or c in (" ", "_")).strip()
    safe_name = safe_name.replace(" ", "_")[:40] or "hujjat"

    try:
        if file_type == "pptx":
            path = os.path.join(OUTPUT_DIR, f"{safe_name}.pptx")
            create_pptx(topic, points, path, language)
        elif file_type == "docx":
            path = os.path.join(OUTPUT_DIR, f"{safe_name}.docx")
            create_docx(topic, points, path, language)
        else:  # pdf
            path = os.path.join(OUTPUT_DIR, f"{safe_name}.pdf")
            create_pdf(topic, points, path, language)

        file = FSInputFile(path)
        await message.answer_document(file, caption=t(language, "done", topic=topic))

        # Tarixga saqlash
        db.add_history(message.from_user.id, topic, file_type)

    except Exception as e:
        logging.exception("Fayl yaratishda xatolik")
        await message.answer(t(language, "error", error=str(e)))

    await state.clear()
    await message.answer(t(language, "restart"))


# ============ /history ============
@dp.message(Command("history"))
async def cmd_history(message: Message):
    language = db.get_user_language(message.from_user.id)
    rows = db.get_history(message.from_user.id)

    if not rows:
        await message.answer(t(language, "no_history"))
        return

    text = t(language, "history_title")
    icons = {"pptx": "📊", "docx": "📄", "pdf": "📕"}
    for topic, file_type, created_at in rows:
        date_str = created_at.split("T")[0]
        text += f"{icons.get(file_type, '📁')} {topic} — {date_str}\n"

    await message.answer(text)


# ============ /help ============
@dp.message(Command("help"))
async def cmd_help(message: Message):
    language = db.get_user_language(message.from_user.id)
    await message.answer(t(language, "help"))


# ============ Botni ishga tushirish ============
async def main():
    db.init_db()
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

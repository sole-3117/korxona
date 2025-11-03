# bot.py
import os
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL")  # mini app frontend URL
BACKEND_URL = os.environ.get("BACKEND_URL")  # backend URL

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN required")
if not WEBAPP_URL:
    raise Exception("WEBAPP_URL required")
if not BACKEND_URL:
    raise Exception("BACKEND_URL required")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    text = (
        "🚫 <b>Ruxsatsiz kirish taqiqlanadi!</b>\n\n"
        "Bu bot faqat maxsus foydalanuvchilar uchun mo‘ljallangan.\n"
        "Har qanday kirish urinishlari tizimda qayd etiladi.\n\n"
        "Ruxsatga ega foydalanuvchilar quyidagi tugma orqali tizimga kirishlari mumkin."
    )
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="🔐 Kirish", web_app=WebAppInfo(url=WEBAPP_URL))
    )
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    """
    When user sends a JSON file to bot (for import), download and POST to backend /api/import-file.
    """
    doc = message.document
    # check mime/type maybe
    if not doc.file_name.lower().endswith(".json"):
        await message.reply("Iltimos, faqat .json formatidagi eksport faylni yuboring.")
        return
    # download file to memory
    file = await bot.get_file(doc.file_id)
    file_path = file.file_path
    file_bytes = await bot.download_file(file_path)
    # file_bytes is bytes-like (aiogram returns BytesIO)
    file_bytes.seek(0)
    data = file_bytes.read()
    # send to backend
    import requests
    files = {"file": (doc.file_name, data, "application/json")}
    try:
        resp = requests.post(f"{BACKEND_URL}/api/import-file", files=files, timeout=30)
        if resp.status_code == 200:
            await message.reply("Fayl qabul qilindi va import qilindi. Rahmat.")
        else:
            await message.reply(f"Importda xatolik: {resp.status_code} {resp.text}")
    except Exception as e:
        await message.reply(f"Import server bilan xato yuz berdi: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
from aiogram import Router
import asyncio
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

@router.message(CommandStart())
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🪄 Mini App ochish", web_app=WebAppInfo(url=f"{WEBAPP_URL}"))]
        ]
    )
    await message.answer(
        f"Assalomu aleykum, {message.from_user.first_name}!\n"
        f"Bu bot shaxsiy 🤫\n\nQuyidagi tugmadan mini ilovani oching 👇",
        reply_markup=keyboard
    )

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
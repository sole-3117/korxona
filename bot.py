import logging
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
WEB_APP_URL = "https://your-render-url.onrender.com"  # Flask joylashgan manzil

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("🛍️ Kirish", web_app=types.WebAppInfo(url=WEB_APP_URL))
    kb.add(btn)
    await message.answer("Assalomu alaykum! Bu bot orqali do‘kon boshqaruvi mumkin.", reply_markup=kb)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
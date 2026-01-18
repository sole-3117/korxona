from telegram import Bot
from ..config import settings

bot = Bot(token=settings.telegram_token)

async def send_receipt(chat_id: int, pdf_path: str):
    with open(pdf_path, 'rb') as pdf:
        await bot.send_document(chat_id=chat_id, document=pdf)

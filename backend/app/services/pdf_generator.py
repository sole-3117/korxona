from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generate_receipt(sale_id: int, sale_data: dict, file_path: str):
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawString(100, 750, f"Do'kon nomi: {sale_data['shop_name']}")
    c.drawString(100, 730, f"Manzil: Toshkent")
    c.drawString(100, 710, f"Sana: {sale_data['date']}")
    # Mahsulotlar ro'yxati...
    c.drawString(100, 500, f"Jami: {sale_data['total']} so'm")
    c.save()
    return file_path  # Telegram'ga yuborish uchun

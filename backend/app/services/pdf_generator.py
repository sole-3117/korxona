from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os

def generate_receipt_pdf(sale_data: dict, file_path: str = "receipt.pdf"):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    y = height - 2*cm
    c.drawString(2*cm, y, f"Do'kon nomi: {sale_data['shop_name']}")
    y -= 20
    c.drawString(2*cm, y, f"Manzil: Samarqand shahar Rudakiy 175A uy")
    y -= 20
    c.drawString(2*cm, y, f"Sana: {sale_data['date']}")
    y -= 20
    c.drawString(2*cm, y, f"Sotuvchi: {sale_data['user']}")
    y -= 40
    for item in sale_data['items']:
        c.drawString(2*cm, y, f"{item['name']} x{item['qty']} = {item['total']} so'm")
        y -= 20
    y -= 20
    c.drawString(2*cm, y, f"Chegirma: {sale_data['discount']} so'm")
    y -= 20
    c.drawString(2*cm, y, f"Jami: {sale_data['total']} so'm")
    c.save()
    return file_path

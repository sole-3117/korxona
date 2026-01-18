def get_daily_report(db: Session, user_id: int, role: str):
    # Kunlik tushum hisoblash
    if role == 'admin':
        # To'liq hisobot
        pass
    else:
        # Faqat o'z sotuvlari
        pass
    # PDF generatsiya
    return {"tushum": 0, "xarajat": 0, "foyda": 0}

from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime
from sqlalchemy.sql import func
from ..database import Base

class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    pdf_path = Column(String, nullable=False)
    telegram_chat_id = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

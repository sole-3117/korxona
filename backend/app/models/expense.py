from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # 'ish_haqi', 'ijara', 'ovqat', 'bayram_puli', 'boshqa'
    amount = Column(Float, nullable=False)
    note = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

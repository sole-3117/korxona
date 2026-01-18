from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from ..database import Base

class InventoryLog(Base):
    __tablename__ = "inventory_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    expected_quantity = Column(Integer, nullable=False)
    actual_quantity = Column(Integer, nullable=False)
    loss_quantity = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

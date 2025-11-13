# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="admin")  # 'admin' or 'super'
    created_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    price = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)
    action = Column(String)
    ts = Column(DateTime, default=datetime.utcnow)

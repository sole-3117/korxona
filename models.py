# models.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

DB_PATH = os.environ.get("DB_PATH", "sqlite:///./korxona.db")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="admin")  # 'admin' or 'super'
    created_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
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

def init_db():
    Base.metadata.create_all(bind=engine)
    # create default superadmin if not exists
    db = SessionLocal()
    if not db.query(User).filter(User.username == "superadmin").first():
        from passlib.hash import bcrypt
        u = User(username="superadmin", password_hash=bcrypt.hash("superpass"), role="super")
        db.add(u)
        db.commit()
    db.close()

if __name__ == "__main__":
    init_db()

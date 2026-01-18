from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.utils.security import get_password_hash
from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()
# Dastlabki admin
admin = User(
    telegram_id=6887251996, #O'z ID'ingizni qo'ying
    username="admin",
    password_hash=get_password_hash("Sole2008"),
    role="admin"
)
db.add(admin)
db.commit()
print("Admin yaratildi: username=admin, password=Sole2008")
db.close()
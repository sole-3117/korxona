from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin
from ..services.auth_service import verify_telegram, create_user, authenticate_user, get_current_user
from ..utils.security import create_access_token

router = APIRouter()
security = HTTPBearer()

@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    # Telegram ID tekshirish
    if not verify_telegram(user.telegram_id):
        raise HTTPException(status_code=400, detail="Telegram ID noto'g'ri")
    
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Login yoki parol xato")
    
    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Hisob faol emas")
    
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer", "role": db_user.role}

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserLogin, User
from ..services.auth_service import authenticate_user, get_current_user
from ..utils.security import create_access_token, verify_password, get_password_hash

router = APIRouter()

@router.post("/login", response_model=dict)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user_login.username, user_login.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Noto'g'ri login yoki parol")
    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Hisob faol emas")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer", "role": db_user.role}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/create", response_model=User)  # Admin uchun
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, password_hash=get_password_hash(user.password), telegram_id=user.telegram_id, role="sotuvchi")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

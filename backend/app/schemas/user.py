from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    telegram_id: int

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str
    telegram_id: int

class User(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

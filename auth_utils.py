# auth_utils.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.hash import bcrypt
import os

# IMPORTANT: set SECRET_KEY env var in production
SECRET_KEY = os.environ.get("SECRET_KEY", "change_this_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_EXPIRE_MINUTES", 60*24*7))  # default 7 days

def create_access_token(subject: str, role: str):
    to_encode = {"sub": subject, "role": role, "iat": datetime.utcnow()}
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def hash_password(password: str) -> str:
    return bcrypt.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.verify(plain, hashed)

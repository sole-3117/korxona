from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./pos.db")
    secret_key: str = os.getenv("SECRET_KEY", "secret_super_key")
    telegram_token: str = os.getenv("TELEGRAM_TOKEN", "")

settings = Settings()
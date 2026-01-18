from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./pos.db"
    secret_key: str = "secret_super_key"  # .env dan o'qish
    telegram_token: str = "YOUR_TELEGRAM_BOT_TOKEN"

settings = Settings()

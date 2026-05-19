from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "")
    api_title: str = os.getenv("API_TITLE", "Brawl Stars API")
    api_description: str = os.getenv("API_DESCRIPTION", "API for Brawl Stars brawlers and player statistics")
    api_version: str = os.getenv("API_VERSION", "1.0.0")
    
    # 👇 Add this line
    brawl_stars_api_key: str = os.getenv("BRAWL_STARS_API_KEY", "")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
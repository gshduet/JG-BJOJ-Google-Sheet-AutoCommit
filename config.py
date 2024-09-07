from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env 파일 로드
load_dotenv()


class Settings(BaseSettings):
    json_file_path: str
    spreadsheet_url: str

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()

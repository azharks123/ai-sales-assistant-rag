import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "AI Sales Assistant RAG"
    API_V1_STR: str = "/api/v1"
    
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
    MAX_TOKEN: int = int(os.getenv("MAX_TOKEN", 500))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.7))
    
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASS: str = os.getenv("DB_PASS", "mysecretpassword")
    
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    SESSION_TTL: int = 1800

settings = Settings()

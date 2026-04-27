import os
import json
from typing import List, Union
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CyberShield AI"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "@Sinu8541")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "cybershield_db")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+aiomysql://root:%40Sinu8541@localhost:3306/cybershield_db"
    )
    CELERY_TASK_ALWAYS_EAGER: bool = os.getenv("CELERY_TASK_ALWAYS_EAGER", "True").lower() == "true"
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super_secret_jwt_key_change_in_production_32chars")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/app/uploads")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASS: str = os.getenv("SMTP_PASS", "")
    
    # Parse CORS Origins
    _raw_cors = os.getenv("CORS_ORIGINS", '["http://localhost:3000","http://localhost:80"]')
    try:
        CORS_ORIGINS: List[str] = json.loads(_raw_cors)
    except:
        CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80"]

    class Config:
        env_file = ".env"

settings = Settings()

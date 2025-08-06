import os
import dotenv

dotenv.load_dotenv()


class Settings:
    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgres://username:password@localhost:5432/fastapi_db"
    )

    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7  # 7 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 day

    # 应用配置
    APP_NAME: str = "RBAC 模版"
    APP_DESC: str = "RBAC 模版，基于 FastAPI + Tortoise ORM + JWT 实现的 RBAC 系统"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # CORS配置
    ALLOWED_HOSTS: list = ["*"]
    ALLOWED_ORIGINS: list = ["*"]

    # 微信配置
    APP_ID: str = os.getenv("APP_ID", "your-appid-here")
    APP_SECRET: str = os.getenv("APP_SECRET", "your-appsecret-here")

    # redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://:@localhost:6379/0")

settings = Settings()

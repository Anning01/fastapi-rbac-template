from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from api import api_router

from config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api")

register_tortoise(
    app,
    db_url=settings.DATABASE_URL,
    modules={"models": [f"models.{module}" for module in __import__("models").__all__]},
    generate_schemas=True,
    add_exception_handlers=True,
)

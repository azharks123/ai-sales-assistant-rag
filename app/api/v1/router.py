from fastapi import APIRouter
from app.api.v1.endpoints import chat, tools

api_router = APIRouter()
api_router.include_router(chat.router)
api_router.include_router(tools.router)

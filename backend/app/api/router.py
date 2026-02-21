from fastapi import APIRouter
from app.api.routes import datasources, scans, scans_recent, tables, chat

api_router = APIRouter()
api_router.include_router(datasources.router, prefix="/datasources", tags=["datasources"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(scans_recent.router, prefix="/scans", tags=["scans"])
api_router.include_router(tables.router, prefix="/tables", tags=["tables"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

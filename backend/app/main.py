from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import init_db
from app.api.router import api_router

def create_app() -> FastAPI:
    app = FastAPI(title="EDDA Backend", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def _startup():
        init_db()

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "edda-backend"}

    app.include_router(api_router, prefix="/api")
    return app

app = create_app()

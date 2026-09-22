"""FastAPI 应用工厂。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging("DEBUG" if get_settings().debug else "INFO")
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="AI 面试实训智能体（宁夏本地化版）后端 API",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/", tags=["root"])
    async def root() -> dict:
        return {"app": settings.app_name, "docs": "/docs"}

    return app


app = create_app()

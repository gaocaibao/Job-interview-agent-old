"""健康检查：部署探活 + Provider 配置状态。"""

from fastapi import APIRouter, Depends

from app.api.deps import get_llm_router
from app.config import get_settings
from app.services.llm.router import LLMRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
    }


@router.get("/health/llm")
async def llm_health(llm_router: LLMRouter = Depends(get_llm_router)) -> dict:
    return {
        "default_provider": get_settings().llm_default_provider,
        "fallback_chain": get_settings().fallback_chain,
        "available_providers": llm_router.available_providers(),
    }

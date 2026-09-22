"""API 路由汇总。"""

from fastapi import APIRouter

from app.api.v1 import health, interview, quiz, resume

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(resume.router)
api_router.include_router(quiz.router)
api_router.include_router(interview.router)

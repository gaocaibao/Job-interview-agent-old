"""依赖注入：服务单例。"""

from functools import lru_cache

from app.config import get_settings
from app.services.interview_service import InterviewService
from app.services.llm.providers import create_providers
from app.services.llm.router import LLMRouter
from app.services.quiz_service import QuizService
from app.services.resume_service import ResumeService


@lru_cache
def get_llm_router() -> LLMRouter:
    settings = get_settings()
    return LLMRouter(
        providers=create_providers(settings),
        fallback_chain=settings.fallback_chain,
        default_provider=settings.llm_default_provider,
    )


@lru_cache
def get_resume_service() -> ResumeService:
    return ResumeService(llm_router=get_llm_router())


@lru_cache
def get_quiz_service() -> QuizService:
    return QuizService(llm_router=get_llm_router())


@lru_cache
def get_interview_service() -> InterviewService:
    return InterviewService(llm_router=get_llm_router())

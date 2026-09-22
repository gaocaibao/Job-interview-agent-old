"""AI 视频面试模块 API。"""

from fastapi import APIRouter, Depends

from app.api.deps import get_interview_service
from app.schemas.interview import (
    InterviewNextAction,
    InterviewReport,
    InterviewSession,
    InterviewStartRequest,
)
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/sessions", response_model=InterviewSession, summary="创建面试会话")
async def create_session(
    request: InterviewStartRequest,
    service: InterviewService = Depends(get_interview_service),
) -> InterviewSession:
    return service.create_session(request)


@router.post(
    "/sessions/{session_id}/start",
    response_model=InterviewNextAction,
    summary="开始面试（返回第一题）",
)
async def start_interview(
    session_id: str, service: InterviewService = Depends(get_interview_service)
) -> InterviewNextAction:
    return await service.start(session_id)


@router.post(
    "/sessions/{session_id}/answers",
    response_model=InterviewNextAction,
    summary="提交回答（返回追问/下一题/结束指令）",
)
async def submit_answer(
    session_id: str,
    answer: str,
    service: InterviewService = Depends(get_interview_service),
) -> InterviewNextAction:
    return await service.submit_answer(session_id, answer)


@router.post(
    "/sessions/{session_id}/finish",
    response_model=InterviewReport,
    summary="结束面试并生成评价报告",
)
async def finish_interview(
    session_id: str, service: InterviewService = Depends(get_interview_service)
) -> InterviewReport:
    return await service.finish(session_id)

"""简历模块 API。"""

from fastapi import APIRouter, Depends

from app.api.deps import get_resume_service
from app.schemas.resume import (
    ResumeParseRequest,
    ResumeProfile,
    ResumeReviewRequest,
    ResumeReviewResponse,
)
from app.services.resume_service import ResumeService
from app.workflows.resume_flow import ResumeFlow

router = APIRouter(prefix="/resume", tags=["resume"])


def _flow(service: ResumeService = Depends(get_resume_service)) -> ResumeFlow:
    return ResumeFlow(service)


@router.post("/parse", response_model=ResumeProfile, summary="解析简历为结构化画像")
async def parse_resume(
    request: ResumeParseRequest, flow: ResumeFlow = Depends(_flow)
) -> ResumeProfile:
    return flow.parse(request)


@router.post(
    "/review",
    response_model=ResumeReviewResponse,
    summary="简历点评 + 生成定制面试题",
)
async def review_resume(
    request: ResumeReviewRequest, flow: ResumeFlow = Depends(_flow)
) -> ResumeReviewResponse:
    return await flow.review(request)

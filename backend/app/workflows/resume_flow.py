"""简历流程编排：解析 → 点评 → 生成定制考题。"""

from app.schemas.resume import (
    CustomQuestion,
    ResumeParseRequest,
    ResumeProfile,
    ResumeReviewRequest,
    ResumeReviewResponse,
)
from app.services.resume_service import ResumeService


class ResumeFlow:
    """简历模块业务流程（P0 版本：直接编排 Service，后续可扩展并行步骤）。"""

    def __init__(self, resume_service: ResumeService):
        self._service = resume_service

    async def parse(self, request: ResumeParseRequest) -> ResumeProfile:
        return self._service.parse(request.raw_text)

    async def review(self, request: ResumeReviewRequest) -> ResumeReviewResponse:
        return await self._service.review(request.profile, request.raw_text)

    async def parse_and_review(self, raw_text: str) -> tuple[ResumeProfile, ResumeReviewResponse]:
        profile = self._service.parse(raw_text)
        response = await self._service.review(profile, raw_text)
        return profile, response

    def custom_questions(self, response: ResumeReviewResponse) -> list[CustomQuestion]:
        return response.custom_questions

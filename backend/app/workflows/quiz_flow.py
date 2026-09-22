"""题库流程编排：选题 → 评分 → 掌握度更新。"""

from app.schemas.quiz import (
    MasterySummary,
    QuestionBankInfo,
    QuizAnswerRequest,
    QuizGradeResult,
    QuizQuestion,
)
from app.services.quiz_service import QuizService


class QuizFlow:
    """题库模块业务流程。"""

    def __init__(self, quiz_service: QuizService):
        self._service = quiz_service

    def list_banks(self) -> list[QuestionBankInfo]:
        return self._service.list_banks()

    async def start_session(self, bank_id: str, count: int = 5) -> list[QuizQuestion]:
        return self._service.draw_questions(bank_id, count)

    async def grade(self, request: QuizAnswerRequest) -> QuizGradeResult:
        return await self._service.grade(request)

    def summarize(self, results: list[QuizGradeResult]) -> list[MasterySummary]:
        return self._service.summarize(results)

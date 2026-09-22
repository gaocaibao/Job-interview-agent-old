"""题库训练模块 API。"""

from fastapi import APIRouter, Depends

from app.api.deps import get_quiz_service
from app.schemas.quiz import (
    MasterySummary,
    QuestionBankInfo,
    QuizAnswerRequest,
    QuizGradeResult,
    QuizQuestion,
)
from app.services.quiz_service import QuizService
from app.workflows.quiz_flow import QuizFlow

router = APIRouter(prefix="/quiz", tags=["quiz"])


def _flow(service: QuizService = Depends(get_quiz_service)) -> QuizFlow:
    return QuizFlow(service)


@router.get("/banks", response_model=list[QuestionBankInfo], summary="题库列表")
async def list_banks(flow: QuizFlow = Depends(_flow)) -> list[QuestionBankInfo]:
    return flow.list_banks()


@router.get(
    "/banks/{bank_id}/questions",
    response_model=list[QuizQuestion],
    summary="抽取题目",
)
async def draw_questions(
    bank_id: str, count: int = 5, flow: QuizFlow = Depends(_flow)
) -> list[QuizQuestion]:
    return await flow.start_session(bank_id, count)


@router.post("/grade", response_model=QuizGradeResult, summary="单题评分（LLM-as-Judge）")
async def grade_answer(
    request: QuizAnswerRequest, flow: QuizFlow = Depends(_flow)
) -> QuizGradeResult:
    return await flow.grade(request)


@router.post("/summarize", response_model=list[MasterySummary], summary="掌握度汇总")
async def summarize(results: list[QuizGradeResult]) -> list[MasterySummary]:
    return QuizService.summarize(results)

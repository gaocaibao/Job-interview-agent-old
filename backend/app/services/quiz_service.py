"""题库服务：题库管理 + LLM-as-Judge 评分。

P0 版本：内存种子题库；P2 迁移至数据库 + 知识网络驱动。
"""

import json

from app.core.errors import BadRequestError, NotFoundError
from app.schemas.common import EducationLevel, IndustryType, PositionType
from app.schemas.quiz import (
    MasterySummary,
    QuestionBankInfo,
    QuizAnswerRequest,
    QuizGradeResult,
    QuizQuestion,
)
from app.services.llm.base import ChatMessage
from app.services.llm.router import LLMRouter

_QUESTION_BANKS: dict[str, QuestionBankInfo] = {
    "ne-new-energy-op": QuestionBankInfo(
        id="ne-new-energy-op",
        title="宁夏新能源产业·运维操作岗",
        industry=IndustryType.NEW_ENERGY,
        position=PositionType.MANUFACTURING,
        education_levels=[EducationLevel.COLLEGE, EducationLevel.SENIOR_HIGH],
        question_count=3,
    ),
    "ne-wine-sales": QuestionBankInfo(
        id="ne-wine-sales",
        title="宁夏葡萄酒产业·销售岗",
        industry=IndustryType.WINE,
        position=PositionType.SALES,
        education_levels=[EducationLevel.SENIOR_HIGH, EducationLevel.JUNIOR_HIGH],
        question_count=2,
    ),
    "ne-ecom-service": QuestionBankInfo(
        id="ne-ecom-service",
        title="枸杞/滩羊电商·客服岗",
        industry=IndustryType.AGRICULTURE,
        position=PositionType.SERVICE,
        education_levels=[EducationLevel.JUNIOR_HIGH, EducationLevel.SENIOR_HIGH],
        question_count=2,
    ),
}

_QUESTIONS: dict[str, list[QuizQuestion]] = {
    "ne-new-energy-op": [
        QuizQuestion(
            id="ne-neo-1",
            content="风电和光伏发电的本质区别是什么？请用面试官能听懂的话说清楚。",
            knowledge_point="新能源发电原理",
            difficulty=2,
        ),
        QuizQuestion(
            id="ne-neo-2",
            content="宁夏作为国家新能源综合示范区，本地的风光资源优势体现在哪些方面？",
            knowledge_point="宁夏新能源产业政策",
            difficulty=2,
        ),
        QuizQuestion(
            id="ne-neo-3",
            content="运维人员在现场发现光伏板温度异常升高，你会按什么步骤处理？",
            knowledge_point="光伏运维安全规范",
            difficulty=3,
        ),
    ],
    "ne-wine-sales": [
        QuizQuestion(
            id="ne-ws-1",
            content="贺兰山东麓产区的风土特点是什么？对葡萄酒品质有什么影响？",
            knowledge_point="宁夏葡萄酒产区知识",
            difficulty=2,
        ),
        QuizQuestion(
            id="ne-ws-2",
            content="顾客说'我从没喝过国产葡萄酒'，你会怎么回应？",
            knowledge_point="销售沟通技巧",
            difficulty=1,
        ),
    ],
    "ne-ecom-service": [
        QuizQuestion(
            id="ne-es-1",
            content="顾客投诉收到的枸杞比直播间展示的小，要求退货，你怎么处理？",
            knowledge_point="客诉处理流程",
            difficulty=2,
        ),
        QuizQuestion(
            id="ne-es-2",
            content="请用三句话向新顾客介绍宁夏中宁枸杞的核心卖点。",
            knowledge_point="产品卖点提炼",
            difficulty=1,
        ),
    ],
}

_JUDGE_SYSTEM_PROMPT = """你是面试评审官。针对给定题目和参考答案要点，对求职者的回答评分。
严格输出 JSON（不要输出其他内容）：
{
  "level": "correct | half_correct | wrong",
  "score": 0-100 整数,
  "reason": "评分理由，一句话",
  "evidence": ["回答中的关键依据引用"]
}
评分标准：要点齐全且有条理=correct；覆盖部分要点=half_correct；偏题或空白=wrong。"""


class QuizService:
    def __init__(self, llm_router: LLMRouter):
        self._llm = llm_router

    def list_banks(self) -> list[QuestionBankInfo]:
        return list(_QUESTION_BANKS.values())

    def draw_questions(self, bank_id: str, count: int = 5) -> list[QuizQuestion]:
        if bank_id not in _QUESTION_BANKS:
            raise NotFoundError(f"题库 {bank_id} 不存在")
        return _QUESTIONS[bank_id][:count]

    async def grade(self, request: QuizAnswerRequest) -> QuizGradeResult:
        question = self._find_question(request.question_id)
        result = await self._llm.chat(
            [
                ChatMessage(role="system", content=_JUDGE_SYSTEM_PROMPT),
                ChatMessage(
                    role="user",
                    content=(
                        f"【题目】{question.content}\n"
                        f"【知识点】{question.knowledge_point}\n"
                        f"【求职者回答】{request.answer}"
                    ),
                ),
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        try:
            data = json.loads(result.content)
        except json.JSONDecodeError as exc:
            raise BadRequestError(f"模型返回格式异常: {exc}") from exc

        return QuizGradeResult(
            question_id=question.id,
            level=data.get("level", "wrong"),
            score=float(data.get("score", 0)),
            reason=data.get("reason", ""),
            evidence=data.get("evidence", []),
            knowledge_point=question.knowledge_point,
        )

    @staticmethod
    def summarize(results: list[QuizGradeResult]) -> list[MasterySummary]:
        grouped: dict[str, MasterySummary] = {}
        for r in results:
            if r.knowledge_point not in grouped:
                grouped[r.knowledge_point] = MasterySummary(knowledge_point=r.knowledge_point)
            s = grouped[r.knowledge_point]
            if r.level == "correct":
                s.correct += 1
            elif r.level == "half_correct":
                s.half_correct += 1
            else:
                s.wrong += 1
            total = s.correct + s.half_correct + s.wrong
            s.mastery = round((s.correct + 0.5 * s.half_correct) / total, 3) if total else 0.0
        return list(grouped.values())

    @staticmethod
    def _find_question(question_id: str) -> QuizQuestion:
        for questions in _QUESTIONS.values():
            for q in questions:
                if q.id == question_id:
                    return q
        raise NotFoundError(f"题目 {question_id} 不存在")

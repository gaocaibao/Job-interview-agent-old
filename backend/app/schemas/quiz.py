"""题库训练模块 API 模型。"""

from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.common import EducationLevel, IndustryType, PositionType


class QuestionBankInfo(BaseModel):
    """题库基本信息（列表项）。"""

    id: str
    title: str
    industry: IndustryType
    position: PositionType
    education_levels: list[EducationLevel]
    question_count: int = 0


class QuizQuestion(BaseModel):
    """小测题目（不含答案）。"""

    id: str
    content: str
    knowledge_point: str
    difficulty: int = Field(default=1, ge=1, le=3)


class QuizGradeLevel(StrEnum):
    """LLM-as-Judge 三级评分。"""

    CORRECT = "correct"
    HALF_CORRECT = "half_correct"
    WRONG = "wrong"


class QuizAnswerRequest(BaseModel):
    """单题作答提交。"""

    question_id: str
    answer: str = Field(..., min_length=1)


class QuizGradeResult(BaseModel):
    """单题评分结果。"""

    question_id: str
    level: str  # correct / half_correct / wrong
    score: float = Field(ge=0, le=100)
    reason: str = ""
    evidence: list[str] = Field(default_factory=list)
    knowledge_point: str = ""


class MasterySummary(BaseModel):
    """掌握度汇总。"""

    knowledge_point: str
    correct: int = 0
    half_correct: int = 0
    wrong: int = 0
    mastery: float = Field(default=0.0, ge=0, le=1)

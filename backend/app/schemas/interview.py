"""AI 视频面试模块 API 模型。"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.common import EducationLevel, IndustryType, PositionType
from app.schemas.resume import ResumeProfile


class InterviewMode(StrEnum):
    STANDARD = "standard"  # 常规模式
    PRESSURE = "pressure"  # 压力面试模式
    WARMUP = "warmup"  # 热身模式


class InterviewStartRequest(BaseModel):
    """发起面试请求。"""

    profile: ResumeProfile | None = None
    position: PositionType = PositionType.GENERAL
    industry: IndustryType = IndustryType.GENERAL
    education_level: EducationLevel = EducationLevel.BACHELOR
    mode: InterviewMode = InterviewMode.STANDARD
    question_count: int = Field(default=5, ge=1, le=10)


class InterviewState(StrEnum):
    IDLE = "idle"
    INTRO = "intro"
    ASKING = "asking"
    LISTENING = "listening"
    EVALUATING = "evaluating"
    FOLLOW_UP = "follow_up"
    TRANSITION = "transition"
    REPORT = "report"
    DONE = "done"


class InterviewTurn(BaseModel):
    """单个问答回合。"""

    index: int
    question: str
    answer: str = ""
    question_audio_url: str = ""
    evaluation: dict = Field(default_factory=dict)
    expression: dict = Field(default_factory=dict)  # 语速/停顿/填充词等


class InterviewSession(BaseModel):
    """面试会话（状态机快照）。"""

    session_id: str
    state: InterviewState = InterviewState.IDLE
    position: PositionType
    industry: IndustryType
    mode: InterviewMode
    profile: ResumeProfile | None = None
    turns: list[InterviewTurn] = Field(default_factory=list)
    total_questions: int = 5
    created_at: datetime = Field(default_factory=datetime.now)


class InterviewNextAction(BaseModel):
    """面试进行中的下一动作指令（前端据此渲染数字人/播放音频）。"""

    action: str  # ask_question / listen / follow_up / finish
    question: str = ""
    audio_url: str = ""
    turn_index: int = 0
    remaining: int = 0


class RadarDimension(BaseModel):
    dimension: str
    score: float = Field(ge=0, le=100)


class InterviewReport(BaseModel):
    """面试评价报告。"""

    session_id: str
    overall_score: float = Field(ge=0, le=100)
    radar: list[RadarDimension] = Field(default_factory=list)
    highlights: list[str] = Field(default_factory=list)
    weak_points: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    retrain_links: list[str] = Field(default_factory=list)

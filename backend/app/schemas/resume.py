"""简历模块 API 模型。"""

from pydantic import BaseModel, Field

from app.schemas.common import EducationLevel, IndustryType, PositionType


class ResumeParseRequest(BaseModel):
    """简历解析请求：原文粘贴或文本提取后的内容。"""

    raw_text: str = Field(..., min_length=20, description="简历纯文本内容")


class EducationItem(BaseModel):
    school: str = ""
    major: str = ""
    degree: str = ""
    period: str = ""


class ExperienceItem(BaseModel):
    company: str = ""
    role: str = ""
    period: str = ""
    highlights: list[str] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    """结构化简历画像。"""

    name: str = ""
    phone: str = ""
    email: str = ""
    education_level: EducationLevel = EducationLevel.BACHELOR
    target_position: PositionType = PositionType.GENERAL
    target_industry: IndustryType = IndustryType.GENERAL
    skills: list[str] = Field(default_factory=list)
    educations: list[EducationItem] = Field(default_factory=list)
    experiences: list[ExperienceItem] = Field(default_factory=list)


class ResumeReviewRequest(BaseModel):
    """简历点评请求。"""

    profile: ResumeProfile
    raw_text: str = Field(..., min_length=20)


class ResumeReviewItem(BaseModel):
    title: str
    detail: str
    severity: str = "medium"  # high / medium / low


class ResumeReview(BaseModel):
    """简历点评结果。"""

    highlights: list[ResumeReviewItem] = Field(default_factory=list)
    weaknesses: list[ResumeReviewItem] = Field(default_factory=list)
    keyword_suggestions: list[str] = Field(default_factory=list)
    template_recommendation: str = ""
    overall_score: int = Field(default=0, ge=0, le=100)


class CustomQuestion(BaseModel):
    """基于简历生成的定制面试题。"""

    question: str
    intent: str = ""
    reference_answer_points: list[str] = Field(default_factory=list)
    source_ref: str = ""


class ResumeReviewResponse(BaseModel):
    review: ResumeReview
    custom_questions: list[CustomQuestion] = Field(default_factory=list)
    provider_used: str = ""

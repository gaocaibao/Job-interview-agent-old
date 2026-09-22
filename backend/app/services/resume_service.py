"""简历服务：规则解析 + LLM 点评。"""

import json
import re

from app.core.errors import BadRequestError
from app.schemas.common import EducationLevel
from app.schemas.resume import (
    CustomQuestion,
    ResumeProfile,
    ResumeReview,
    ResumeReviewItem,
    ResumeReviewResponse,
)
from app.services.llm.base import ChatMessage
from app.services.llm.router import LLMRouter

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")

_EDU_PATTERNS: list[tuple[str, EducationLevel]] = [
    ("博士", EducationLevel.MASTER),
    ("硕士", EducationLevel.MASTER),
    ("研究生", EducationLevel.MASTER),
    ("本科", EducationLevel.BACHELOR),
    ("学士", EducationLevel.BACHELOR),
    ("大专", EducationLevel.COLLEGE),
    ("专科", EducationLevel.COLLEGE),
    ("高职", EducationLevel.COLLEGE),
    ("高中", EducationLevel.SENIOR_HIGH),
    ("中专", EducationLevel.SENIOR_HIGH),
    ("初中", EducationLevel.JUNIOR_HIGH),
]

_SKILL_KEYWORDS = [
    "Excel",
    "Word",
    "PPT",
    "Python",
    "Java",
    "JavaScript",
    "SQL",
    "CAD",
    "焊接",
    "电工",
    "PLC",
    "运维",
    "直播",
    "电商",
    "客服",
    "销售",
    "叉车",
    "光伏",
    "风电",
    "储能",
    "葡萄酒",
    "品酒",
    "枸杞",
    "养殖",
    "数据标注",
    "客服话术",
    "短视频",
    "剪辑",
    "驾证",
    "厨师",
    "护理",
]

_REVIEW_SYSTEM_PROMPT = """你是资深简历顾问，服务对象是宁夏本地求职者（含低学历、转行、应届群体）。
请基于给定的结构化画像和简历原文输出点评，严格输出 JSON（不要输出其他内容）：
{
  "highlights": [{"title": "亮点标题", "detail": "说明", "severity": "high|medium|low"}],
  "weaknesses": [{"title": "不足标题", "detail": "说明与改法", "severity": "high|medium|low"}],
  "keyword_suggestions": ["建议补充的关键词"],
  "template_recommendation": "推荐的简历模板策略（结合学历）",
  "overall_score": 0-100 的整数,
  "custom_questions": [{"question": "结合简历经历的定制面试题", "intent": "考察意图",
     "reference_answer_points": ["参考答案要点"], "source_ref": "知识来源（如有）"}]
}
要求：亮点和不足各 2-4 条；定制面试题 3-5 道，必须结合简历中的具体经历；语言直白、可执行。"""


class ResumeService:
    def __init__(self, llm_router: LLMRouter):
        self._llm = llm_router

    def parse(self, raw_text: str) -> ResumeProfile:
        if not raw_text or len(raw_text.strip()) < 20:
            raise BadRequestError("简历内容过短，无法解析")

        email = _EMAIL_RE.search(raw_text)
        phone = _PHONE_RE.search(raw_text)

        education = EducationLevel.BACHELOR
        for keyword, level in _EDU_PATTERNS:
            if keyword in raw_text:
                education = level
                break

        skills = [kw for kw in _SKILL_KEYWORDS if kw.lower() in raw_text.lower()]

        return ResumeProfile(
            name="",
            phone=phone.group(0) if phone else "",
            email=email.group(0) if email else "",
            education_level=education,
            skills=skills,
        )

    async def review(self, profile: ResumeProfile, raw_text: str) -> ResumeReviewResponse:
        result = await self._llm.chat(
            [
                ChatMessage(role="system", content=_REVIEW_SYSTEM_PROMPT),
                ChatMessage(
                    role="user",
                    content=(
                        f"【结构化画像】\n{profile.model_dump_json(indent=2)}\n\n"
                        f"【简历原文】\n{raw_text[:6000]}"
                    ),
                ),
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        try:
            data = json.loads(result.content)
        except json.JSONDecodeError as exc:
            raise BadRequestError(f"模型返回格式异常: {exc}") from exc

        review = ResumeReview(
            highlights=[ResumeReviewItem(**h) for h in data.get("highlights", [])],
            weaknesses=[ResumeReviewItem(**w) for w in data.get("weaknesses", [])],
            keyword_suggestions=data.get("keyword_suggestions", []),
            template_recommendation=data.get("template_recommendation", ""),
            overall_score=int(data.get("overall_score", 0)),
        )
        questions = [CustomQuestion(**q) for q in data.get("custom_questions", [])]
        return ResumeReviewResponse(
            review=review, custom_questions=questions, provider_used=result.provider
        )

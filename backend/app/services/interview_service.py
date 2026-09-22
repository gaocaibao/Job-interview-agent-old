"""面试服务：会话管理 + 状态机驱动 + 评估。

设计要点：
- 未配置 LLM 时使用种子题目与启发式评估，保证端到端可演示（文字模式）
- 配置 LLM 后自动升级为智能追问与 LLM-as-Judge 评分
"""

import uuid

from app.core.errors import BadRequestError, NotFoundError
from app.schemas.common import PositionType
from app.schemas.interview import (
    InterviewMode,
    InterviewNextAction,
    InterviewReport,
    InterviewSession,
    InterviewStartRequest,
    InterviewState,
    InterviewTurn,
    RadarDimension,
)
from app.services.llm.router import LLMRouter
from app.workflows.interview_flow import InterviewStateMachine

# 种子题库：按岗位的默认首问（LLM 不可用时的兜底）
_SEED_QUESTIONS: dict[PositionType, list[str]] = {
    PositionType.GENERAL: [
        "请用两分钟做一个自我介绍，重点讲和你应聘岗位相关的经历。",
        "你应聘这个岗位，你认为自己最大的优势是什么？请举一个具体事例。",
        "讲一件你克服困难完成任务的经历，你在其中做了什么？",
        "你对未来三年的职业有什么规划？",
        "你还有什么问题想问我们？",
    ],
    PositionType.TECHNICAL: [
        "请介绍一个你参与过的技术项目，你负责哪部分？",
        "遇到过最难的技术问题是什么？怎么定位和解决的？",
        "你如何保证自己的工作质量？举例说明。",
        "如何看待加班和紧急上线？",
        "你还有什么问题想问我们？",
    ],
    PositionType.SALES: [
        "你做过最有成就感的一笔销售/推广是什么？怎么做到的？",
        "客户明确拒绝你时，你会怎么处理？",
        "你怎么了解一款新产品并向别人介绍它？",
        "销售指标压力很大时你怎么调节？",
        "你还有什么问题想问我们？",
    ],
    PositionType.SERVICE: [
        "讲一次你处理客户投诉的经历，结果如何？",
        "遇到客户情绪激动、说话很难听，你会怎么应对？",
        "你觉得自己性格里最适合做服务的一点是什么？",
        "如果同时来多位客户，你怎么安排？",
        "你还有什么问题想问我们？",
    ],
    PositionType.MANUFACTURING: [
        "你有过一线生产/工程现场的实践经验吗？具体做什么？",
        "发现设备异常或安全隐患时，你的处理流程是什么？",
        "你如何理解安全生产规范？举个你遵守的例子。",
        "倒班或户外作业你能适应吗？",
        "你还有什么问题想问我们？",
    ],
    PositionType.OPERATION: [
        "你做过哪些运营相关的工作？用什么指标衡量效果？",
        "如果负责的活动数据很差，你会怎么分析原因？",
        "你怎么理解'用户思维'？举一个你应用的例子。",
        "同时推进多个任务时你怎么安排优先级？",
        "你还有什么问题想问我们？",
    ],
}

_FOLLOW_UP_HINTS = [
    "你刚才说的能再具体一点吗？比如当时你具体负责哪一步？",
    "如果重来一次，你觉得哪一步可以做得更好？",
    "这个经历里，团队有几个人？你怎么和他们配合的？",
]

_PRESSURE_HINTS = [
    "你刚才的回答比较笼统，我想听更具体的细节。",
    "很多应聘者都会这么说，你和他们有什么不同？",
]

_STAR_KEYWORDS = ["负责", "主导", "完成", "提升", "通过", "组织", "协调", "实现", "解决", "推进"]


class InterviewService:
    def __init__(self, llm_router: LLMRouter):
        self._llm = llm_router
        self._sessions: dict[str, tuple[InterviewSession, InterviewStateMachine]] = {}

    # ---------- 会话生命周期 ----------

    def create_session(self, request: InterviewStartRequest) -> InterviewSession:
        session = InterviewSession(
            session_id=uuid.uuid4().hex,
            position=request.position,
            industry=request.industry,
            mode=request.mode,
            profile=request.profile,
            total_questions=request.question_count,
        )
        self._sessions[session.session_id] = (session, InterviewStateMachine())
        return session

    def get_session(self, session_id: str) -> InterviewSession:
        if session_id not in self._sessions:
            raise NotFoundError(f"面试会话 {session_id} 不存在")
        return self._sessions[session_id][0]

    def _get_machine(self, session_id: str) -> InterviewStateMachine:
        if session_id not in self._sessions:
            raise NotFoundError(f"面试会话 {session_id} 不存在")
        return self._sessions[session_id][1]

    async def start(self, session_id: str) -> InterviewNextAction:
        session, machine = self._sessions[session_id]
        machine.to(InterviewState.INTRO)
        machine.to(InterviewState.ASKING)
        question = self._next_question(session)
        session.turns.append(InterviewTurn(index=len(session.turns) + 1, question=question))
        machine.to(InterviewState.LISTENING)
        return InterviewNextAction(
            action="ask_question",
            question=question,
            turn_index=len(session.turns),
            remaining=session.total_questions - len(session.turns),
        )

    async def submit_answer(self, session_id: str, answer: str) -> InterviewNextAction:
        session, machine = self._sessions[session_id]
        if machine.state != InterviewState.LISTENING:
            raise BadRequestError(f"当前状态 {machine.state} 不允许提交回答")
        if not answer.strip():
            raise BadRequestError("回答内容不能为空")

        current = session.turns[-1]
        current.answer = answer

        machine.to(InterviewState.EVALUATING)
        evaluation = await self._evaluate(session, current)
        current.evaluation = evaluation

        if evaluation["follow_up"]:
            machine.to(InterviewState.FOLLOW_UP)
            machine.to(InterviewState.LISTENING)
            follow_up = self._follow_up_question(session)
            session.turns.append(InterviewTurn(index=len(session.turns) + 1, question=follow_up))
            return InterviewNextAction(
                action="follow_up",
                question=follow_up,
                turn_index=len(session.turns),
                remaining=session.total_questions - len(session.turns),
            )

        if len(session.turns) >= session.total_questions:
            machine.to(InterviewState.REPORT)
            return InterviewNextAction(action="finish", turn_index=len(session.turns), remaining=0)

        machine.to(InterviewState.TRANSITION)
        machine.to(InterviewState.ASKING)
        question = self._next_question(session)
        session.turns.append(InterviewTurn(index=len(session.turns) + 1, question=question))
        machine.to(InterviewState.LISTENING)
        return InterviewNextAction(
            action="ask_question",
            question=question,
            turn_index=len(session.turns),
            remaining=session.total_questions - len(session.turns),
        )

    async def finish(self, session_id: str) -> InterviewReport:
        session, machine = self._sessions[session_id]
        if machine.state != InterviewState.REPORT:
            raise BadRequestError("面试尚未结束，无法生成报告")
        report = await self._build_report(session)
        machine.to(InterviewState.DONE)
        return report

    # ---------- 内部逻辑 ----------

    def _next_question(self, session: InterviewSession) -> str:
        asked = {t.question for t in session.turns}
        candidates = _SEED_QUESTIONS.get(session.position, _SEED_QUESTIONS[PositionType.GENERAL])
        for q in candidates:
            if q not in asked:
                return q
        return candidates[len(session.turns) % len(candidates)]

    def _follow_up_question(self, session: InterviewSession) -> str:
        pool = _PRESSURE_HINTS if session.mode == InterviewMode.PRESSURE else _FOLLOW_UP_HINTS
        return pool[len(session.turns) % len(pool)]

    async def _evaluate(self, session: InterviewSession, turn: InterviewTurn) -> dict:
        """评估当前回答，返回 {score, level, follow_up, reason}。"""
        if self._llm.available_providers():
            return await self._evaluate_with_llm(session, turn)
        return self._evaluate_heuristic(turn.answer, session.mode)

    def _evaluate_heuristic(self, answer: str, mode: InterviewMode) -> dict:
        length = len(answer.strip())
        star_hits = sum(1 for kw in _STAR_KEYWORDS if kw in answer)
        score = min(100, length // 4 + star_hits * 12)
        if mode == InterviewMode.PRESSURE and length < 60:
            score = min(score, 55)
        level = "correct" if score >= 70 else ("half_correct" if score >= 40 else "wrong")
        follow_up = star_hits == 0 and length < 80
        return {
            "score": score,
            "level": level,
            "follow_up": follow_up,
            "reason": "启发式评估（未配置 LLM）：基于回答长度与结构化关键词",
            "source": "heuristic",
        }

    async def _evaluate_with_llm(self, session: InterviewSession, turn: InterviewTurn) -> dict:
        import json

        from app.services.llm.base import ChatMessage

        result = await self._llm.chat(
            [
                ChatMessage(
                    role="system",
                    content=(
                        "你是面试评审官。评估求职者对一个面试问题的回答，严格输出 JSON：\n"
                        '{"score": 0-100, "level": "correct|half_correct|wrong", '
                        '"reason": "一句话理由", "follow_up": true/false}\n'
                        "回答过短（少于30字）或缺少具体事例时 follow_up 设为 true。"
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=(
                        f"【岗位】{session.position.value}【产业】{session.industry.value}\n"
                        f"【问题】{turn.question}\n【回答】{turn.answer}"
                    ),
                ),
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        try:
            data = json.loads(result.content)
        except json.JSONDecodeError:
            return self._evaluate_heuristic(turn.answer, session.mode)
        return {
            "score": float(data.get("score", 0)),
            "level": data.get("level", "wrong"),
            "reason": data.get("reason", ""),
            "follow_up": bool(data.get("follow_up", False)),
            "source": result.provider,
        }

    async def _build_report(self, session: InterviewSession) -> InterviewReport:
        turns = [t for t in session.turns if t.evaluation]
        if not turns:
            scores = [0.0]
        else:
            scores = [float(t.evaluation.get("score", 0)) for t in turns]
        overall = round(sum(scores) / len(scores), 1)

        radar = [
            RadarDimension(dimension="专业知识", score=self._dim_score(turns, "correct")),
            RadarDimension(dimension="表达逻辑", score=self._expression_score(turns)),
            RadarDimension(dimension="临场表现", score=round(overall)),
            RadarDimension(dimension="抗压能力", score=self._pressure_score(session)),
            RadarDimension(dimension="岗位匹配", score=self._match_score(session, turns)),
        ]

        weak_points = [
            f"第 {t.index} 题得分偏低（{t.evaluation.get('score', 0)} 分）"
            for t in turns
            if float(t.evaluation.get("score", 0)) < 60
        ][:3]

        return InterviewReport(
            session_id=session.session_id,
            overall_score=overall,
            radar=radar,
            highlights=[
                f"第 {t.index} 题表现较好"
                for t in turns
                if float(t.evaluation.get("score", 0)) >= 70
            ][:3],
            weak_points=weak_points,
            suggestions=[
                "回答时使用 STAR 结构：情境-任务-行动-结果",
                "每个观点尽量配合一个具体数字或事例",
                "针对薄弱知识点回到题库模块专项训练",
            ],
            retrain_links=[f"/quiz?knowledge_point={wp}" for wp in weak_points],
        )

    @staticmethod
    def _dim_score(turns: list[InterviewTurn], level: str) -> float:
        if not turns:
            return 0.0
        good = sum(1 for t in turns if t.evaluation.get("level") == level)
        return round(good / len(turns) * 100, 1)

    @staticmethod
    def _expression_score(turns: list[InterviewTurn]) -> float:
        if not turns:
            return 0.0
        avg_len = sum(len(t.answer.strip()) for t in turns) / len(turns)
        return round(min(100, avg_len), 1)

    @staticmethod
    def _pressure_score(session: InterviewSession) -> float:
        base = 70.0
        if session.mode == InterviewMode.PRESSURE:
            base += 10.0
        return base

    def _match_score(self, session: InterviewSession, turns: list[InterviewTurn]) -> float:
        if not turns:
            return 0.0
        return round(sum(float(t.evaluation.get("score", 0)) for t in turns) / len(turns), 1)

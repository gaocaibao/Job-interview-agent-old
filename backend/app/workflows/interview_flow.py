"""面试流程状态机。

状态流转：
    IDLE → INTRO → ASKING ⇄ LISTENING → EVALUATING
                        ↑          ↓
                        └─ FOLLOW_UP / TRANSITION
                                   ↓
                                 REPORT → DONE
"""

from app.schemas.interview import InterviewState
from app.workflows.base import StateMachine

TRANSITIONS: dict[InterviewState, set[InterviewState]] = {
    InterviewState.IDLE: {InterviewState.INTRO},
    InterviewState.INTRO: {InterviewState.ASKING},
    InterviewState.ASKING: {InterviewState.LISTENING},
    InterviewState.LISTENING: {InterviewState.EVALUATING},
    InterviewState.EVALUATING: {
        InterviewState.FOLLOW_UP,
        InterviewState.TRANSITION,
        InterviewState.REPORT,
    },
    InterviewState.FOLLOW_UP: {InterviewState.LISTENING},
    InterviewState.TRANSITION: {InterviewState.ASKING},
    InterviewState.REPORT: {InterviewState.DONE},
    InterviewState.DONE: set(),
}


class InterviewStateMachine(StateMachine):
    def __init__(self) -> None:
        super().__init__(
            initial=InterviewState.IDLE,
            transitions={k.value: {v.value for v in vs} for k, vs in TRANSITIONS.items()},
        )

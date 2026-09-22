"""通用状态机基类。"""

from app.core.errors import BadRequestError


class InvalidTransitionError(BadRequestError):
    code = "invalid_transition"
    message = "非法状态流转"


class StateMachine:
    """极简状态机：白名单式流转控制。"""

    def __init__(self, initial: str, transitions: dict[str, set[str]]):
        if initial not in transitions:
            raise ValueError(f"初始状态 {initial} 不在流转表中")
        self._state = initial
        self._transitions = transitions

    @property
    def state(self) -> str:
        return self._state

    def can(self, to_state: str) -> bool:
        return to_state in self._transitions.get(self._state, set())

    def to(self, to_state: str) -> str:
        if not self.can(to_state):
            raise InvalidTransitionError(f"不允许从 {self._state} 流转到 {to_state}")
        self._state = to_state
        return self._state

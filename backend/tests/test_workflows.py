"""面试状态机测试。"""

import pytest

from app.workflows.base import InvalidTransitionError
from app.workflows.interview_flow import InterviewStateMachine


def test_happy_path_transitions():
    sm = InterviewStateMachine()
    assert sm.state == "idle"
    path = ["intro", "asking", "listening", "evaluating", "transition", "asking", "listening"]
    for target in path:
        sm.to(target)
    assert sm.state == "listening"


def test_follow_up_path():
    sm = InterviewStateMachine()
    sm.to("intro")
    sm.to("asking")
    sm.to("listening")
    sm.to("evaluating")
    sm.to("follow_up")
    sm.to("listening")
    assert sm.state == "listening"


def test_invalid_transition_rejected():
    sm = InterviewStateMachine()
    with pytest.raises(InvalidTransitionError):
        sm.to("asking")  # idle 不能直接到 asking


def test_done_is_terminal():
    sm = InterviewStateMachine()
    for target in ["intro", "asking", "listening", "evaluating", "report", "done"]:
        sm.to(target)
    assert not sm.can("intro")

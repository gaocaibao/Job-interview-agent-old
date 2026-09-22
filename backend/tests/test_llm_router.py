"""LLM 路由测试：降级链、错误处理。"""

import pytest

from app.core.errors import ConfigError
from app.services.llm.base import ChatMessage, ChatResult, LLMProvider
from app.services.llm.router import LLMRouter


class FakeProvider(LLMProvider):
    def __init__(self, name: str, *, configured: bool = True, fail: bool = False):
        self.name = name
        self.api_key = "k" if configured else ""
        self._fail = fail

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages, model=None, **kwargs) -> ChatResult:
        if self._fail:
            raise RuntimeError("模拟故障")
        return ChatResult(content="ok", model=model or "m", provider=self.name)


def _router(**providers) -> LLMRouter:
    return LLMRouter(
        providers=providers,
        fallback_chain=["primary", "backup"],
        default_provider="primary",
    )


async def test_primary_success():
    router = _router(primary=FakeProvider("primary"), backup=FakeProvider("backup"))
    result = await router.chat([ChatMessage(role="user", content="hi")])
    assert result.provider == "primary"


async def test_fallback_on_failure():
    router = _router(primary=FakeProvider("primary", fail=True), backup=FakeProvider("backup"))
    result = await router.chat([ChatMessage(role="user", content="hi")])
    assert result.provider == "backup"


async def test_unconfigured_skipped():
    router = _router(
        primary=FakeProvider("primary", configured=False),
        backup=FakeProvider("backup"),
    )
    result = await router.chat([ChatMessage(role="user", content="hi")])
    assert result.provider == "backup"


async def test_no_provider_raises():
    router = _router(primary=FakeProvider("primary", configured=False))
    with pytest.raises(ConfigError):
        await router.chat([ChatMessage(role="user", content="hi")])


def test_available_providers():
    router = _router(
        primary=FakeProvider("primary", configured=False),
        backup=FakeProvider("backup"),
    )
    assert router.available_providers() == ["backup"]

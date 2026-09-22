"""LLM Provider 抽象基类。"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(slots=True)
class ChatMessage:
    role: str  # system / user / assistant
    content: str


@dataclass(slots=True)
class ChatResult:
    content: str
    model: str
    provider: str
    usage: dict = field(default_factory=dict)


class LLMProvider(ABC):
    """公有大模型 API 统一接口。"""

    name: str = "base"
    models: tuple[str, ...] = ()

    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        response_format: dict | None = None,
    ) -> ChatResult:
        """非流式对话补全。"""

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ):
        """流式对话补全，yield 增量文本。默认不支持。"""
        raise NotImplementedError(f"{self.name} 暂不支持流式输出")
        yield  # pragma: no cover

    def is_configured(self) -> bool:
        """是否已配置 API Key。"""
        return bool(getattr(self, "api_key", ""))

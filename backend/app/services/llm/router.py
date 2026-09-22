"""LLM 路由：按链降级 + 可观测。"""

from app.core.errors import ConfigError, ServiceUnavailableError
from app.core.logging import getLogger
from app.services.llm.base import ChatMessage, ChatResult, LLMProvider

logger = getLogger(__name__)


class LLMRouter:
    """多模型路由器。

    - 优先使用指定 Provider，失败时按 fallback_chain 依次降级
    - 未配置 Key 的 Provider 自动跳过
    """

    def __init__(
        self,
        providers: dict[str, LLMProvider],
        fallback_chain: list[str],
        default_provider: str,
    ):
        self._providers = providers
        self._fallback_chain = [p for p in fallback_chain if p in providers]
        self._default = default_provider

    def available_providers(self) -> list[str]:
        return [n for n, p in self._providers.items() if p.is_configured()]

    def _candidates(self, provider: str | None) -> list[LLMProvider]:
        order: list[str] = []
        if provider:
            order.append(provider)
        elif self._default:
            order.append(self._default)
        order.extend(self._fallback_chain)

        seen: set[str] = set()
        result: list[LLMProvider] = []
        for name in order:
            if name in seen or name not in self._providers:
                continue
            seen.add(name)
            p = self._providers[name]
            if p.is_configured():
                result.append(p)
        return result

    async def chat(
        self,
        messages: list[ChatMessage],
        provider: str | None = None,
        **kwargs,
    ) -> ChatResult:
        candidates = self._candidates(provider)
        if not candidates:
            raise ConfigError("没有可用的 LLM Provider，请检查 API Key 配置")

        last_error: Exception | None = None
        for p in candidates:
            try:
                result = await p.chat(messages, **kwargs)
                if p.name != candidates[0].name:
                    logger.info("LLM 降级: %s -> %s", candidates[0].name, p.name)
                return result
            except Exception as exc:  # noqa: BLE001 - 降级需要捕获全部异常
                last_error = exc
                logger.warning("LLM Provider %s 失败: %s", p.name, exc)
                continue
        raise ServiceUnavailableError(f"所有 LLM Provider 均失败: {last_error}")

"""OpenAI 兼容协议的通用 Provider 实现。

DeepSeek、StepFun（阶跃星辰）、豆包（火山方舟）均提供 OpenAI 兼容端点，
因此共享同一实现，仅通过配置区分。
"""

import json

import httpx

from app.core.errors import ServiceUnavailableError
from app.services.llm.base import ChatMessage, ChatResult, LLMProvider

_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, name: str, api_key: str, base_url: str, model: str):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.models = (model,) if model else ()
        self._default_model = model

    def is_configured(self) -> bool:
        return bool(self.api_key and self._default_model)

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        response_format: dict | None = None,
    ) -> ChatResult:
        payload: dict = {
            "model": model or self._default_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if response_format:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
            except httpx.HTTPError as exc:
                raise ServiceUnavailableError(f"{self.name} 网络错误: {exc}") from exc

        if resp.status_code != 200:
            raise ServiceUnavailableError(f"{self.name} 返回 {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        choice = data.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        if not content:
            raise ServiceUnavailableError(f"{self.name} 返回了空内容")
        return ChatResult(
            content=content,
            model=data.get("model", payload["model"]),
            provider=self.name,
            usage=data.get("usage", {}),
        )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ):
        payload = {
            "model": model or self._default_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                ) as resp:
                    if resp.status_code != 200:
                        body = await resp.aread()
                        raise ServiceUnavailableError(
                            f"{self.name} 返回 {resp.status_code}: {body[:200]!r}"
                        )
                    async for line in resp.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        chunk = line[len("data:") :].strip()
                        if chunk == "[DONE]":
                            break
                        try:
                            delta = json.loads(chunk)["choices"][0]["delta"]
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
                        text = delta.get("content")
                        if text:
                            yield text
            except httpx.HTTPError as exc:
                raise ServiceUnavailableError(f"{self.name} 流式网络错误: {exc}") from exc

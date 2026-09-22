"""LLM 客户端层：Provider 抽象 + 多模型路由降级。

设计要点：
- 统一 OpenAI 兼容协议（DeepSeek / StepFun / 豆包方舟均兼容）
- Provider 可插拔，新增模型只需注册一个配置
- 路由层按 fallback 链自动降级，单点故障不阻塞业务
"""

from app.services.llm.base import ChatMessage, ChatResult, LLMProvider
from app.services.llm.router import LLMRouter

__all__ = ["ChatMessage", "ChatResult", "LLMProvider", "LLMRouter"]

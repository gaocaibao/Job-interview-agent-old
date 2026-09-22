"""Provider 注册表：从配置创建 Provider 实例。"""

from app.config import Settings
from app.services.llm.providers.openai_compatible import OpenAICompatibleProvider


def create_providers(settings: Settings) -> dict[str, OpenAICompatibleProvider]:
    """按配置创建全部已知 Provider（未配置 Key 的也会创建，由路由层跳过）。"""
    return {
        "deepseek": OpenAICompatibleProvider(
            name="deepseek",
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            model=settings.deepseek_model,
        ),
        "stepfun": OpenAICompatibleProvider(
            name="stepfun",
            api_key=settings.stepfun_api_key,
            base_url=settings.stepfun_base_url,
            model=settings.stepfun_model,
        ),
        "doubao": OpenAICompatibleProvider(
            name="doubao",
            api_key=settings.doubao_api_key,
            base_url=settings.doubao_base_url,
            model=settings.doubao_model,
        ),
    }

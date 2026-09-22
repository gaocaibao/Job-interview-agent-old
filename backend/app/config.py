from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，全部支持环境变量覆盖。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # 应用
    app_name: str = "面训 AI"
    app_env: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # CORS
    cors_origins: str = "http://localhost:3000"

    # LLM Provider（公有大模型 API，按量计费）
    llm_default_provider: str = "deepseek"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    stepfun_api_key: str = ""
    stepfun_base_url: str = "https://api.stepfun.com/v1"
    stepfun_model: str = "step-2-16k"
    doubao_api_key: str = ""
    doubao_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    doubao_model: str = ""

    # LLM 路由：逗号分隔的有序降级链，如 "stepfun,deepseek,doubao"
    llm_fallback_chain: str = "stepfun,deepseek,doubao"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def fallback_chain(self) -> list[str]:
        return [p.strip() for p in self.llm_fallback_chain.split(",") if p.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

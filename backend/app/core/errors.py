"""统一错误体系：业务异常 + 全局异常处理器。"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """业务异常基类。"""

    code: str = "app_error"
    message: str = "服务内部错误"
    status_code: int = 500

    def __init__(self, message: str | None = None, detail: Any = None):
        self.message = message or self.message
        self.detail = detail
        super().__init__(self.message)


class BadRequestError(AppError):
    code = "bad_request"
    message = "请求参数错误"
    status_code = 400


class NotFoundError(AppError):
    code = "not_found"
    message = "资源不存在"
    status_code = 404


class ServiceUnavailableError(AppError):
    code = "service_unavailable"
    message = "依赖的模型服务暂不可用"
    status_code = 503


class ConfigError(AppError):
    code = "config_error"
    message = "服务配置缺失"
    status_code = 500


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
            },
        )

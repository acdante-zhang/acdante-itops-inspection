"""
Acdante ITOps - 健康检查中间件
用于监控API健康状态
"""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """健康检查中间件"""

    def __init__(self, app, health_path: str = "/api/v1/health"):
        super().__init__(app)
        self.health_path = health_path
        self.request_count = 0
        self.error_count = 0
        self.start_time = time.time()

    async def dispatch(self, request: Request, call_next):
        self.request_count += 1

        try:
            response = await call_next(request)
            if response.status_code >= 500:
                self.error_count += 1
            return response
        except Exception as e:
            self.error_count += 1
            logger.error(f"Request error: {e}")
            raise


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000

        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"duration={duration:.0f}ms"
        )

        return response

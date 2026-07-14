"""
Acdante ITOps Inspection Platform - FastAPI 主入口
v3.1.0 - 真实巡检引擎版本
"""

import sys
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api.real_routes import router
from backend.api.pacs_routes import router as pacs_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 初始化数据库
    from backend.core.database import init_db, seed_builtin_templates
    init_db()
    seed_builtin_templates()
    logger.info("数据库已初始化，内置模板已加载")

    # 启动调度器
    from backend.core.scheduler import task_scheduler
    task_scheduler.start()
    logger.info("巡检任务调度器已启动")

    logger.info("Acdante ITOps 后端服务已启动 (v3.1.0)")
    logger.info("巡检引擎: SSH + SNMP + DBCheck + HTTP")
    logger.info("数据库: SQLite")

    yield

    task_scheduler.stop()
    logger.info("Acdante ITOps 后端服务已关闭")


app = FastAPI(
    title="Acdante ITOps Inspection Platform",
    description="企业级IT基础设施巡检平台 API\n\n"
                "核心能力:\n"
                "- SSH巡检: Linux/Windows/AIX/网络设备\n"
                "- SNMP巡检: v1/v2c/v3, 136+内置OID\n"
                "- DBCheck巡检: 10种数据库, 130+规则\n"
                "- HTTP巡检: 防火墙/安全设备Web API\n"
                "- 定时调度: APScheduler\n"
                "- 报告生成: DOCX/PDF/HTML",
    version="3.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(pacs_router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PYTHON_API_PORT", 8000))
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )

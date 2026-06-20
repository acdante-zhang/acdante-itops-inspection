# Oracle ADG 容灾管控平台 - FastAPI 主入口
# Acdante DR Console Backend Server

import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api.routes import router
from backend.services.dg_service import get_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据
    get_store()
    print("[Acdante ITOps] 后端服务已启动")
    print("[Acdante ITOps] SNMP采集引擎 + 报告生成引擎已就绪")
    yield
    print("[Acdante ITOps] 后端服务关闭")


app = FastAPI(
    title="Acdante ITOps Inspection Platform",
    description="企业级IT基础设施巡检平台 API\n\n"
                "核心能力:\n"
                "- 多协议巡检: SSH/SNMP/JDBC/Redfish/HTTP\n"
                "- 巡检模板: 50+内置设备模板(华为/华三/思科/Dell/F5等)\n"
                "- 报告生成: DOCX/PDF/HTML多格式报告\n"
                "- SNMP采集: 支持v1/v2c/v3, 300+内置OID\n\n"
                "支持 Oracle 10g/11g/19c/23c/26ai 全版本",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


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

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
    print("[Acdante DR Console] 后端服务已启动")
    print("[Acdante DR Console] 四层容灾架构: 存储->虚拟化->ADG->K8s")
    yield
    print("[Acdante DR Console] 后端服务关闭")


app = FastAPI(
    title="Acdante DR Console",
    description="Oracle ADG 容灾管控与可视化搭建平台 API\n\n"
                "基于 Acdante 四层云原生容灾架构:\n"
                "- L1 存储层: ZFS快照/秒级回滚/LZ4+ZSTD压缩\n"
                "- L2 虚拟化层: KVM/QEMU/资源隔离\n"
                "- L3 数据库层: ADG实时同步/DG配置/FSFO\n"
                "- L4 编排层: K8s+OpenShift/自动切换/生命周期托管\n\n"
                "支持 Oracle 10g/11g/19c/23c/26ai 全版本",
    version="1.0.0",
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

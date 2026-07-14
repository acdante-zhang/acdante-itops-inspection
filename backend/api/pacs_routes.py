"""
Acdante ITOps - PACS-AI 影像质控健康检查 API
专门针对PACS-AI系统的健康检查端点
"""

from __future__ import annotations
from typing import Optional
import time
import logging

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/pacs")


@router.get("/health", tags=["PACS-AI"])
async def pacs_health_check():
    """PACS-AI系统整体健康检查"""
    return {
        "status": "healthy",
        "service": "PACS-AI Inspection Module",
        "version": "1.0.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modules": {
            "ssh_engine": "available",
            "snmp_engine": "available",
            "dbcheck_engine": "available",
            "report_engine": "available",
            "scheduler": "running",
        },
    }


@router.get("/gpu/status", tags=["PACS-AI"])
async def get_gpu_status():
    """获取GPU状态（通过SSH巡检）"""
    return {
        "message": "请通过 /api/v1/tasks/:id/run 执行GPU巡检任务",
        "template_id": "pacs-ai-gpu-server-v1",
        "endpoints": {
            "run_inspection": "POST /api/v1/tasks/{task_id}/run",
            "get_results": "GET /api/v1/results?task_id={task_id}",
        },
    }


@router.get("/templates", tags=["PACS-AI"])
async def list_pacs_templates():
    """获取PACS-AI专用巡检模板"""
    from backend.templates.pacs_ai_templates import get_pacs_templates
    templates = get_pacs_templates()
    return {
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "item_count": len(t.items),
            }
            for t in templates
        ],
        "total": len(templates),
    }


@router.post("/inspect/gpu", tags=["PACS-AI"])
async def inspect_gpu(req: dict):
    """快速GPU巡检"""
    from backend.core.ssh_executor import SSHExecutor, SSHConfig, SSHAuthType
    from backend.templates.pacs_ai_templates import GPU_SERVER_TEMPLATE

    host = req.get("host", "")
    if not host:
        raise HTTPException(status_code=400, detail="host参数必填")

    config = SSHConfig(
        host=host,
        port=req.get("port", 22),
        username=req.get("username", "root"),
        password=req.get("password", ""),
        timeout=req.get("timeout", 30),
        device_type="linux",
    )

    executor = SSHExecutor(config)
    commands = [
        {"command": item["command"], "name": item["name"], "timeout": 30}
        for item in GPU_SERVER_TEMPLATE.items
    ]

    result = executor.execute_batch(commands)

    return {
        "host": host,
        "connected": result.connected,
        "timestamp": result.timestamp,
        "total_items": result.total_commands,
        "success_count": result.success_count,
        "error_count": result.error_count,
        "duration_ms": result.total_duration_ms,
        "results": [
            {
                "name": r.command,
                "value": r.stdout[:500] if r.status == "success" else r.error_message,
                "status": r.status,
                "duration_ms": r.duration_ms,
            }
            for r in result.commands
        ],
    }


@router.post("/inspect/vllm", tags=["PACS-AI"])
async def inspect_vllm(req: dict):
    """快速vLLM服务巡检"""
    from backend.core.ssh_executor import SSHExecutor, SSHConfig
    from backend.templates.pacs_ai_templates import VLLM_SERVICE_TEMPLATE

    host = req.get("host", "")
    if not host:
        raise HTTPException(status_code=400, detail="host参数必填")

    config = SSHConfig(
        host=host,
        port=req.get("port", 22),
        username=req.get("username", "root"),
        password=req.get("password", ""),
        timeout=req.get("timeout", 30),
        device_type="linux",
    )

    executor = SSHExecutor(config)
    commands = [
        {"command": item["command"], "name": item["name"], "timeout": 30}
        for item in VLLM_SERVICE_TEMPLATE.items
    ]

    result = executor.execute_batch(commands)

    return {
        "host": host,
        "connected": result.connected,
        "timestamp": result.timestamp,
        "total_items": result.total_commands,
        "success_count": result.success_count,
        "results": [
            {
                "name": r.command,
                "value": r.stdout[:500] if r.status == "success" else r.error_message,
                "status": r.status,
            }
            for r in result.commands
        ],
    }


@router.post("/inspect/pacs", tags=["PACS-AI"])
async def inspect_pacs_system(req: dict):
    """快速PACS系统巡检"""
    from backend.core.ssh_executor import SSHExecutor, SSHConfig
    from backend.templates.pacs_ai_templates import PACS_SYSTEM_TEMPLATE

    host = req.get("host", "")
    if not host:
        raise HTTPException(status_code=400, detail="host参数必填")

    config = SSHConfig(
        host=host,
        port=req.get("port", 22),
        username=req.get("username", "root"),
        password=req.get("password", ""),
        timeout=req.get("timeout", 30),
        device_type="linux",
    )

    executor = SSHExecutor(config)
    commands = [
        {"command": item["command"], "name": item["name"], "timeout": 30}
        for item in PACS_SYSTEM_TEMPLATE.items
    ]

    result = executor.execute_batch(commands)

    return {
        "host": host,
        "connected": result.connected,
        "timestamp": result.timestamp,
        "total_items": result.total_commands,
        "success_count": result.success_count,
        "results": [
            {
                "name": r.command,
                "value": r.stdout[:500] if r.status == "success" else r.error_message,
                "status": r.status,
            }
            for r in result.commands
        ],
    }

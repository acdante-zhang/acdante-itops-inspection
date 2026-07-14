"""
Acdante ITOps - 真实 API 路由
连接前端与后端巡检引擎
"""

from __future__ import annotations
from typing import Optional
import json
import time
import logging

from fastapi import APIRouter, Query, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")


# ============================================================
# 仪表盘
# ============================================================

@router.get("/dashboard/stats", tags=["仪表盘"])
async def dashboard_stats():
    """获取仪表盘统计数据"""
    from backend.core.database import get_dashboard_stats
    return get_dashboard_stats()


# ============================================================
# 巡检对象 CRUD
# ============================================================

@router.get("/targets", tags=["巡检对象"])
async def list_targets(type: Optional[str] = Query(default=None)):
    from backend.core.database import get_targets
    targets = get_targets(type)
    return {"targets": targets}


@router.get("/targets/{target_id}", tags=["巡检对象"])
async def get_target(target_id: int):
    from backend.core.database import get_target
    t = get_target(target_id)
    if not t:
        raise HTTPException(status_code=404, detail="巡检对象不存在")
    return t


@router.post("/targets", tags=["巡检对象"])
async def create_target(data: dict):
    from backend.core.database import create_target
    return create_target(data)


@router.put("/targets/{target_id}", tags=["巡检对象"])
async def update_target(target_id: int, data: dict):
    from backend.core.database import update_target
    t = update_target(target_id, data)
    if not t:
        raise HTTPException(status_code=404, detail="巡检对象不存在")
    return t


@router.delete("/targets/{target_id}", tags=["巡检对象"])
async def delete_target(target_id: int):
    from backend.core.database import delete_target
    delete_target(target_id)
    return {"message": "已删除"}


@router.post("/targets/{target_id}/test", tags=["巡检对象"])
async def test_target_connection(target_id: int):
    """测试巡检对象连接"""
    from backend.core.database import get_target
    from backend.core.ssh_executor import SSHExecutor, SSHConfig, SSHAuthType

    target = get_target(target_id)
    if not target:
        raise HTTPException(status_code=404, detail="巡检对象不存在")

    protocol = target.get("protocol", "ssh")

    if protocol == "ssh":
        config = SSHConfig(
            host=target.get("host", ""),
            port=target.get("port", 22),
            username=target.get("username", ""),
            password=target.get("password_enc", ""),
            timeout=target.get("timeout", 30),
            device_type=target.get("device_type", "linux"),
        )
        executor = SSHExecutor(config)
        return executor.test_connection()

    elif protocol == "snmp":
        from backend.snmp_engine.snmp_collector import SNMPCollector, SNMPConfig, SNMPVersion
        version_map = {"v1": SNMPVersion.V1, "v2c": SNMPVersion.V2C, "v3": SNMPVersion.V3}
        config = SNMPConfig(
            host=target.get("host", ""),
            port=target.get("port", 161),
            version=version_map.get(target.get("snmp_version", "v2c"), SNMPVersion.V2C),
            community=target.get("community", "public"),
            timeout=target.get("timeout", 5),
        )
        collector = SNMPCollector(config)
        return collector.test_connection()

    else:
        return {"success": True, "message": f"协议 {protocol} 连接测试（模拟）"}


# ============================================================
# 巡检模板
# ============================================================

@router.get("/templates", tags=["巡检模板"])
async def list_templates(type: Optional[str] = Query(default=None)):
    from backend.core.database import get_templates
    templates = get_templates(type)
    return {"templates": templates}


@router.get("/templates/{template_id}", tags=["巡检模板"])
async def get_template(template_id: str):
    from backend.core.database import get_template
    t = get_template(template_id)
    if not t:
        raise HTTPException(status_code=404, detail="模板不存在")
    return t


# ============================================================
# 巡检任务
# ============================================================

@router.get("/tasks", tags=["巡检任务"])
async def list_tasks():
    from backend.core.database import get_tasks
    return {"tasks": get_tasks()}


@router.get("/tasks/{task_id}", tags=["巡检任务"])
async def get_task(task_id: str):
    from backend.core.database import get_task
    t = get_task(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    return t


@router.post("/tasks", tags=["巡检任务"])
async def create_task(data: dict):
    from backend.core.database import create_task
    return create_task(data)


@router.put("/tasks/{task_id}", tags=["巡检任务"])
async def update_task(task_id: str, data: dict):
    from backend.core.database import update_task
    t = update_task(task_id, data)
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    return t


@router.delete("/tasks/{task_id}", tags=["巡检任务"])
async def delete_task(task_id: str):
    from backend.core.database import delete_task
    from backend.core.scheduler import task_scheduler
    task_scheduler.remove_task(task_id)
    delete_task(task_id)
    return {"message": "已删除"}


@router.post("/tasks/{task_id}/run", tags=["巡检任务"])
async def run_task(task_id: str):
    """触发巡检任务执行"""
    from backend.core.database import get_task, get_target, get_template, update_task, save_inspection_result
    from backend.core.inspect_engine import inspect_engine

    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    template = get_template(task.get("template_id", ""))
    if not template:
        raise HTTPException(status_code=400, detail="关联模板不存在")

    target_ids = task.get("target_ids", [])
    if not target_ids:
        raise HTTPException(status_code=400, detail="未指定巡检对象")

    # 更新任务状态
    update_task(task_id, {"status": "running", "last_run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})

    # 执行巡检
    all_results = []
    for tid in target_ids:
        target = get_target(tid)
        if not target:
            continue

        result = inspect_engine.execute_inspection(
            task_id=task_id,
            task_name=task.get("name", ""),
            target={
                "id": target.get("id"),
                "name": target.get("name"),
                "host": target.get("host"),
                "port": target.get("port"),
                "protocol": target.get("protocol", "ssh"),
                "username": target.get("username"),
                "password": target.get("password_enc", ""),
                "device_type": target.get("device_type", "linux"),
                "timeout": target.get("timeout", 30),
            },
            template_items=template.get("items", []),
        )

        # 保存结果
        save_inspection_result({
            "task_id": task_id,
            "target_id": target.get("id"),
            "target_name": target.get("name"),
            "items": [
                {
                    "item_id": item.item_id,
                    "item_name": item.item_name,
                    "category": item.category,
                    "raw_value": item.raw_value,
                    "parsed_value": item.parsed_value,
                    "status": item.status,
                    "threshold_desc": item.threshold_desc,
                    "suggestion": item.suggestion,
                    "duration_ms": item.duration_ms,
                }
                for item in result.items
            ],
        })

        all_results.append({
            "target_id": target.get("id"),
            "target_name": target.get("name"),
            "status": result.status,
            "health_score": result.health_score,
            "total_items": result.total_items,
            "ok_count": result.ok_count,
            "warning_count": result.warning_count,
            "critical_count": result.critical_count,
            "error_count": result.error_count,
            "duration_ms": result.total_duration_ms,
            "items": [
                {
                    "item_id": item.item_id,
                    "item_name": item.item_name,
                    "category": item.category,
                    "raw_value": item.raw_value[:500],
                    "status": item.status,
                    "suggestion": item.suggestion,
                    "duration_ms": item.duration_ms,
                }
                for item in result.items
            ],
        })

    # 更新任务状态
    update_task(task_id, {"status": "completed"})

    return {
        "task_id": task_id,
        "task_name": task.get("name"),
        "results": all_results,
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


# ============================================================
# 巡检结果
# ============================================================

@router.get("/results", tags=["巡检结果"])
async def list_results(
    task_id: Optional[str] = Query(default=None),
    target_id: Optional[int] = Query(default=None),
    limit: int = Query(default=200, le=1000),
):
    from backend.core.database import get_results
    return {"results": get_results(task_id, target_id, limit)}


# ============================================================
# 报告
# ============================================================

@router.get("/reports", tags=["报告"])
async def list_reports():
    from backend.core.database import get_reports
    return {"reports": get_reports()}


@router.get("/reports/{report_id}", tags=["报告"])
async def get_report(report_id: str):
    from backend.core.database import get_report
    r = get_report(report_id)
    if not r:
        raise HTTPException(status_code=404, detail="报告不存在")
    return r


# ============================================================
# 知识库
# ============================================================

@router.get("/knowledge", tags=["知识库"])
async def list_knowledge():
    """知识库条目（静态）"""
    return {"entries": [
        {"id": "kb-001", "title": "Oracle锁阻塞排查指南", "category": "数据库", "target_type": "oracle",
         "symptom": "会话等待enq: TX - row lock contention", "solution": "1. 查询V$SESSION定位阻塞源\n2. ALTER SYSTEM KILL SESSION", "severity": "critical", "tags": ["Oracle", "锁"]},
        {"id": "kb-002", "title": "Linux磁盘使用率告警处理", "category": "操作系统", "target_type": "linux",
         "symptom": "磁盘使用率超过80%", "solution": "1. du -sh /* | sort -rh\n2. 清理旧日志\n3. 扩容", "severity": "warning", "tags": ["Linux", "磁盘"]},
        {"id": "kb-003", "title": "GPU显存不足处理", "category": "GPU", "target_type": "linux",
         "symptom": "GPU显存使用率超过90%", "solution": "1. nvidia-smi查看进程\n2. 清理僵尸进程\n3. 降低batch_size", "severity": "critical", "tags": ["GPU", "AI"]},
    ]}


# ============================================================
# SNMP 巡检
# ============================================================

@router.get("/snmp/templates", tags=["SNMP巡检"])
async def list_snmp_templates(brand: Optional[str] = None, device_type: Optional[str] = None):
    try:
        from backend.snmp_engine.snmp_templates import SNMPTemplates
        if brand:
            templates = SNMPTemplates.get_templates_by_brand(brand)
        elif device_type:
            templates = SNMPTemplates.get_templates_by_type(device_type)
        else:
            templates = SNMPTemplates.get_all_templates()
        return {"templates": [SNMPTemplates.to_dict(t) for t in templates], "total": len(templates)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/snmp/test", tags=["SNMP巡检"])
async def test_snmp_connection(req: dict):
    try:
        from backend.snmp_engine.snmp_collector import SNMPCollector, SNMPConfig, SNMPVersion
        version_map = {"v1": SNMPVersion.V1, "v2c": SNMPVersion.V2C, "v3": SNMPVersion.V3}
        config = SNMPConfig(
            host=req.get("host", "127.0.0.1"),
            port=req.get("port", 161),
            version=version_map.get(req.get("version", "v2c"), SNMPVersion.V2C),
            community=req.get("community", "public"),
            timeout=req.get("timeout", 5),
        )
        collector = SNMPCollector(config)
        return collector.test_connection()
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/snmp/collect", tags=["SNMP巡检"])
async def collect_snmp_data(req: dict):
    try:
        from backend.snmp_engine.snmp_collector import SNMPCollector, SNMPConfig, SNMPVersion
        version_map = {"v1": SNMPVersion.V1, "v2c": SNMPVersion.V2C, "v3": SNMPVersion.V3}
        config = SNMPConfig(
            host=req.get("host", "127.0.0.1"),
            port=req.get("port", 161),
            version=version_map.get(req.get("version", "v2c"), SNMPVersion.V2C),
            community=req.get("community", "public"),
            timeout=req.get("timeout", 5),
        )
        collector = SNMPCollector(config)
        oids = req.get("oids", [])
        result = collector.collect_from_registry(oids)
        return {
            "host": result.host, "timestamp": result.timestamp,
            "total_items": result.total_items, "success_count": result.success_count,
            "failed_count": result.failed_count, "total_time_ms": result.total_time_ms,
            "results": [{"oid": r.oid, "name": r.name, "value": r.value, "status": r.status} for r in result.results],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# DBCheck
# ============================================================

@router.get("/dbcheck/db-types", tags=["DBCheck"])
async def list_dbcheck_types():
    try:
        from backend.dbcheck_bridge import DBCheckWrapper
        wrapper = DBCheckWrapper()
        return {"db_types": wrapper.get_supported_db_types(), "version": wrapper.get_version()}
    except Exception as e:
        return {"db_types": [], "version": "unavailable", "error": str(e)}


@router.post("/dbcheck/inspect", tags=["DBCheck"])
async def run_dbcheck_inspect(req: dict):
    try:
        from backend.dbcheck_bridge import DBCheckWrapper
        wrapper = DBCheckWrapper()
        result = wrapper.inspect(
            db_type=req.get("db_type", "mysql"),
            host=req.get("host", "localhost"),
            port=req.get("port", 3306),
            user=req.get("user", "root"),
            password=req.get("password", ""),
            db_name=req.get("db_name", ""),
        )
        return {
            "success": result.success, "health_score": result.health_score,
            "total_items": result.total_items, "ok_count": result.ok_count,
            "warning_count": result.warning_count, "critical_count": result.critical_count,
            "results": result.results, "errors": result.errors,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 报告生成
# ============================================================

@router.post("/reports/generate", tags=["报告"])
async def generate_report_api(req: dict):
    try:
        from backend.report_engine.report_generator import generate_report
        result = generate_report(
            task_name=req.get("task_name", "巡检报告"),
            task_id=req.get("task_id", ""),
            targets=req.get("targets", []),
            results=req.get("results", []),
            format=req.get("format", "all"),
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# 系统
# ============================================================

@router.get("/health", tags=["系统"])
async def health_check():
    return {"status": "healthy", "service": "Acdante ITOps Inspection", "version": "3.1.0"}

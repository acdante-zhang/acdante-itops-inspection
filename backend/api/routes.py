# Oracle ADG 容灾管控平台 - API路由定义
# REST API端点，供前端调用

from __future__ import annotations
from typing import Optional

from fastapi import APIRouter, Query, HTTPException

from backend.models.schemas import (
    OracleVersion, DGType, DGProtectionMode, LogType, TakeoverType,
    DGSetupRequest, TakeoverRequest,
)
from backend.services.dg_service import DGService, get_store

router = APIRouter(prefix="/api/v1")


# ============================================================
# 仪表盘 API
# ============================================================

@router.get("/dashboard/stats", tags=["仪表盘"])
async def get_dashboard_stats():
    """获取仪表盘统计数据"""
    return DGService.get_dashboard_stats()


@router.get("/dashboard/alerts", tags=["仪表盘"])
async def get_dashboard_alerts(limit: int = Query(default=10, le=50)):
    """获取最新告警"""
    store = get_store()
    return store.alert_logs[:limit]


# ============================================================
# Oracle 实例 API
# ============================================================

@router.get("/instances", tags=["实例"])
async def list_instances(
    role: Optional[str] = Query(default=None, description="按角色过滤(primary/standby)"),
    health: Optional[str] = Query(default=None, description="按健康状态过滤"),
):
    """列出所有Oracle实例"""
    store = get_store()
    instances = list(store.instances.values())
    if role:
        instances = [i for i in instances if i.role.value == role]
    if health:
        instances = [i for i in instances if i.health.value == health]
    return instances


@router.get("/instances/{instance_id}", tags=["实例"])
async def get_instance(instance_id: str):
    """获取单个实例详情"""
    store = get_store()
    inst = store.instances.get(instance_id)
    if not inst:
        raise HTTPException(status_code=404, detail=f"实例 {instance_id} 不存在")
    return inst


# ============================================================
# DG 配置 API
# ============================================================

@router.get("/dg-configs", tags=["DG配置"])
async def list_dg_configs(health: Optional[str] = Query(default=None)):
    """列出所有DG配置"""
    store = get_store()
    configs = list(store.dg_configs.values())
    if health:
        configs = [c for c in configs if c.health.value == health]
    return configs


@router.get("/dg-configs/version-matrix", tags=["DG配置"])
async def get_version_matrix():
    """获取Oracle版本特性支持矩阵"""
    return DGService.get_version_matrix()


@router.get("/dg-configs/{config_id}", tags=["DG配置"])
async def get_dg_config(config_id: str):
    """获取单个DG配置详情"""
    store = get_store()
    cfg = store.dg_configs.get(config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail=f"DG配置 {config_id} 不存在")
    return cfg


@router.post("/dg-configs/setup-plan", tags=["DG配置"])
async def generate_setup_plan(req: DGSetupRequest):
    """生成DG搭建执行计划"""
    # 版本校验
    if req.oracle_version == OracleVersion.ORACLE_10G:
        if req.dg_type in (DGType.ADG, DGType.FSFO):
            raise HTTPException(
                status_code=400,
                detail="Oracle 10g 不支持 ADG/FSFO，仅支持物理DG"
            )
        if req.enable_fsfo:
            raise HTTPException(
                status_code=400,
                detail="Oracle 10g 不支持 FSFO"
            )

    return DGService.generate_setup_plan(
        config_name=req.config_name,
        dg_type=req.dg_type,
        oracle_version=req.oracle_version,
        protection_mode=req.protection_mode,
        fsfo_enabled=req.enable_fsfo,
    )


# ============================================================
# 同步监控 API
# ============================================================

@router.get("/sync/logs", tags=["同步监控"])
async def list_sync_logs(
    dg_config_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, le=200),
):
    """获取同步日志"""
    store = get_store()
    logs = store.sync_logs
    if dg_config_id:
        logs = [l for l in logs if l.dg_config_id == dg_config_id]
    if status:
        logs = [l for l in logs if l.status.value == status]
    return logs[:limit]


@router.get("/sync/overview", tags=["同步监控"])
async def get_sync_overview():
    """获取所有DG配置的同步状态概览"""
    store = get_store()
    result = []
    for cfg in store.dg_configs.values():
        primary = store.instances.get(cfg.primary_id)
        standbys = [store.instances.get(sid) for sid in cfg.standby_ids]
        standbys = [s for s in standbys if s is not None]
        result.append({
            "dg_config": cfg,
            "primary": primary,
            "standbys": standbys,
        })
    return result


# ============================================================
# 容灾接管 API
# ============================================================

@router.post("/takeover/validate", tags=["容灾接管"])
async def validate_takeover(req: TakeoverRequest):
    """验证容灾接管是否可执行"""
    return DGService.validate_takeover(req.dg_config_id, req.operation)


@router.post("/takeover/execute", tags=["容灾接管"])
async def execute_takeover(req: TakeoverRequest):
    """执行容灾接管（模拟）"""
    validation = DGService.validate_takeover(req.dg_config_id, req.operation)
    if not validation.can_proceed and not req.force:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "容灾接管预检未通过",
                "errors": validation.errors,
                "warnings": validation.warnings,
            }
        )
    store = get_store()
    cfg = store.dg_configs.get(req.dg_config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="DG配置不存在")
    primary = store.instances.get(cfg.primary_id)
    standby = store.instances.get(cfg.standby_ids[0]) if cfg.standby_ids else None
    # 模拟操作记录
    return {
        "success": True,
        "operation": req.operation.value,
        "dg_config": cfg.name,
        "source": primary.name if primary else "N/A",
        "target": standby.name if standby else "N/A",
        "message": f"{req.operation.value} 操作已提交（模拟），请监控执行进度",
    }


@router.get("/takeover/history", tags=["容灾接管"])
async def list_failover_history(limit: int = Query(default=20, le=100)):
    """获取容灾操作历史"""
    store = get_store()
    return store.failover_history[:limit]


# ============================================================
# 性能监控 API
# ============================================================

@router.get("/performance/{instance_id}", tags=["性能监控"])
async def get_performance(
    instance_id: str,
    minutes: int = Query(default=30, le=60, description="查询时间范围(分钟)"),
):
    """获取实例性能指标"""
    store = get_store()
    if instance_id not in store.instances:
        raise HTTPException(status_code=404, detail=f"实例 {instance_id} 不存在")
    return DGService.get_instance_performance(instance_id, minutes)


@router.get("/performance/summary/all", tags=["性能监控"])
async def get_performance_summary():
    """获取所有实例性能概览"""
    store = get_store()
    result = []
    for inst_id, inst in store.instances.items():
        metrics = store.performance_metrics.get(inst_id, [])
        latest = metrics[-1] if metrics else None
        result.append({
            "instance_id": inst_id,
            "instance_name": inst.name,
            "version": inst.version.value,
            "role": inst.role.value,
            "health": inst.health.value,
            "cpu_usage": latest.cpu_usage if latest else 0,
            "memory_usage": latest.memory_usage if latest else 0,
            "redo_rate": latest.redo_rate if latest else 0,
            "apply_rate": latest.apply_rate if latest else 0,
        })
    return result


# ============================================================
# 日志 API
# ============================================================

@router.get("/logs", tags=["日志"])
async def list_logs(
    log_type: Optional[str] = Query(default=None, description="日志类型(alert/dg_broker/sync/audit)"),
    level: Optional[str] = Query(default=None, description="日志级别(INFO/WARNING/ERROR/CRITICAL)"),
    limit: int = Query(default=50, le=200),
):
    """获取日志列表"""
    store = get_store()
    # 根据日志类型返回不同数据
    if log_type == "alert" or log_type == "dg_broker":
        logs = store.alert_logs
        if level:
            logs = [l for l in logs if l.level.value == level]
        return logs[:limit]
    elif log_type == "sync":
        logs = store.sync_logs
        return logs[:limit]
    elif log_type == "audit":
        logs = store.audit_logs
        return logs[:limit]
    else:
        # 默认返回通用日志条目
        entries = DGService.get_logs(None, limit)
        if level:
            entries = [e for e in entries if e.level.value == level]
        return entries


# ============================================================
# 基础设施 API
# ============================================================

@router.get("/infrastructure/zfs", tags=["基础设施"])
async def list_zfs_datasets():
    """列出ZFS数据集"""
    store = get_store()
    return store.zfs_datasets


@router.get("/infrastructure/k8s", tags=["基础设施"])
async def list_k8s_resources(namespace: Optional[str] = Query(default=None)):
    """列出K8s资源"""
    store = get_store()
    resources = store.k8s_resources
    if namespace:
        resources = [r for r in resources if r.namespace == namespace]
    return resources


# ============================================================
# 系统 API
# ============================================================

@router.get("/health", tags=["系统"])
async def health_check():
    """系统健康检查"""
    return {"status": "healthy", "service": "acdante-shield", "version": "1.0.0"}

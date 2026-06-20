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


# ============================================================
# SNMP 巡检 API
# ============================================================

@router.get("/snmp/templates", tags=["SNMP巡检"])
async def list_snmp_templates(brand: Optional[str] = Query(default=None), device_type: Optional[str] = Query(default=None)):
    """获取SNMP设备巡检模板列表"""
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
        raise HTTPException(status_code=500, detail=f"获取SNMP模板失败: {str(e)}")


@router.get("/snmp/templates/{template_id}", tags=["SNMP巡检"])
async def get_snmp_template(template_id: str):
    """获取指定SNMP模板详情"""
    try:
        from backend.snmp_engine.snmp_templates import SNMPTemplates
        template = SNMPTemplates.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"SNMP模板 {template_id} 不存在")
        return SNMPTemplates.to_dict(template)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板详情失败: {str(e)}")


@router.get("/snmp/oids", tags=["SNMP巡检"])
async def list_snmp_oids(vendor: Optional[str] = Query(default=None), keyword: Optional[str] = Query(default=None)):
    """获取SNMP OID注册表"""
    try:
        from backend.snmp_engine.snmp_oid_registry import SNMPOIDRegistry
        registry = SNMPOIDRegistry()
        if keyword:
            results = registry.search_oid(keyword)
            return {"oids": results, "total": len(results)}
        elif vendor:
            flat_list = registry.get_flat_oid_list(vendor)
            return {"vendor": vendor, "oids": flat_list, "total": len(flat_list)}
        else:
            return {"vendors": registry.list_vendors(), "registry": registry.get_all_oids()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取OID注册表失败: {str(e)}")


@router.post("/snmp/test", tags=["SNMP巡检"])
async def test_snmp_connection(req: dict):
    """测试SNMP连接"""
    try:
        from backend.snmp_engine.snmp_collector import SNMPCollector, SNMPConfig, SNMPVersion
        version_map = {"v1": SNMPVersion.V1, "v2c": SNMPVersion.V2C, "v3": SNMPVersion.V3}
        config = SNMPConfig(
            host=req.get("host", "127.0.0.1"),
            port=req.get("port", 161),
            version=version_map.get(req.get("version", "v2c"), SNMPVersion.V2C),
            community=req.get("community", "public"),
            username=req.get("username", ""),
            auth_protocol=req.get("auth_protocol", ""),
            auth_password=req.get("auth_password", ""),
            priv_protocol=req.get("priv_protocol", ""),
            priv_password=req.get("priv_password", ""),
            timeout=req.get("timeout", 5),
        )
        collector = SNMPCollector(config)
        result = collector.test_connection()
        return result
    except Exception as e:
        return {"success": False, "message": f"连接测试失败: {str(e)}"}


@router.post("/snmp/collect", tags=["SNMP巡检"])
async def collect_snmp_data(req: dict):
    """采集SNMP数据"""
    try:
        from backend.snmp_engine.snmp_collector import SNMPCollector, SNMPConfig, SNMPVersion
        from backend.snmp_engine.snmp_templates import SNMPTemplates
        
        version_map = {"v1": SNMPVersion.V1, "v2c": SNMPVersion.V2C, "v3": SNMPVersion.V3}
        config = SNMPConfig(
            host=req.get("host", "127.0.0.1"),
            port=req.get("port", 161),
            version=version_map.get(req.get("version", "v2c"), SNMPVersion.V2C),
            community=req.get("community", "public"),
            username=req.get("username", ""),
            timeout=req.get("timeout", 5),
            retries=req.get("retries", 2),
        )
        
        collector = SNMPCollector(config)
        
        # 如果指定了模板ID，从模板获取OID列表
        template_id = req.get("template_id")
        if template_id:
            template = SNMPTemplates.get_template(template_id)
            if not template:
                raise HTTPException(status_code=404, detail=f"模板 {template_id} 不存在")
            oid_list = [{"oid": item.oid, "name": item.name, "type": item.oid_type} for item in template.items]
        else:
            # 否则使用请求中的OID列表
            oid_list = req.get("oids", [])
        
        if not oid_list:
            raise HTTPException(status_code=400, detail="未指定要采集的OID")
        
        result = collector.collect_from_registry(oid_list)
        
        return {
            "host": result.host,
            "timestamp": result.timestamp,
            "total_items": result.total_items,
            "success_count": result.success_count,
            "failed_count": result.failed_count,
            "total_time_ms": result.total_time_ms,
            "results": [
                {
                    "oid": r.oid,
                    "name": r.name,
                    "value": r.value,
                    "type": r.type,
                    "status": r.status,
                    "error_message": r.error_message,
                    "response_time_ms": r.response_time_ms,
                }
                for r in result.results
            ],
            "errors": result.errors,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SNMP采集失败: {str(e)}")


@router.post("/snmp/walk", tags=["SNMP巡检"])
async def snmp_walk(req: dict):
    """SNMP Walk操作"""
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
        base_oid = req.get("base_oid", "1.3.6.1.2.1.1")
        max_iterations = req.get("max_iterations", 100)
        
        results = collector.snmp_walk(base_oid, max_iterations)
        
        return {
            "base_oid": base_oid,
            "count": len(results),
            "results": [
                {"oid": r.oid, "name": r.name, "value": r.value, "type": r.type}
                for r in results
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SNMP Walk失败: {str(e)}")


# ============================================================
# 报告生成 API
# ============================================================

@router.post("/reports/generate", tags=["报告生成"])
async def generate_report_api(req: dict):
    """生成巡检报告（支持DOCX/PDF）"""
    try:
        from backend.report_engine.report_generator import generate_report
        
        task_name = req.get("task_name", "巡检报告")
        task_id = req.get("task_id", "task-unknown")
        targets = req.get("targets", [])
        results = req.get("results", [])
        format_type = req.get("format", "all")
        config = req.get("config", {})
        
        result = generate_report(
            task_name=task_name,
            task_id=task_id,
            targets=targets,
            results=results,
            format=format_type,
            config=config,
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


@router.post("/reports/generate/sample", tags=["报告生成"])
async def generate_sample_reports_api(req: dict = None):
    """生成示例报告（用于测试）"""
    try:
        from backend.report_engine.report_generator import generate_sample_reports
        paths = generate_sample_reports()
        return {"success": True, "paths": paths, "message": "示例报告已生成"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"示例报告生成失败: {str(e)}")


@router.get("/reports/download/{report_id}", tags=["报告生成"])
async def download_report(report_id: str, format: str = Query(default="docx")):
    """下载报告文件"""
    import os
    from backend.report_engine import OUTPUT_DIR
    
    file_path = os.path.join(OUTPUT_DIR, f"{report_id}.{format}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"报告文件不存在: {report_id}.{format}")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=file_path,
        filename=f"{report_id}.{format}",
        media_type="application/octet-stream",
    )


# ============================================================
# DBCheck 数据库巡检 API
# ============================================================

@router.get("/dbcheck/db-types", tags=["DBCheck数据库巡检"])
async def list_dbcheck_db_types():
    """获取DBCheck支持的数据库类型列表"""
    try:
        from backend.dbcheck_bridge import DBCheckWrapper
        wrapper = DBCheckWrapper()
        types = wrapper.get_supported_db_types()
        return {"db_types": types, "version": wrapper.get_version()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库类型失败: {str(e)}")


@router.get("/dbcheck/version", tags=["DBCheck数据库巡检"])
async def get_dbcheck_version():
    """获取DBCheck引擎版本信息"""
    try:
        from backend.dbcheck_bridge import DBCheckWrapper, DBCheckUpdater
        wrapper = DBCheckWrapper()
        updater = DBCheckUpdater()
        return {
            "version": wrapper.get_version(),
            "commit": updater.get_current_commit(),
            "supported_types": len(wrapper.get_supported_db_types()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取版本信息失败: {str(e)}")


@router.get("/dbcheck/templates", tags=["DBCheck数据库巡检"])
async def list_dbcheck_templates(db_type: Optional[str] = Query(default=None)):
    """获取DBCheck数据库巡检模板"""
    try:
        from backend.dbcheck_bridge import DBCheckWrapper
        wrapper = DBCheckWrapper()
        templates = wrapper.get_templates(db_type)
        return {"templates": templates, "total": len(templates)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板失败: {str(e)}")


@router.get("/dbcheck/templates/{template_id}", tags=["DBCheck数据库巡检"])
async def get_dbcheck_template_detail(template_id: str):
    """获取DBCheck模板详情（包含章节结构）"""
    try:
        from backend.dbcheck_bridge import DBCheckWrapper
        wrapper = DBCheckWrapper()
        detail = wrapper.get_template_detail(template_id)
        if not detail:
            raise HTTPException(status_code=404, detail=f"模板 {template_id} 不存在")
        return detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模板详情失败: {str(e)}")


@router.get("/dbcheck/rules", tags=["DBCheck数据库巡检"])
async def list_dbcheck_rules(db_type: Optional[str] = Query(default=None)):
    """获取DBCheck YAML规则列表"""
    try:
        from backend.dbcheck_bridge import DBCheckWrapper
        wrapper = DBCheckWrapper()
        rules = wrapper.get_rules(db_type)
        return {"rules": rules, "total": len(rules)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取规则失败: {str(e)}")


@router.post("/dbcheck/rules/toggle", tags=["DBCheck数据库巡检"])
async def toggle_dbcheck_rule(req: dict):
    """启用/禁用DBCheck规则"""
    try:
        from backend.dbcheck_bridge import DBCheckWrapper
        wrapper = DBCheckWrapper()
        result = wrapper.toggle_rule(
            rule_id=req.get("rule_id", ""),
            enabled=req.get("enabled", True),
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换规则失败: {str(e)}")


@router.post("/dbcheck/inspect", tags=["DBCheck数据库巡检"])
async def run_dbcheck_inspection(req: dict):
    """执行DBCheck数据库巡检"""
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
            version=req.get("version"),
            template_id=req.get("template_id"),
            ssh_info=req.get("ssh_info"),
            options=req.get("options"),
        )
        
        return {
            "success": result.success,
            "db_type": result.db_type,
            "host": result.host,
            "port": result.port,
            "db_name": result.db_name,
            "version": result.version,
            "health_score": result.health_score,
            "total_items": result.total_items,
            "ok_count": result.ok_count,
            "warning_count": result.warning_count,
            "critical_count": result.critical_count,
            "summary": result.summary,
            "report_path": result.report_path,
            "issues": result.issues,
            "results": result.results,
            "errors": result.errors,
            "execution_time": result.execution_time,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DBCheck巡检失败: {str(e)}")


@router.get("/dbcheck/check-update", tags=["DBCheck数据库巡检"])
async def check_dbcheck_update():
    """检查DBCheck更新"""
    try:
        from backend.dbcheck_bridge import DBCheckUpdater
        updater = DBCheckUpdater()
        return updater.check_for_updates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查更新失败: {str(e)}")


@router.post("/dbcheck/update", tags=["DBCheck数据库巡检"])
async def update_dbcheck():
    """更新DBCheck到最新版本"""
    try:
        from backend.dbcheck_bridge import DBCheckUpdater
        updater = DBCheckUpdater()
        return updater.update()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.get("/dbcheck/changelog", tags=["DBCheck数据库巡检"])
async def get_dbcheck_changelog():
    """获取DBCheck CHANGELOG"""
    try:
        from backend.dbcheck_bridge import DBCheckUpdater
        updater = DBCheckUpdater()
        return {"changelog": updater.get_changelog()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取CHANGELOG失败: {str(e)}")


@router.get("/dbcheck/availability/{db_type}", tags=["DBCheck数据库巡检"])
async def check_dbcheck_availability(db_type: str):
    """检查指定数据库类型的驱动可用性"""
    try:
        from backend.dbcheck_bridge import DBCheckWrapper
        wrapper = DBCheckWrapper()
        return wrapper.check_availability(db_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查可用性失败: {str(e)}")

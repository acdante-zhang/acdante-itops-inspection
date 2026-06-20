"""
Acdante ITOps — DBCheck 模板同步器
将DBCheck的SQL模板库同步为ITOps的巡检模板
"""

from typing import Dict, List, Optional
from .dbcheck_config import (
    DBCHECK_TEMPLATE_MAP, DBCHECK_DATA_DIR,
    get_target_type, get_db_label, get_db_icon,
    TARGET_TO_DBCHECK,
)


class DBCheckTemplateSync:
    """DBCheck模板同步器"""
    
    def __init__(self, dbcheck_path: str = None):
        from .dbcheck_config import DBCHECK_BASE_PATH
        self.dbcheck_path = dbcheck_path or DBCHECK_BASE_PATH
        self.data_dir = DBCHECK_DATA_DIR
    
    def sync_all_templates(self) -> List[Dict]:
        """同步所有DBCheck模板到ITOps格式"""
        templates = []
        
        for tpl_id, tpl_info in DBCHECK_TEMPLATE_MAP.items():
            target_type = get_target_type(tpl_info["db_type"])
            template = {
                "id": tpl_id,
                "name": tpl_info["template_name"],
                "target_type": target_type,
                "brand": "DBCheck",
                "version": "v3.0.0",
                "description": tpl_info["description"],
                "is_builtin": True,
                "is_dbcheck": True,
                "dbcheck_type": tpl_info["db_type"],
                "items": self._generate_template_items(target_type, tpl_info["db_type"]),
                "created_by": "system (DBCheck)",
            }
            templates.append(template)
        
        return templates
    
    def _generate_template_items(self, target_type: str, dbcheck_type: str) -> List[Dict]:
        """为模板生成ITOps格式的巡检项"""
        items = []
        
        # 通用数据库巡检项（所有DB类型共用）
        common_items = [
            {"name": "数据库实例状态", "category": "实例", "cmd": "dbcheck:instance_status", "weight": 20, "order": 1},
            {"name": "数据库版本信息", "category": "系统", "cmd": "dbcheck:version_info", "weight": 5, "order": 2},
            {"name": "运行时间", "category": "系统", "cmd": "dbcheck:uptime", "weight": 5, "order": 3},
        ]
        
        # 数据库类型特定巡检项
        db_specific = {
            "oracle": [
                {"name": "表空间使用率", "category": "存储", "cmd": "dbcheck:tablespace_usage", "weight": 20, "order": 10, "threshold": {"metric": "tbs_usage", "operator": "gt", "critical": 95, "warning": 85, "unit": "%"}},
                {"name": "ASM磁盘组状态", "category": "存储", "cmd": "dbcheck:asm_diskgroup", "weight": 15, "order": 11},
                {"name": "DataGuard同步状态", "category": "容灾", "cmd": "dbcheck:dataguard_status", "weight": 15, "order": 12},
                {"name": "DG同步延迟", "category": "容灾", "cmd": "dbcheck:dg_lag", "weight": 15, "order": 13, "threshold": {"metric": "dg_lag", "operator": "gt", "critical": 60, "warning": 10, "unit": "秒"}},
                {"name": "SGA/PGA使用率", "category": "内存", "cmd": "dbcheck:sga_pga", "weight": 10, "order": 14},
                {"name": "活跃会话数", "category": "会话", "cmd": "dbcheck:active_sessions", "weight": 10, "order": 15, "threshold": {"metric": "sessions", "operator": "gt", "critical": 500, "warning": 300, "unit": ""}},
                {"name": "锁阻塞检测", "category": "锁", "cmd": "dbcheck:lock_blocking", "weight": 20, "order": 16},
                {"name": "RMAN备份状态", "category": "备份", "cmd": "dbcheck:rman_backup", "weight": 15, "order": 17},
                {"name": "归档日志空间", "category": "存储", "cmd": "dbcheck:archive_log", "weight": 10, "order": 18, "threshold": {"metric": "arch_usage", "operator": "gt", "critical": 90, "warning": 75, "unit": "%"}},
                {"name": "AWR性能概览", "category": "性能", "cmd": "dbcheck:awr_overview", "weight": 10, "order": 19},
                {"name": "无效对象检查", "category": "对象", "cmd": "dbcheck:invalid_objects", "weight": 5, "order": 20},
                {"name": "Redo日志切换频率", "category": "日志", "cmd": "dbcheck:redo_switch", "weight": 10, "order": 21},
                {"name": "Undo表空间状态", "category": "存储", "cmd": "dbcheck:undo_status", "weight": 10, "order": 22},
                {"name": "用户权限审计", "category": "安全", "cmd": "dbcheck:user_audit", "weight": 10, "order": 23},
                {"name": "数据库参数检查", "category": "配置", "cmd": "dbcheck:parameter_check", "weight": 10, "order": 24},
            ],
            "mysql": [
                {"name": "InnoDB缓冲池命中率", "category": "内存", "cmd": "dbcheck:innodb_buffer_pool", "weight": 20, "order": 10, "threshold": {"metric": "buffer_hit", "operator": "lt", "critical": 95, "warning": 98, "unit": "%"}},
                {"name": "主从复制状态", "category": "复制", "cmd": "dbcheck:replication_status", "weight": 20, "order": 11},
                {"name": "慢查询统计", "category": "性能", "cmd": "dbcheck:slow_queries", "weight": 15, "order": 12},
                {"name": "连接数使用率", "category": "连接", "cmd": "dbcheck:connection_usage", "weight": 15, "order": 13, "threshold": {"metric": "conn_usage", "operator": "gt", "critical": 90, "warning": 75, "unit": "%"}},
                {"name": "表锁等待", "category": "锁", "cmd": "dbcheck:table_locks", "weight": 15, "order": 14},
                {"name": "binlog状态", "category": "日志", "cmd": "dbcheck:binlog_status", "weight": 10, "order": 15},
                {"name": "查询缓存命中率", "category": "缓存", "cmd": "dbcheck:query_cache", "weight": 10, "order": 16},
                {"name": "表状态检查", "category": "对象", "cmd": "dbcheck:table_status", "weight": 10, "order": 17},
            ],
            "postgresql": [
                {"name": "缓存命中率", "category": "缓存", "cmd": "dbcheck:cache_hit_ratio", "weight": 20, "order": 10, "threshold": {"metric": "cache_hit", "operator": "lt", "critical": 95, "warning": 98, "unit": "%"}},
                {"name": "死元组比例", "category": "存储", "cmd": "dbcheck:dead_tuples", "weight": 15, "order": 11, "threshold": {"metric": "dead_tuples", "operator": "gt", "critical": 20, "warning": 10, "unit": "%"}},
                {"name": "复制状态", "category": "复制", "cmd": "dbcheck:replication", "weight": 15, "order": 12},
                {"name": "连接数使用率", "category": "连接", "cmd": "dbcheck:connection_usage", "weight": 15, "order": 13, "threshold": {"metric": "conn_usage", "operator": "gt", "critical": 90, "warning": 75, "unit": "%"}},
                {"name": "锁等待", "category": "锁", "cmd": "dbcheck:lock_waiting", "weight": 15, "order": 14},
                {"name": "归档模式", "category": "备份", "cmd": "dbcheck:archive_mode", "weight": 10, "order": 15},
                {"name": "数据库大小", "category": "存储", "cmd": "dbcheck:db_size", "weight": 10, "order": 16},
            ],
            "sqlserver": [
                {"name": "等待统计", "category": "性能", "cmd": "dbcheck:wait_stats", "weight": 20, "order": 10},
                {"name": "锁与阻塞", "category": "锁", "cmd": "dbcheck:lock_blocking", "weight": 20, "order": 11},
                {"name": "备份状态", "category": "备份", "cmd": "dbcheck:backup_status", "weight": 15, "order": 12},
                {"name": "文件使用率", "category": "存储", "cmd": "dbcheck:file_usage", "weight": 15, "order": 13, "threshold": {"metric": "file_usage", "operator": "gt", "critical": 90, "warning": 80, "unit": "%"}},
                {"name": "索引碎片", "category": "对象", "cmd": "dbcheck:index_frag", "weight": 10, "order": 14},
            ],
            "dm8": [
                {"name": "表空间使用率", "category": "存储", "cmd": "dbcheck:tablespace_usage", "weight": 20, "order": 10, "threshold": {"metric": "tbs_usage", "operator": "gt", "critical": 95, "warning": 85, "unit": "%"}},
                {"name": "SGA/PGA使用率", "category": "内存", "cmd": "dbcheck:sga_pga", "weight": 15, "order": 11},
                {"name": "缓冲池命中率", "category": "缓存", "cmd": "dbcheck:buffer_hit", "weight": 15, "order": 12},
                {"name": "配置基线检查", "category": "配置", "cmd": "dbcheck:config_baseline", "weight": 15, "order": 13},
                {"name": "索引健康检查", "category": "对象", "cmd": "dbcheck:index_health", "weight": 10, "order": 14},
                {"name": "备份状态", "category": "备份", "cmd": "dbcheck:backup_status", "weight": 10, "order": 15},
            ],
            "tidb": [
                {"name": "Placement Rules", "category": "配置", "cmd": "dbcheck:placement_rules", "weight": 15, "order": 10},
                {"name": "TiCDC状态", "category": "复制", "cmd": "dbcheck:ticdc_status", "weight": 15, "order": 11},
                {"name": "PD心跳", "category": "集群", "cmd": "dbcheck:pd_heartbeat", "weight": 15, "order": 12},
                {"name": "Follower延迟", "category": "复制", "cmd": "dbcheck:follower_lag", "weight": 15, "order": 13, "threshold": {"metric": "follower_lag", "operator": "gt", "critical": 60, "warning": 10, "unit": "秒"}},
                {"name": "慢查询分析", "category": "性能", "cmd": "dbcheck:slow_query", "weight": 10, "order": 14},
                {"name": "连接数使用率", "category": "连接", "cmd": "dbcheck:connection_usage", "weight": 10, "order": 15},
            ],
            "kingbase": [
                {"name": "实例状态", "category": "实例", "cmd": "dbcheck:instance_status", "weight": 20, "order": 10},
                {"name": "表空间使用率", "category": "存储", "cmd": "dbcheck:tablespace_usage", "weight": 20, "order": 11, "threshold": {"metric": "tbs_usage", "operator": "gt", "critical": 95, "warning": 85, "unit": "%"}},
                {"name": "复制状态", "category": "复制", "cmd": "dbcheck:replication", "weight": 15, "order": 12},
                {"name": "锁等待", "category": "锁", "cmd": "dbcheck:lock_waiting", "weight": 15, "order": 13},
                {"name": "配置基线", "category": "配置", "cmd": "dbcheck:config_baseline", "weight": 10, "order": 14},
            ],
        }
        
        # 构建巡检项
        for item in common_items:
            items.append({
                "id": f"dbcheck-{target_type}-{item['cmd'].replace(':', '-')}",
                "name": item["name"],
                "category": item["category"],
                "command": item["cmd"],
                "command_type": "dbcheck",
                "is_read_only": True,
                "parser": "raw",
                "weight": item.get("weight", 10),
                "order": item.get("order", 1),
                "threshold": item.get("threshold"),
                "suggestion": item.get("suggestion", ""),
            })
        
        specific = db_specific.get(dbcheck_type, [])
        for item in specific:
            items.append({
                "id": f"dbcheck-{target_type}-{item['cmd'].replace(':', '-')}",
                "name": item["name"],
                "category": item["category"],
                "command": item["cmd"],
                "command_type": "dbcheck",
                "is_read_only": True,
                "parser": "raw",
                "weight": item.get("weight", 10),
                "order": item.get("order", 1),
                "threshold": item.get("threshold"),
                "suggestion": item.get("suggestion", ""),
            })
        
        return items


def get_dbcheck_templates_as_itops_format() -> List[Dict]:
    """获取所有DBCheck模板（ITOps格式）"""
    sync = DBCheckTemplateSync()
    return sync.sync_all_templates()

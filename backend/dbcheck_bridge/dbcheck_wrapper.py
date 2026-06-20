"""
Acdante ITOps — DBCheck 核心包装器
封装 DBCheck 的所有数据库巡检能力，提供统一接口
"""

import os
import sys
import json
import time
import tempfile
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .dbcheck_config import (
    DBCHECK_BASE_PATH, DBCHECK_DATA_DIR, DBCHECK_REPORTS_DIR,
    TARGET_TO_DBCHECK, DBCHECK_TEMPLATE_MAP,
    get_dbcheck_db_type, get_target_type, is_dbcheck_driven,
    DBCHECK_MAIN_MODULES,
)


@dataclass
class DBCheckInspectionResult:
    """DBCheck巡检结果"""
    success: bool = False
    db_type: str = ""
    host: str = ""
    port: int = 0
    db_name: str = ""
    version: str = ""
    health_score: int = 0
    total_items: int = 0
    ok_count: int = 0
    warning_count: int = 0
    critical_count: int = 0
    error_count: int = 0
    summary: str = ""
    report_path: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    alerts: List[Dict] = field(default_factory=list)
    issues: List[Dict] = field(default_factory=list)
    results: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    raw_output: str = ""


class DBCheckWrapper:
    """DBCheck引擎包装器 - 提供统一的数据巡检接口"""
    
    def __init__(self, dbcheck_path: str = None):
        """
        初始化DBCheck包装器
        
        Args:
            dbcheck_path: DBCheck安装路径，默认使用vendor/dbcheck
        """
        self.dbcheck_path = dbcheck_path or DBCHECK_BASE_PATH
        self.data_dir = os.path.join(self.dbcheck_path, "data")
        self.reports_dir = os.path.join(self.dbcheck_path, "reports")
        
        # 确保DBCheck在Python路径中
        if self.dbcheck_path not in sys.path:
            sys.path.insert(0, self.dbcheck_path)
        
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # 缓存的版本信息
        self._version = None
        self._supported_types = None
    
    # ============================================================
    # 基本信息
    # ============================================================
    
    def get_version(self) -> str:
        """获取DBCheck版本"""
        if self._version:
            return self._version
        
        version_file = os.path.join(self.dbcheck_path, "version.json")
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                data = json.load(f)
                self._version = data.get("version", "unknown")
        else:
            try:
                from version import __version__
                self._version = __version__
            except ImportError:
                self._version = "unknown"
        
        return self._version
    
    def get_supported_db_types(self) -> List[Dict]:
        """获取支持的数据库类型列表"""
        if self._supported_types:
            return self._supported_types
        
        from .dbcheck_config import DB_LABELS, DB_ICONS, DB_DEFAULT_PORTS
        
        types = []
        for target_type, dbcheck_type in TARGET_TO_DBCHECK.items():
            types.append({
                "target_type": target_type,
                "dbcheck_type": dbcheck_type,
                "label": DB_LABELS.get(target_type, target_type),
                "icon": DB_ICONS.get(target_type, ""),
                "default_port": DB_DEFAULT_PORTS.get(target_type, 0),
                "has_template": any(
                    t["db_type"] == dbcheck_type 
                    for t in DBCHECK_TEMPLATE_MAP.values()
                ),
            })
        
        self._supported_types = types
        return types
    
    def check_availability(self, db_type: str) -> Dict:
        """检查指定数据库类型的驱动是否可用"""
        dbcheck_type = get_dbcheck_db_type(db_type) if db_type in TARGET_TO_DBCHECK else db_type
        
        drivers = {
            "oracle": "oracledb",
            "mysql": "pymysql",
            "postgresql": "psycopg2",
            "sqlserver": "pyodbc",
            "dm8": "dmpython",
            "tidb": "pymysql",
            "kingbase": "psycopg2",
        }
        
        driver_name = drivers.get(dbcheck_type)
        if not driver_name:
            return {"available": False, "reason": f"未知数据库类型: {dbcheck_type}"}
        
        try:
            __import__(driver_name)
            return {"available": True, "driver": driver_name}
        except ImportError:
            return {
                "available": False,
                "reason": f"驱动 {driver_name} 未安装。请运行: pip install {driver_name}",
                "driver": driver_name,
            }
    
    # ============================================================
    # 模板管理
    # ============================================================
    
    def get_templates(self, db_type: str = None) -> List[Dict]:
        """获取DBCheck的巡检模板"""
        templates = []
        
        for tpl_id, tpl_info in DBCHECK_TEMPLATE_MAP.items():
            if db_type and tpl_info["db_type"] != get_dbcheck_db_type(db_type):
                continue
            templates.append({
                "id": tpl_id,
                "name": tpl_info["template_name"],
                "target_type": get_target_type(tpl_info["db_type"]),
                "db_type": tpl_info["db_type"],
                "description": tpl_info["description"],
                "item_count": tpl_info["item_count"],
                "is_dbcheck": True,
                "is_builtin": True,
            })
        
        return templates
    
    def get_template_detail(self, template_id: str) -> Dict:
        """获取模板详细信息，包括DBCheck的SQL章节"""
        tpl_info = DBCHECK_TEMPLATE_MAP.get(template_id)
        if not tpl_info:
            return {}
        
        result = {
            "id": template_id,
            "name": tpl_info["template_name"],
            "target_type": get_target_type(tpl_info["db_type"]),
            "db_type": tpl_info["db_type"],
            "description": tpl_info["description"],
            "item_count": tpl_info["item_count"],
            "is_dbcheck": True,
            "chapters": [],
        }
        
        # 尝试从DBCheck的SQLite数据库读取章节结构
        try:
            chapters = self._load_template_chapters(tpl_info["db_type"])
            result["chapters"] = chapters
        except Exception:
            pass
        
        return result
    
    def _load_template_chapters(self, db_type: str) -> List[Dict]:
        """从DBCheck inspection.db加载模板章节"""
        import sqlite3
        
        db_path = os.path.join(self.data_dir, "inspection.db")
        if not os.path.exists(db_path):
            return []
        
        chapters = []
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 获取默认模板
            cursor.execute(
                """SELECT t.id as template_id, c.id as chapter_id, 
                   c.chapter_number, c.chapter_title, c.enabled,
                   q.id as query_id, q.query_key, q.query_sql, q.enabled as query_enabled
                FROM inspection_template t
                JOIN inspection_chapter c ON c.template_id = t.id
                LEFT JOIN inspection_query q ON q.chapter_id = c.id
                WHERE t.db_type = ? AND t.is_default = 1
                ORDER BY c.sort_order, q.sort_order""",
                (db_type,)
            )
            
            chapter_map = {}
            for row in cursor.fetchall():
                ch_id = row["chapter_id"]
                if ch_id not in chapter_map:
                    chapter_map[ch_id] = {
                        "chapter_id": ch_id,
                        "number": row["chapter_number"],
                        "title": row["chapter_title"],
                        "enabled": bool(row["enabled"]),
                        "queries": [],
                    }
                if row["query_id"]:
                    chapter_map[ch_id]["queries"].append({
                        "query_id": row["query_id"],
                        "key": row["query_key"],
                        "sql": row["query_sql"],
                        "enabled": bool(row["query_enabled"]),
                    })
            
            chapters = sorted(chapter_map.values(), key=lambda c: c.get("number", 99))
            conn.close()
        except Exception:
            pass
        
        return chapters
    
    # ============================================================
    # 规则引擎
    # ============================================================
    
    def get_rules(self, db_type: str = None) -> List[Dict]:
        """获取DBCheck YAML规则列表"""
        try:
            from pro.rule_engine import get_rule_engine
            engine = get_rule_engine()
            dbcheck_type = get_dbcheck_db_type(db_type) if db_type else None
            rules = engine.list_rules(dbcheck_type)
            return rules
        except Exception as e:
            return []
    
    def toggle_rule(self, rule_id: str, enabled: bool) -> Dict:
        """启用/禁用规则"""
        try:
            from pro.rule_engine import get_rule_engine
            engine = get_rule_engine()
            success = engine.toggle_rule(rule_id, enabled)
            return {"success": success, "rule_id": rule_id, "enabled": enabled}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_with_rules(self, db_type: str, context: Dict) -> List[Dict]:
        """使用DBCheck规则引擎分析巡检数据"""
        try:
            from pro.rule_engine import analyze_with_plugins
            dbcheck_type = get_dbcheck_db_type(db_type)
            issues = analyze_with_plugins(dbcheck_type, context)
            return issues
        except Exception as e:
            return []
    
    # ============================================================
    # 巡检执行
    # ============================================================
    
    def inspect(self, db_type: str, host: str, port: int,
                user: str, password: str, db_name: str = "",
                version: str = None, template_id: str = None,
                ssh_info: Dict = None, options: Dict = None) -> DBCheckInspectionResult:
        """
        执行数据库巡检（模拟/真实）
        
        对于真实环境，会调用DBCheck的run_inspection.py执行
        对于开发/演示环境，生成模拟结果
        """
        dbcheck_type = get_dbcheck_db_type(db_type)
        
        # 构建DBCheck参数
        params = {
            "db_type": dbcheck_type,
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "db_name": db_name or self._infer_db_name(dbcheck_type, user),
            "version": version,
            "template_id": template_id,
        }
        
        start_time = time.time()
        
        try:
            result = self._run_inspection(params, ssh_info, options)
        except Exception as e:
            traceback.print_exc()
            result = self._generate_mock_result(params, str(e))
        
        result.execution_time = time.time() - start_time
        return result
    
    def _run_inspection(self, params: Dict, ssh_info: Dict = None,
                        options: Dict = None) -> DBCheckInspectionResult:
        """尝试真实执行DBCheck巡检"""
        dbcheck_type = params["db_type"]
        
        # 检查驱动是否可用
        avail = self.check_availability(dbcheck_type)
        if not avail["available"]:
            return self._generate_mock_result(
                params, f"驱动不可用: {avail.get('reason', '未知')}"
            )
        
        try:
            # 尝试动态导入DBCheck模块
            main_module = DBCHECK_MAIN_MODULES.get(dbcheck_type)
            if not main_module:
                return self._generate_mock_result(params, f"不支持的数据库类型: {dbcheck_type}")
            
            # 构建db_info
            db_info = {
                "host": params["host"],
                "port": params["port"],
                "user": params["user"],
                "password": params["password"],
                "db_name": params["db_name"],
                "label": f"{params['db_name']}@{params['host']}:{params['port']}",
            }
            
            if params.get("version"):
                db_info["version"] = params["version"]
            
            # 对于MySQL/PG/SQLServer等，使用BaseInspectionEngine子类
            if dbcheck_type in ("mysql", "postgresql", "sqlserver", "dm8", "tidb", "kingbase"):
                return self._run_base_engine(dbcheck_type, db_info, ssh_info)
            elif dbcheck_type == "oracle":
                return self._run_oracle_inspection(db_info, ssh_info)
            else:
                return self._generate_mock_result(
                    params, f"该数据库类型的真实巡检尚未集成: {dbcheck_type}"
                )
                
        except Exception as e:
            traceback.print_exc()
            return self._generate_mock_result(params, f"巡检执行异常: {str(e)}")
    
    def _run_base_engine(self, dbcheck_type: str, db_info: Dict,
                         ssh_info: Dict = None) -> DBCheckInspectionResult:
        """使用BaseInspectionEngine子类执行巡检"""
        try:
            inspector_map = {
                "mysql": ("main_mysql", "MySQLInspector"),
                "postgresql": ("main_pg", "PGInspector"),
                "sqlserver": ("main_sqlserver", "SQLServerInspector"),
                "dm8": ("main_dm", "DM8Inspector"),
                "tidb": ("main_tidb", "TiDBInspector"),
                "kingbase": ("main_kingbase", "KingbaseInspector"),
            }
            
            module_name, class_name = inspector_map.get(dbcheck_type, (None, None))
            if not module_name:
                return self._generate_mock_result(
                    {"db_type": dbcheck_type, **db_info},
                    f"未找到{dbcheck_type}的Inspector"
                )
            
            # 动态导入
            module = __import__(module_name, fromlist=[class_name])
            inspector_class = getattr(module, class_name)
            
            # 实例化并执行
            inspector = inspector_class(
                host=db_info["host"],
                port=db_info["port"],
                user=db_info["user"],
                password=db_info["password"],
                db_name=db_info.get("db_name", ""),
            )
            
            # 连接
            ok, version = inspector.connect()
            if not ok:
                return self._generate_mock_result(
                    {"db_type": dbcheck_type, **db_info},
                    f"连接失败: {version}"
                )
            
            # 采集数据
            inspector.collect_data()
            
            # 生成报告
            output_path = os.path.join(
                self.reports_dir,
                f"dbcheck_{dbcheck_type}_{db_info['host']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
            )
            inspector.generate_report(output_path)
            
            # 构建结果
            return self._build_result_from_context(
                dbcheck_type, db_info, inspector.context, output_path, version
            )
            
        except Exception as e:
            traceback.print_exc()
            return self._generate_mock_result(
                {"db_type": dbcheck_type, **db_info}, str(e)
            )
    
    def _run_oracle_inspection(self, db_info: Dict,
                               ssh_info: Dict = None) -> DBCheckInspectionResult:
        """执行Oracle巡检（使用独立的main_oracle_full模块）"""
        try:
            from main_oracle_full import single_inspection
            import argparse
            
            # 构建参数
            args = argparse.Namespace()
            args.host = db_info["host"]
            args.port = db_info["port"]
            args.user = db_info["user"]
            args.password = db_info["password"]
            args.db_name = db_info.get("db_name", "")
            args.label = db_info.get("label", "")
            args.version = db_info.get("version", "")
            args.output = os.path.join(self.reports_dir, "oracle_report.docx")
            
            if ssh_info:
                args.ssh_host = ssh_info.get("host")
                args.ssh_port = ssh_info.get("port", 22)
                args.ssh_user = ssh_info.get("user")
                args.ssh_password = ssh_info.get("password")
            
            # 执行巡检
            result_data = single_inspection(args)
            
            return self._build_result_from_oracle(result_data, db_info)
            
        except Exception as e:
            traceback.print_exc()
            return self._generate_mock_result(
                {"db_type": "oracle", **db_info}, str(e)
            )
    
    # ============================================================
    # 结果构建
    # ============================================================
    
    def _build_result_from_context(self, dbcheck_type: str, db_info: Dict,
                                   context: Dict, report_path: str,
                                   version: str) -> DBCheckInspectionResult:
        """从DBCheck context构建结果"""
        target_type = get_target_type(dbcheck_type)
        
        # 提取健康评分
        health_score = context.get("health_score", 
                      context.get("score", 85))
        
        # 提取告警
        alerts = context.get("alerts", [])
        critical_count = sum(1 for a in alerts if a.get("severity") == "critical")
        warning_count = sum(1 for a in alerts if a.get("severity") == "warning")
        ok_count = context.get("total_checks", 100) - critical_count - warning_count
        
        # 构建结果列表
        results = []
        for alert in alerts:
            results.append({
                "target_name": db_info.get("label", f"{target_type}@{db_info['host']}"),
                "item_name": alert.get("title", alert.get("name", "")),
                "category": alert.get("category", ""),
                "raw_value": alert.get("value", ""),
                "status": alert.get("severity", "ok"),
                "threshold": alert.get("threshold", ""),
                "suggestion": alert.get("suggestion", alert.get("fix", "")),
                "weight": alert.get("weight", 10),
            })
        
        # 摘要
        if critical_count > 0:
            summary = f"DBCheck巡检发现 {critical_count} 个严重问题、{warning_count} 个警告，健康度 {health_score} 分。"
        elif warning_count > 0:
            summary = f"DBCheck巡检发现 {warning_count} 个警告项，整体运行基本正常，健康度 {health_score} 分。"
        else:
            summary = f"DBCheck巡检完成，所有项目正常，健康度 {health_score} 分。数据库版本: {version}"
        
        return DBCheckInspectionResult(
            success=True,
            db_type=target_type,
            host=db_info["host"],
            port=db_info["port"],
            db_name=db_info.get("db_name", ""),
            version=version,
            health_score=int(health_score),
            total_items=context.get("total_checks", len(alerts) + ok_count),
            ok_count=ok_count,
            warning_count=warning_count,
            critical_count=critical_count,
            summary=summary,
            report_path=report_path,
            context=context,
            alerts=alerts,
            issues=[a for a in alerts if a.get("severity") in ("warning", "critical")],
            results=results,
        )
    
    def _build_result_from_oracle(self, result_data: Dict,
                                  db_info: Dict) -> DBCheckInspectionResult:
        """从Oracle巡检结果构建"""
        health_score = result_data.get("health_score", 85)
        alerts = result_data.get("alerts", [])
        critical_count = result_data.get("critical_count", 0)
        warning_count = result_data.get("warning_count", 0)
        total = result_data.get("total_items", 100)
        ok_count = total - critical_count - warning_count
        
        return DBCheckInspectionResult(
            success=True,
            db_type="oracle",
            host=db_info["host"],
            port=db_info["port"],
            db_name=db_info.get("db_name", ""),
            version=result_data.get("version", ""),
            health_score=health_score,
            total_items=total,
            ok_count=ok_count,
            warning_count=warning_count,
            critical_count=critical_count,
            summary=result_data.get("summary", "Oracle巡检完成"),
            report_path=result_data.get("report_path", ""),
            context=result_data.get("context", {}),
            alerts=alerts,
            issues=result_data.get("issues", []),
            results=result_data.get("results", []),
        )
    
    def _generate_mock_result(self, params: Dict,
                              error_msg: str = "") -> DBCheckInspectionResult:
        """生成模拟巡检结果（开发/演示用）"""
        dbcheck_type = params.get("db_type", "mysql")
        target_type = get_target_type(dbcheck_type)
        host = params.get("host", "localhost")
        port = params.get("port", 3306)
        db_name = params.get("db_name", "")
        
        import random
        random.seed(hash(f"{host}:{port}:{db_name}") % 10000)
        
        total = random.randint(60, 130)
        critical = random.randint(0, 3)
        warning = random.randint(1, 8)
        ok_count = total - critical - warning
        health_score = random.randint(70, 98)
        
        mock_issues = []
        categories = ["实例状态", "表空间", "内存", "会话", "备份", "复制", "性能", "安全"]
        
        for i in range(critical + warning):
            severity = "critical" if i < critical else "warning"
            cat = random.choice(categories)
            mock_issues.append({
                "target_name": f"{target_type}@{host}",
                "item_name": f"巡检项-{cat}-{i+1}",
                "category": cat,
                "status": severity,
                "value": f"{random.randint(80, 99)}%",
                "threshold": ">85%告警" if severity == "warning" else ">95%严重",
                "suggestion": f"建议检查{cat}相关配置" if severity == "warning" else f"紧急处理{cat}问题",
            })
        
        note = f"\n[注意: {error_msg}]" if error_msg else ""
        summary = f"DBCheck {target_type} 巡检完成。健康度 {health_score} 分，发现 {critical} 个严重问题、{warning} 个警告。{note}"
        
        return DBCheckInspectionResult(
            success=not bool(error_msg),
            db_type=target_type,
            host=host,
            port=port,
            db_name=db_name,
            version=f"{target_type} v{random.choice(['8.0.35','15.4','19c','2019','8.1.2'])}",
            health_score=health_score,
            total_items=total,
            ok_count=ok_count,
            warning_count=warning,
            critical_count=critical,
            summary=summary,
            issues=mock_issues,
            results=mock_issues,
            errors=[error_msg] if error_msg else [],
        )
    
    def _infer_db_name(self, dbcheck_type: str, user: str) -> str:
        """推断数据库名"""
        defaults = {
            "oracle": "ORCL",
            "mysql": "mysql",
            "postgresql": "postgres",
            "sqlserver": "master",
            "dm8": "DAMENG",
        }
        return defaults.get(dbcheck_type, user)
    
    # ============================================================
    # 报告生成
    # ============================================================
    
    def generate_report(self, result: DBCheckInspectionResult,
                        format: str = "docx") -> str:
        """生成巡检报告"""
        from backend.report_engine.report_generator import generate_report
        from backend.report_engine import ReportConfig
        
        config = ReportConfig(
            title=f"{result.db_type.upper()} 数据库巡检报告 (DBCheck)",
            subtitle=f"引擎版本: {self.get_version()}",
            platform_name="Acdante ITOps + DBCheck",
        )
        
        report_result = generate_report(
            task_name=f"{result.db_type}数据库巡检",
            task_id=f"dbcheck-{result.host}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            targets=[{
                "name": f"{result.db_type}@{result.host}:{result.port}",
                "type": result.db_type,
                "version": result.version,
            }],
            results=result.results if result.results else [
                {
                    "target_name": f"{result.db_type}@{result.host}",
                    "item_name": "DBCheck巡检",
                    "category": "数据库",
                    "raw_value": f"健康度{result.health_score}",
                    "value": result.health_score,
                    "status": "ok",
                    "weight": 100,
                    "threshold": "",
                    "suggestion": "",
                }
            ],
            format=format,
            config={"title": config.title, "platform_name": config.platform_name},
        )
        
        return report_result.get("paths", {}).get(format, "")
    
    # ============================================================
    # 更新管理
    # ============================================================
    
    def check_update(self) -> Dict:
        """检查DBCheck更新（通过git）"""
        import subprocess
        
        try:
            result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=self.dbcheck_path,
                capture_output=True, text=True, timeout=30
            )
            
            current = self.get_version()
            
            # 获取远程最新tag
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0", "origin/main"],
                cwd=self.dbcheck_path,
                capture_output=True, text=True, timeout=30
            )
            latest = result.stdout.strip()
            
            has_update = latest and latest != current
            
            return {
                "current_version": current,
                "latest_version": latest if latest else "unknown",
                "has_update": has_update,
                "checked_at": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "current_version": self.get_version(),
                "latest_version": "unknown",
                "has_update": False,
                "error": str(e),
            }

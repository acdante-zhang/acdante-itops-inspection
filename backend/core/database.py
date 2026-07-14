"""
Acdante ITOps - SQLite 数据持久化层
存储巡检对象、模板、任务、结果、报告
"""

import sqlite3
import json
import os
import time
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("ITOPS_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "itops.db"))


def ensure_db_dir():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


@contextmanager
def get_db():
    """获取数据库连接"""
    ensure_db_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """初始化数据库表结构"""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'linux',
                brand TEXT DEFAULT '',
                model TEXT DEFAULT '',
                version TEXT DEFAULT '',
                location TEXT DEFAULT '',
                protocol TEXT DEFAULT 'ssh',
                host TEXT NOT NULL,
                port INTEGER DEFAULT 22,
                username TEXT DEFAULT '',
                password_enc TEXT DEFAULT '',
                private_key_path TEXT DEFAULT '',
                snmp_version TEXT DEFAULT 'v2c',
                community TEXT DEFAULT 'public',
                snmp_username TEXT DEFAULT '',
                snmp_auth_protocol TEXT DEFAULT '',
                snmp_auth_password TEXT DEFAULT '',
                snmp_priv_protocol TEXT DEFAULT '',
                snmp_priv_password TEXT DEFAULT '',
                device_type TEXT DEFAULT 'linux',
                use_https INTEGER DEFAULT 0,
                verify_cert INTEGER DEFAULT 0,
                timeout INTEGER DEFAULT 30,
                database_name TEXT DEFAULT '',
                offline_mode INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                health_score INTEGER DEFAULT 100,
                last_inspection_at TEXT,
                tags TEXT DEFAULT '[]',
                connection_params TEXT DEFAULT '{}',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                target_type TEXT NOT NULL,
                brand TEXT DEFAULT 'Generic',
                version TEXT DEFAULT 'v1.0.0',
                description TEXT DEFAULT '',
                is_builtin INTEGER DEFAULT 1,
                is_dbcheck INTEGER DEFAULT 0,
                dbcheck_type TEXT DEFAULT '',
                items TEXT DEFAULT '[]',
                created_by TEXT DEFAULT 'system',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                template_id TEXT NOT NULL,
                target_ids TEXT DEFAULT '[]',
                schedule_type TEXT DEFAULT 'manual',
                cron_expr TEXT DEFAULT '',
                status TEXT DEFAULT 'pending',
                last_run_at TEXT,
                next_run_at TEXT,
                notify_email TEXT DEFAULT '[]',
                created_by TEXT DEFAULT 'admin',
                config TEXT DEFAULT '{}',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS inspection_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                target_name TEXT DEFAULT '',
                item_id TEXT DEFAULT '',
                item_name TEXT DEFAULT '',
                category TEXT DEFAULT '',
                raw_value TEXT DEFAULT '',
                parsed_value TEXT DEFAULT '',
                status TEXT DEFAULT 'ok',
                threshold_desc TEXT DEFAULT '',
                suggestion TEXT DEFAULT '',
                executed_at TEXT DEFAULT (datetime('now')),
                duration_ms REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                task_name TEXT DEFAULT '',
                target_ids TEXT DEFAULT '[]',
                format TEXT DEFAULT 'html',
                health_score INTEGER DEFAULT 100,
                total_items INTEGER DEFAULT 0,
                ok_count INTEGER DEFAULT 0,
                warning_count INTEGER DEFAULT 0,
                critical_count INTEGER DEFAULT 0,
                summary TEXT DEFAULT '',
                file_path TEXT DEFAULT '',
                generated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                level TEXT DEFAULT 'info',
                message TEXT DEFAULT '',
                detail TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_results_task ON inspection_results(task_id);
            CREATE INDEX IF NOT EXISTS idx_results_target ON inspection_results(target_id);
            CREATE INDEX IF NOT EXISTS idx_results_executed ON inspection_results(executed_at);
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        """)


# ============================================================
# Target CRUD
# ============================================================

def get_targets(type_filter: Optional[str] = None) -> List[Dict]:
    with get_db() as conn:
        if type_filter:
            rows = conn.execute("SELECT * FROM targets WHERE type=? ORDER BY id", (type_filter,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM targets ORDER BY id").fetchall()
        return [_row_to_dict(r) for r in rows]


def get_target(target_id: int) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM targets WHERE id=?", (target_id,)).fetchone()
        return _row_to_dict(row) if row else None


def create_target(data: Dict) -> Dict:
    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO targets (name, type, brand, model, version, location, protocol, host, port,
                username, password_enc, private_key_path, snmp_version, community, device_type,
                use_https, verify_cert, timeout, database_name, tags, connection_params)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data.get("name", ""), data.get("type", "linux"), data.get("brand", ""),
            data.get("model", ""), data.get("version", ""), data.get("location", ""),
            data.get("protocol", "ssh"), data.get("host", ""), data.get("port", 22),
            data.get("username", ""), data.get("password_enc", ""), data.get("private_key_path", ""),
            data.get("snmp_version", "v2c"), data.get("community", "public"),
            data.get("device_type", "linux"), data.get("use_https", 0),
            data.get("verify_cert", 0), data.get("timeout", 30),
            data.get("database_name", ""), json.dumps(data.get("tags", [])),
            json.dumps(data.get("connection_params", {})),
        ))
        return get_target(cur.lastrowid)


def update_target(target_id: int, data: Dict) -> Optional[Dict]:
    with get_db() as conn:
        fields = []
        values = []
        for key in ["name", "type", "brand", "model", "version", "location", "protocol",
                     "host", "port", "username", "password_enc", "device_type", "timeout",
                     "database_name", "status", "health_score", "tags"]:
            if key in data:
                fields.append(f"{key}=?")
                values.append(data[key])
        if not fields:
            return get_target(target_id)
        fields.append("updated_at=datetime('now')")
        values.append(target_id)
        conn.execute(f"UPDATE targets SET {','.join(fields)} WHERE id=?", values)
        return get_target(target_id)


def delete_target(target_id: int) -> bool:
    with get_db() as conn:
        conn.execute("DELETE FROM targets WHERE id=?", (target_id,))
        return True


# ============================================================
# Template CRUD
# ============================================================

def get_templates(type_filter: Optional[str] = None) -> List[Dict]:
    with get_db() as conn:
        if type_filter:
            rows = conn.execute("SELECT * FROM templates WHERE target_type=? ORDER BY id", (type_filter,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM templates ORDER BY id").fetchall()
        return [_row_to_dict(r) for r in rows]


def get_template(template_id: str) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM templates WHERE id=?", (template_id,)).fetchone()
        return _row_to_dict(row) if row else None


def create_template(data: Dict) -> Dict:
    with get_db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO templates (id, name, target_type, brand, version, description,
                is_builtin, is_dbcheck, dbcheck_type, items, created_by)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data.get("id", ""), data.get("name", ""), data.get("target_type", ""),
            data.get("brand", ""), data.get("version", ""), data.get("description", ""),
            data.get("is_builtin", 1), data.get("is_dbcheck", 0), data.get("dbcheck_type", ""),
            json.dumps(data.get("items", []), ensure_ascii=False), data.get("created_by", "system"),
        ))
        return get_template(data["id"])


# ============================================================
# Task CRUD
# ============================================================

def get_tasks() -> List[Dict]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
        return [_row_to_dict(r) for r in rows]


def get_task(task_id: str) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        return _row_to_dict(row) if row else None


def create_task(data: Dict) -> Dict:
    task_id = data.get("id") or f"task-{int(time.time()*1000) % 1000000:06d}"
    with get_db() as conn:
        conn.execute("""
            INSERT INTO tasks (id, name, template_id, target_ids, schedule_type, cron_expr,
                notify_email, created_by, config)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            task_id, data.get("name", ""), data.get("template_id", ""),
            json.dumps(data.get("target_ids", [])), data.get("schedule_type", "manual"),
            data.get("cron_expr", ""), json.dumps(data.get("notify_email", [])),
            data.get("created_by", "admin"), json.dumps(data.get("config", {})),
        ))
        return get_task(task_id)


def update_task(task_id: str, data: Dict) -> Optional[Dict]:
    with get_db() as conn:
        fields = []
        values = []
        for key in ["name", "template_id", "target_ids", "schedule_type", "cron_expr",
                     "status", "last_run_at", "next_run_at", "notify_email", "config"]:
            if key in data:
                val = data[key]
                if isinstance(val, (list, dict)):
                    val = json.dumps(val, ensure_ascii=False)
                fields.append(f"{key}=?")
                values.append(val)
        if not fields:
            return get_task(task_id)
        fields.append("updated_at=datetime('now')")
        values.append(task_id)
        conn.execute(f"UPDATE tasks SET {','.join(fields)} WHERE id=?", values)
        return get_task(task_id)


def delete_task(task_id: str) -> bool:
    with get_db() as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        return True


# ============================================================
# Inspection Results
# ============================================================

def save_inspection_result(result: Dict):
    """保存巡检结果"""
    with get_db() as conn:
        for item in result.get("items", []):
            conn.execute("""
                INSERT INTO inspection_results (task_id, target_id, target_name, item_id, item_name,
                    category, raw_value, parsed_value, status, threshold_desc, suggestion, duration_ms)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                result.get("task_id", ""), result.get("target_id", 0),
                result.get("target_name", ""), item.get("item_id", ""),
                item.get("item_name", ""), item.get("category", ""),
                str(item.get("raw_value", ""))[:2000], str(item.get("parsed_value", ""))[:500],
                item.get("status", "ok"), item.get("threshold_desc", ""),
                item.get("suggestion", ""), item.get("duration_ms", 0),
            ))


def get_results(task_id: Optional[str] = None, target_id: Optional[int] = None,
                limit: int = 200) -> List[Dict]:
    with get_db() as conn:
        query = "SELECT * FROM inspection_results WHERE 1=1"
        params = []
        if task_id:
            query += " AND task_id=?"
            params.append(task_id)
        if target_id:
            query += " AND target_id=?"
            params.append(target_id)
        query += " ORDER BY executed_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        return [_row_to_dict(r) for r in rows]


# ============================================================
# Reports
# ============================================================

def save_report(report: Dict) -> str:
    report_id = report.get("id") or f"rpt-{int(time.time()*1000) % 1000000:06d}"
    with get_db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO reports (id, task_id, task_name, target_ids, format,
                health_score, total_items, ok_count, warning_count, critical_count, summary, file_path)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            report_id, report.get("task_id", ""), report.get("task_name", ""),
            json.dumps(report.get("target_ids", [])), report.get("format", "html"),
            report.get("health_score", 100), report.get("total_items", 0),
            report.get("ok_count", 0), report.get("warning_count", 0),
            report.get("critical_count", 0), report.get("summary", ""),
            report.get("file_path", ""),
        ))
    return report_id


def get_reports(limit: int = 50) -> List[Dict]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM reports ORDER BY generated_at DESC LIMIT ?", (limit,)).fetchall()
        return [_row_to_dict(r) for r in rows]


def get_report(report_id: str) -> Optional[Dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()
        return _row_to_dict(row) if row else None


# ============================================================
# Dashboard Stats
# ============================================================

def get_dashboard_stats() -> Dict:
    with get_db() as conn:
        total_targets = conn.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
        active_targets = conn.execute("SELECT COUNT(*) FROM targets WHERE status='active'").fetchone()[0]
        total_templates = conn.execute("SELECT COUNT(*) FROM templates").fetchone()[0]
        total_tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        running_tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE status='running'").fetchone()[0]

        # 最近结果统计
        recent = conn.execute("""
            SELECT status, COUNT(*) as cnt FROM inspection_results
            WHERE executed_at > datetime('now', '-24 hours')
            GROUP BY status
        """).fetchall()

        critical = sum(r["cnt"] for r in recent if r["status"] == "critical")
        warning = sum(r["cnt"] for r in recent if r["status"] == "warning")

        # 按类型统计
        type_rows = conn.execute("SELECT type, COUNT(*) as cnt FROM targets GROUP BY type").fetchall()
        targets_by_type = [{"type": r["type"], "count": r["cnt"]} for r in type_rows]

        # 最近任务
        recent_tasks = conn.execute("""
            SELECT id, name, status, last_run_at FROM tasks
            ORDER BY last_run_at DESC LIMIT 5
        """).fetchall()

        return {
            "total_targets": total_targets,
            "active_targets": active_targets,
            "total_templates": total_templates,
            "total_tasks": total_tasks,
            "running_tasks": running_tasks,
            "today_reports": conn.execute("SELECT COUNT(*) FROM reports WHERE generated_at > datetime('now','-24 hours')").fetchone()[0],
            "critical_issues": critical,
            "warning_issues": warning,
            "targets_by_type": targets_by_type,
            "recent_tasks": [dict(r) for r in recent_tasks],
            "recent_alerts": [],
            "health_trend": [],
        }


# ============================================================
# Seed Data
# ============================================================

def seed_builtin_templates():
    """写入内置模板到数据库"""
    builtin_templates = [
        {
            "id": "tpl-linux-generic-v1",
            "name": "Linux通用巡检模板",
            "target_type": "linux",
            "brand": "Generic",
            "version": "v1.0.0",
            "description": "适用于RHEL/CentOS/Ubuntu等主流Linux发行版",
            "items": [
                {"id": "li-01", "name": "系统运行时间", "category": "系统信息", "command": "uptime", "command_type": "ssh", "parser": "raw", "weight": 5, "order": 1},
                {"id": "li-02", "name": "CPU使用率", "category": "CPU", "command": "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'", "command_type": "ssh", "parser": "raw", "threshold": {"metric": "cpu_usage", "operator": "gt", "critical": 90, "warning": 70, "unit": "%"}, "weight": 20, "order": 2},
                {"id": "li-03", "name": "内存使用率", "category": "内存", "command": "free -m | awk 'NR==2{printf \"%.1f\", $3/$2*100}'", "command_type": "ssh", "parser": "raw", "threshold": {"metric": "mem_usage", "operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, "weight": 20, "order": 3},
                {"id": "li-04", "name": "磁盘使用率", "category": "磁盘", "command": "df -h --type=ext4 --type=xfs --type=ext3 | awk 'NR>1{print $6, $5}'", "command_type": "ssh", "parser": "raw", "threshold": {"metric": "disk_usage", "operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, "weight": 20, "order": 4},
                {"id": "li-05", "name": "系统负载", "category": "CPU", "command": "cat /proc/loadavg | awk '{print $1, $2, $3}'", "command_type": "ssh", "parser": "raw", "threshold": {"metric": "load_avg", "operator": "gt", "critical": 16, "warning": 8, "unit": ""}, "weight": 15, "order": 5},
                {"id": "li-06", "name": "Swap使用率", "category": "内存", "command": "free -m | awk 'NR==3{printf \"%.1f\", $3/$2*100}'", "command_type": "ssh", "parser": "raw", "threshold": {"metric": "swap_usage", "operator": "gt", "critical": 80, "warning": 50, "unit": "%"}, "weight": 10, "order": 6},
                {"id": "li-07", "name": "关键进程", "category": "进程", "command": "ps aux --sort=-%mem | head -20", "command_type": "ssh", "parser": "raw", "weight": 10, "order": 7},
                {"id": "li-08", "name": "系统日志错误", "category": "安全", "command": "journalctl -p err --since '24 hours ago' | tail -50", "command_type": "ssh", "parser": "raw", "weight": 15, "order": 8},
            ],
        },
        {
            "id": "tpl-network-huawei-v1",
            "name": "华为网络设备巡检模板",
            "target_type": "network",
            "brand": "华为",
            "version": "v1.0.0",
            "description": "华为交换机/路由器/防火墙通用巡检模板",
            "items": [
                {"id": "hw-01", "name": "设备版本信息", "category": "系统", "command": "display version", "command_type": "ssh", "parser": "raw", "weight": 5, "order": 1},
                {"id": "hw-02", "name": "CPU使用率", "category": "CPU", "command": "display cpu-usage", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 70, "unit": "%"}, "weight": 20, "order": 2},
                {"id": "hw-03", "name": "内存使用率", "category": "内存", "command": "display memory-usage", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 85, "warning": 70, "unit": "%"}, "weight": 20, "order": 3},
                {"id": "hw-04", "name": "接口状态", "category": "接口", "command": "display interface brief", "command_type": "ssh", "parser": "raw", "weight": 15, "order": 4},
                {"id": "hw-05", "name": "告警信息", "category": "告警", "command": "display alarm active all", "command_type": "ssh", "parser": "raw", "weight": 15, "order": 5},
                {"id": "hw-06", "name": "风扇状态", "category": "硬件", "command": "display device fan", "command_type": "ssh", "parser": "raw", "weight": 5, "order": 6},
                {"id": "hw-07", "name": "电源状态", "category": "硬件", "command": "display device power", "command_type": "ssh", "parser": "raw", "weight": 5, "order": 7},
                {"id": "hw-08", "name": "温度信息", "category": "硬件", "command": "display device temperature", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 70, "warning": 60, "unit": "°C"}, "weight": 5, "order": 8},
            ],
        },
        {
            "id": "tpl-snmp-linux-v1",
            "name": "Linux服务器SNMP巡检模板",
            "target_type": "linux",
            "brand": "Generic",
            "version": "v2.0.0",
            "description": "Linux服务器通用SNMP巡检模板",
            "items": [
                {"id": "snmp-lnx-01", "name": "系统描述", "category": "系统", "command": "snmp:1.3.6.1.2.1.1.1.0", "command_type": "snmp", "parser": "raw", "weight": 5, "order": 1},
                {"id": "snmp-lnx-02", "name": "系统运行时间", "category": "系统", "command": "snmp:1.3.6.1.2.1.1.3.0", "command_type": "snmp", "parser": "ticks_to_uptime", "weight": 5, "order": 2},
                {"id": "snmp-lnx-03", "name": "CPU使用率(%)", "category": "CPU", "command": "snmp:1.3.6.1.4.1.2021.11.11.0", "command_type": "snmp", "parser": "raw", "threshold": {"operator": "lt", "critical": 10, "warning": 30, "unit": "%"}, "weight": 20, "order": 3},
                {"id": "snmp-lnx-04", "name": "可用物理内存(KB)", "category": "内存", "command": "snmp:1.3.6.1.4.1.2021.4.6.0", "command_type": "snmp", "parser": "raw", "weight": 20, "order": 4},
                {"id": "snmp-lnx-05", "name": "磁盘使用率(%)", "category": "磁盘", "command": "snmp:1.3.6.1.4.1.2021.9.1.9", "command_type": "snmp", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, "weight": 20, "order": 5},
            ],
        },
        {
            "id": "tpl-pacs-ai-linux-v1",
            "name": "PACS-AI影像质控Linux服务器巡检模板",
            "target_type": "linux",
            "brand": "PACS-AI",
            "version": "v1.0.0",
            "description": "PACS-AI影像质控系统专用Linux服务器巡检模板，关注GPU、磁盘IO、网络带宽",
            "items": [
                {"id": "pacs-01", "name": "系统运行时间", "category": "系统", "command": "uptime", "command_type": "ssh", "parser": "raw", "weight": 5, "order": 1},
                {"id": "pacs-02", "name": "CPU使用率", "category": "CPU", "command": "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 70, "unit": "%"}, "weight": 15, "order": 2},
                {"id": "pacs-03", "name": "内存使用率", "category": "内存", "command": "free -m | awk 'NR==2{printf \"%.1f\", $3/$2*100}'", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, "weight": 15, "order": 3},
                {"id": "pacs-04", "name": "GPU使用率", "category": "GPU", "command": "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null || echo 'N/A'", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 95, "warning": 80, "unit": "%"}, "weight": 20, "order": 4},
                {"id": "pacs-05", "name": "GPU显存使用率", "category": "GPU", "command": "nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader 2>/dev/null || echo 'N/A'", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 95, "warning": 85, "unit": "%"}, "weight": 20, "order": 5},
                {"id": "pacs-06", "name": "GPU温度", "category": "GPU", "command": "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader 2>/dev/null || echo 'N/A'", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 85, "warning": 75, "unit": "°C"}, "weight": 15, "order": 6},
                {"id": "pacs-07", "name": "磁盘使用率", "category": "磁盘", "command": "df -h --type=ext4 --type=xfs | awk 'NR>1{print $6, $5}'", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, "weight": 15, "order": 7},
                {"id": "pacs-08", "name": "磁盘IO等待", "category": "磁盘", "command": "iostat -x 1 2 | tail -5 | awk '{print $1, $NF}' 2>/dev/null || echo 'iostat not available'", "command_type": "ssh", "parser": "raw", "weight": 10, "order": 8},
                {"id": "pacs-09", "name": "网络连接数", "category": "网络", "command": "ss -s", "command_type": "ssh", "parser": "raw", "weight": 5, "order": 9},
                {"id": "pacs-10", "name": "AI推理进程检查", "category": "业务", "command": "ps aux | grep -E '(vllm|torch|tensorflow|python.*infer)' | grep -v grep | head -10", "command_type": "ssh", "parser": "raw", "weight": 20, "order": 10},
                {"id": "pacs-11", "name": "DICOM服务端口检查", "category": "业务", "command": "ss -tlnp | grep -E '(104|11112|8080|8100)' 2>/dev/null || echo 'No DICOM ports found'", "command_type": "ssh", "parser": "raw", "weight": 15, "order": 11},
            ],
        },
    ]

    for tpl in builtin_templates:
        create_template(tpl)

    logger.info(f"已初始化 {len(builtin_templates)} 个内置模板")


def _row_to_dict(row) -> Dict:
    """将sqlite3.Row转为dict，自动解析JSON字段"""
    if row is None:
        return {}
    d = dict(row)
    for key in ["items", "target_ids", "tags", "notify_email", "connection_params", "config"]:
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                pass
    return d

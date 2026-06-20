"""
Acdante ITOps — DBCheck 桥接层配置映射
ITOps target_type ↔ DBCheck db_type 双向映射
"""

import os

# ============================================================
# 路径配置
# ============================================================

# DBCheck 安装路径（相对于项目根目录）
DBCHECK_BASE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "_vendor", "dbcheck"
)

# DBCheck 数据目录
DBCHECK_DATA_DIR = os.path.join(DBCHECK_BASE_PATH, "data")

# DBCheck 报告输出目录
DBCHECK_REPORTS_DIR = os.path.join(DBCHECK_BASE_PATH, "reports")

# ITOps 工作区报告目录
ITOP_REPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "..", "workspace", "reports"
)

# ============================================================
# 数据库类型映射
# ============================================================

# ITOps target_type → DBCheck db_type
TARGET_TO_DBCHECK = {
    "oracle":    "oracle",
    "mysql":     "mysql",
    "postgres":  "postgresql",
    "mssql":     "sqlserver",
    "dm8":       "dm8",
    "tidb":      "tidb",
    "kingbase":  "kingbase",
    "gbase":     "gbase",
    "ivorysql":  "ivorysql",
    "yashandb":  "yashandb",
}

# DBCheck db_type → ITOps target_type
DBCHECK_TO_TARGET = {v: k for k, v in TARGET_TO_DBCHECK.items()}

# ============================================================
# 数据库连接信息
# ============================================================

DB_DEFAULT_PORTS = {
    "oracle":    1521,
    "mysql":     3306,
    "postgres":  5432,
    "mssql":     1433,
    "dm8":       5236,
    "tidb":      4000,
    "kingbase":  54321,
    "gbase":     5258,
    "ivorysql":  5333,
    "yashandb":  1688,
}

DB_LABELS = {
    "oracle":    "Oracle",
    "mysql":     "MySQL",
    "postgres":  "PostgreSQL",
    "mssql":     "SQL Server",
    "dm8":       "达梦 DM8",
    "tidb":      "TiDB",
    "kingbase":  "KingbaseES (人大金仓)",
    "gbase":     "GBase 8s",
    "ivorysql":  "IvorySQL",
    "yashandb":  "YashanDB (崖山)",
}

DB_ICONS = {
    "oracle":    "🔶",
    "mysql":     "🐬",
    "postgres":  "🐘",
    "mssql":     "📊",
    "dm8":       "🗄️",
    "tidb":      "⚡",
    "kingbase":  "👑",
    "gbase":     "🔷",
    "ivorysql":  "🦣",
    "yashandb":  "🏔️",
}

DB_DRIVERS = {
    "oracle":    "oracledb",
    "mysql":     "pymysql",
    "postgres":  "psycopg2",
    "mssql":     "pyodbc",
    "dm8":       "dmpython",
    "tidb":      "pymysql",
    "kingbase":  "psycopg2",
    "gbase":     "gbase8sdb",
    "ivorysql":  "psycopg2",
    "yashandb":  "yasdb",
}

# ============================================================
# DBCheck 巡检入口模块映射
# ============================================================

DBCHECK_MAIN_MODULES = {
    "oracle":    "main_oracle_full",
    "mysql":     "main_mysql",
    "postgresql":"main_pg",
    "sqlserver": "main_sqlserver",
    "dm8":       "main_dm",
    "tidb":      "main_tidb",
    "kingbase":  "main_kingbase",
    "gbase":     "main_gbase",
    "ivorysql":  "main_ivorysql",
    "yashandb":  "main_yashandb",
}

# ============================================================
# 模板映射
# ============================================================

# ITOps 模板ID → DBCheck 模板信息
DBCHECK_TEMPLATE_MAP = {
    "tpl-dbcheck-oracle-v3": {
        "db_type": "oracle",
        "template_name": "Oracle 全量巡检 (DBCheck)",
        "description": "基于DBCheck的Oracle数据库全量巡检，涵盖实例状态、表空间、ASM、DataGuard、AWR、备份恢复、安全审计、性能诊断等130+巡检项",
        "item_count": 130,
    },
    "tpl-dbcheck-mysql-v3": {
        "db_type": "mysql",
        "template_name": "MySQL 全量巡检 (DBCheck)",
        "description": "基于DBCheck的MySQL数据库全量巡检，涵盖主从复制、InnoDB缓冲池、慢查询、连接池、锁等待、binlog、安全配置等80+巡检项",
        "item_count": 80,
    },
    "tpl-dbcheck-pg-v3": {
        "db_type": "postgresql",
        "template_name": "PostgreSQL 全量巡检 (DBCheck)",
        "description": "基于DBCheck的PostgreSQL数据库全量巡检，涵盖归档模式、缓存命中率、死元组、复制状态、锁等待、连接数、配置基线等70+巡检项",
        "item_count": 70,
    },
    "tpl-dbcheck-sqlserver-v3": {
        "db_type": "sqlserver",
        "template_name": "SQL Server 全量巡检 (DBCheck)",
        "description": "基于DBCheck的SQL Server数据库全量巡检，涵盖等待统计、锁与阻塞、备份状态、文件使用率、索引健康、安全审计等60+巡检项",
        "item_count": 60,
    },
    "tpl-dbcheck-dm8-v3": {
        "db_type": "dm8",
        "template_name": "达梦DM8 全量巡检 (DBCheck)",
        "description": "基于DBCheck的达梦DM8数据库全量巡检，涵盖表空间、SGA/PGA、缓冲池、配置基线、索引健康、备份状态、安全审计等70+巡检项",
        "item_count": 70,
    },
    "tpl-dbcheck-tidb-v3": {
        "db_type": "tidb",
        "template_name": "TiDB 全量巡检 (DBCheck)",
        "description": "基于DBCheck的TiDB数据库全量巡检，涵盖Placement Rules、TiCDC状态、PD心跳、Follower延迟、慢查询、连接池等60+巡检项",
        "item_count": 60,
    },
    "tpl-dbcheck-kingbase-v3": {
        "db_type": "kingbase",
        "template_name": "KingbaseES 全量巡检 (DBCheck)",
        "description": "基于DBCheck的KingbaseES数据库全量巡检，涵盖实例状态、表空间、复制状态、锁等待、配置基线等50+巡检项",
        "item_count": 50,
    },
}

def get_dbcheck_db_type(target_type: str) -> str:
    """ITOps target_type → DBCheck db_type"""
    return TARGET_TO_DBCHECK.get(target_type, target_type)

def get_target_type(dbcheck_type: str) -> str:
    """DBCheck db_type → ITOps target_type"""
    return DBCHECK_TO_TARGET.get(dbcheck_type, dbcheck_type)

def get_default_port(db_type: str) -> int:
    """获取数据库默认端口"""
    target = db_type if db_type in DB_DEFAULT_PORTS else get_target_type(db_type)
    return DB_DEFAULT_PORTS.get(target, 0)

def get_db_label(target_type: str) -> str:
    """获取数据库显示名称"""
    return DB_LABELS.get(target_type, target_type)

def get_db_icon(target_type: str) -> str:
    """获取数据库图标"""
    return DB_ICONS.get(target_type, "📄")

def is_dbcheck_driven(template_id: str) -> bool:
    """判断模板是否由DBCheck驱动"""
    return template_id in DBCHECK_TEMPLATE_MAP or template_id.startswith("tpl-dbcheck-")

def get_dbcheck_template_info(template_id: str) -> dict:
    """获取DBCheck模板信息"""
    return DBCHECK_TEMPLATE_MAP.get(template_id, {})

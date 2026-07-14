"""
Acdante ITOps - 配置管理
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """应用配置"""
    # 服务端口
    python_api_port: int = int(os.environ.get("PYTHON_API_PORT", "8000"))
    next_port: int = int(os.environ.get("NEXT_PORT", "5000"))

    # 数据库
    db_path: str = os.environ.get("ITOPS_DB_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "itops.db"))

    # 报告
    report_dir: str = os.environ.get("ITOPS_REPORT_DIR", os.path.join(os.path.dirname(__file__), "..", "data", "reports"))

    # SSH
    ssh_timeout: int = int(os.environ.get("SSH_TIMEOUT", "30"))
    ssh_max_connections: int = int(os.environ.get("SSH_MAX_CONNECTIONS", "10"))

    # SNMP
    snmp_timeout: int = int(os.environ.get("SNMP_TIMEOUT", "5"))
    snmp_retries: int = int(os.environ.get("SNMP_RETRIES", "2"))

    # 调度器
    scheduler_enabled: bool = os.environ.get("SCHEDULER_ENABLED", "true").lower() == "true"

    # 日志
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")

    # 安全
    secret_key: str = os.environ.get("SECRET_KEY", "acdante-itops-secret-key-change-in-production")


config = Config()

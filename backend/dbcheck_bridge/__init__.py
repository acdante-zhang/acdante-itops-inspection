"""
Acdante ITOps — DBCheck 桥接层
将 DBCheck 数据库巡检引擎集成到 ITOps 平台
"""

from .dbcheck_wrapper import DBCheckWrapper, DBCheckInspectionResult
from .dbcheck_config import (
    DBCHECK_BASE_PATH, DBCHECK_DATA_DIR,
    TARGET_TO_DBCHECK, DBCHECK_TO_TARGET,
    DB_DEFAULT_PORTS, DB_LABELS, DB_ICONS,
    DBCHECK_TEMPLATE_MAP, DBCHECK_MAIN_MODULES,
    get_dbcheck_db_type, get_target_type,
    is_dbcheck_driven, get_dbcheck_template_info,
)
from .dbcheck_templates import DBCheckTemplateSync, get_dbcheck_templates_as_itops_format
from .dbcheck_updater import DBCheckUpdater

__all__ = [
    # 核心包装器
    'DBCheckWrapper',
    'DBCheckInspectionResult',
    
    # 配置
    'DBCHECK_BASE_PATH',
    'DBCHECK_DATA_DIR',
    'TARGET_TO_DBCHECK',
    'DBCHECK_TO_TARGET',
    'DB_DEFAULT_PORTS',
    'DB_LABELS',
    'DB_ICONS',
    'DBCHECK_TEMPLATE_MAP',
    'DBCHECK_MAIN_MODULES',
    'get_dbcheck_db_type',
    'get_target_type',
    'is_dbcheck_driven',
    'get_dbcheck_template_info',
    
    # 模板同步
    'DBCheckTemplateSync',
    'get_dbcheck_templates_as_itops_format',
    
    # 更新管理
    'DBCheckUpdater',
]

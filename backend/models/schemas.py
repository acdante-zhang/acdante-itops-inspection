# Oracle ADG 容灾管控平台 - 数据模型定义
# 基于 Acdante 四层云原生容灾架构

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================
# 枚举定义
# ============================================================

class OracleVersion(str, Enum):
    """Oracle 数据库版本枚举"""
    ORACLE_10G = "10g"
    ORACLE_11G = "11g"
    ORACLE_19C = "19c"
    ORACLE_23C = "23c"
    ORACLE_26AI = "26ai"


class InstanceRole(str, Enum):
    """数据库实例角色"""
    PRIMARY = "primary"
    STANDBY = "standby"


class DGType(str, Enum):
    """Data Guard 配置类型"""
    DG = "dg"          # 物理 DG
    ADG = "adg"        # Active Data Guard
    FSFO = "fsfo"      # Fast-Start Failover


class DGProtectionMode(str, Enum):
    """DG 保护模式"""
    MAX_PROTECTION = "最大保护"
    MAX_AVAILABILITY = "最大可用"
    MAX_PERFORMANCE = "最大性能"


class HealthStatus(str, Enum):
    """健康状态"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


class SyncStatus(str, Enum):
    """同步状态"""
    VALID = "VALID"
    GAP = "GAP"
    APPLYING = "APPLYING"
    ERROR = "ERROR"
    IDLE = "IDLE"


class TakeoverType(str, Enum):
    """容灾接管类型"""
    SWITCHOVER = "switchover"
    FAILOVER = "failover"
    REINSTATE = "reinstate"


class TakeoverStatus(str, Enum):
    """容灾操作状态"""
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    PLANNED = "planned"


class LogLevel(str, Enum):
    """日志级别"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogType(str, Enum):
    """日志类型"""
    ALERT = "alert"
    DG_BROKER = "dg_broker"
    SYNC = "sync"
    AUDIT = "audit"


class ZFSDatasetType(str, Enum):
    """ZFS 数据集类型"""
    DATAFILE = "datafile"
    REDO_LOG = "redo_log"
    ARCHIVE_LOG = "archive_log"
    CONTROLFILE = "controlfile"
    BACKUP = "backup"


class K8sResourceKind(str, Enum):
    """K8s 资源类型"""
    DEPLOYMENT = "deployment"
    STATEFULSET = "statefulset"
    SERVICE = "service"
    CONFIGMAP = "configmap"
    PVC = "pvc"
    POD = "pod"


# ============================================================
# 基础实体模型
# ============================================================

class OracleInstance(BaseModel):
    """Oracle 数据库实例"""
    id: str = Field(..., description="实例ID")
    name: str = Field(..., description="实例名称")
    version: OracleVersion = Field(..., description="Oracle版本")
    role: InstanceRole = Field(..., description="角色(primary/standby)")
    host: str = Field(..., description="主机地址")
    port: int = Field(default=1521, description="监听端口")
    db_unique_name: str = Field(..., description="DB_UNIQUE_NAME")
    open_mode: str = Field(default="READ WRITE", description="打开模式")
    health: HealthStatus = Field(default=HealthStatus.HEALTHY, description="健康状态")
    cpu_usage: float = Field(default=0.0, description="CPU使用率%")
    memory_usage: float = Field(default=0.0, description="内存使用率%")
    dg_config_id: Optional[str] = Field(default=None, description="所属DG配置ID")

    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.version.value})"


class DGConfig(BaseModel):
    """Data Guard 配置"""
    id: str = Field(..., description="配置ID")
    name: str = Field(..., description="配置名称")
    dg_type: DGType = Field(..., description="DG类型")
    protection_mode: DGProtectionMode = Field(..., description="保护模式")
    primary_id: str = Field(..., description="主库实例ID")
    standby_ids: list[str] = Field(default_factory=list, description="备库实例ID列表")
    health: HealthStatus = Field(default=HealthStatus.HEALTHY, description="健康状态")
    transport_lag: Optional[str] = Field(default=None, description="传输延迟")
    apply_lag: Optional[str] = Field(default=None, description="应用延迟")
    fsfo_enabled: bool = Field(default=False, description="是否启用FSFO")
    observer_host: Optional[str] = Field(default=None, description="Observer主机")
    sync_rate: float = Field(default=0.0, description="同步率%")
    created_at: Optional[str] = Field(default=None, description="创建时间")

    @property
    def is_adg(self) -> bool:
        return self.dg_type == DGType.ADG or self.dg_type == DGType.FSFO


class SyncLog(BaseModel):
    """同步日志记录"""
    id: str = Field(..., description="日志ID")
    dg_config_id: str = Field(..., description="DG配置ID")
    thread: int = Field(default=1, description="线程号")
    sequence: int = Field(..., description="日志序列号")
    standby_name: str = Field(..., description="备库名称")
    status: SyncStatus = Field(..., description="同步状态")
    transport_lag: Optional[str] = Field(default=None, description="传输延迟")
    apply_lag: Optional[str] = Field(default=None, description="应用延迟")
    received_time: Optional[str] = Field(default=None, description="接收时间")
    applied_time: Optional[str] = Field(default=None, description="应用时间")
    gap_start: Optional[int] = Field(default=None, description="GAP起始序列")
    gap_end: Optional[int] = Field(default=None, description="GAP结束序列")
    # 前端日志页面扩展字段
    source: str = Field(default="PRIMARY", description="源端")
    destination: str = Field(default="", description="目标端")
    lag_seconds: int = Field(default=0, description="延迟秒数")
    size_mb: int = Field(default=0, description="大小MB")
    timestamp: Optional[str] = Field(default=None, description="时间戳")


class AlertLog(BaseModel):
    """告警日志"""
    id: str = Field(..., description="告警ID")
    level: LogLevel = Field(..., description="告警级别")
    instance_id: Optional[str] = Field(default=None, description="相关实例ID")
    dg_config_id: Optional[str] = Field(default=None, description="相关DG配置ID")
    message: str = Field(..., description="告警消息")
    timestamp: str = Field(..., description="告警时间")
    source: Optional[str] = Field(default=None, description="日志来源")


class AuditLog(BaseModel):
    """审计日志"""
    id: str = Field(..., description="审计ID")
    action: str = Field(..., description="操作动作")
    resource_type: str = Field(..., description="资源类型")
    resource_id: str = Field(..., description="资源ID")
    user: str = Field(default="system", description="操作用户")
    result: str = Field(default="success", description="操作结果")
    details: Optional[str] = Field(default=None, description="操作详情")
    timestamp: str = Field(..., description="操作时间")


class FailoverHistory(BaseModel):
    """容灾操作历史"""
    id: str = Field(..., description="操作ID")
    dg_config_id: str = Field(..., description="DG配置ID")
    dg_config_name: str = Field(..., description="DG配置名称")
    operation: TakeoverType = Field(..., description="操作类型")
    status: TakeoverStatus = Field(..., description="操作状态")
    source: str = Field(..., description="源库")
    target: str = Field(..., description="目标库")
    operator: str = Field(default="system", description="操作人")
    start_time: str = Field(..., description="开始时间")
    end_time: Optional[str] = Field(default=None, description="结束时间")
    duration: Optional[str] = Field(default=None, description="耗时")
    notes: Optional[str] = Field(default=None, description="备注")


class ZFSDataset(BaseModel):
    """ZFS 数据集"""
    id: str = Field(..., description="数据集ID")
    name: str = Field(..., description="数据集名称")
    pool: str = Field(..., description="存储池")
    dataset_type: ZFSDatasetType = Field(..., description="数据集类型")
    used: str = Field(..., description="已用空间")
    avail: str = Field(..., description="可用空间")
    compress_ratio: str = Field(..., description="压缩率")
    mountpoint: str = Field(..., description="挂载点")
    snapshot_count: int = Field(default=0, description="快照数")


class K8sResource(BaseModel):
    """K8s 资源"""
    id: str = Field(..., description="资源ID")
    name: str = Field(..., description="资源名称")
    namespace: str = Field(default="oracle-dr", description="命名空间")
    kind: K8sResourceKind = Field(..., description="资源类型")
    status: str = Field(..., description="状态")
    replicas: Optional[int] = Field(default=None, description="副本数")
    ready_replicas: Optional[int] = Field(default=None, description="就绪副本数")
    instance_id: Optional[str] = Field(default=None, description="关联实例ID")
    labels: dict[str, str] = Field(default_factory=dict, description="标签")


class PerformanceMetric(BaseModel):
    """性能指标数据点"""
    timestamp: str = Field(..., description="时间戳")
    cpu_usage: float = Field(default=0.0, description="CPU使用率%")
    memory_usage: float = Field(default=0.0, description="内存使用率%")
    redo_rate: float = Field(default=0.0, description="Redo生成速率 MB/s")
    apply_rate: float = Field(default=0.0, description="Apply速率 MB/s")
    network_throughput: float = Field(default=0.0, description="网络吞吐 MB/s")
    iops: float = Field(default=0.0, description="IOPS")


class LogEntry(BaseModel):
    """日志条目"""
    id: str = Field(..., description="条目ID")
    log_type: LogType = Field(..., description="日志类型")
    instance_name: Optional[str] = Field(default=None, description="实例名称")
    timestamp: str = Field(..., description="时间戳")
    level: LogLevel = Field(default=LogLevel.INFO, description="日志级别")
    message: str = Field(..., description="日志内容")
    raw_line: Optional[str] = Field(default=None, description="原始日志行")


# ============================================================
# API 响应模型
# ============================================================

class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    total_instances: int = Field(..., description="实例总数")
    primary_count: int = Field(..., description="主库数量")
    standby_count: int = Field(..., description="备库数量")
    dg_config_count: int = Field(..., description="DG配置数量")
    healthy_count: int = Field(..., description="健康实例数")
    warning_count: int = Field(..., description="告警实例数")
    critical_count: int = Field(..., description="严重实例数")
    total_alerts: int = Field(..., description="告警总数")
    zfs_pool_count: int = Field(default=0, description="ZFS存储池数")
    k8s_resource_count: int = Field(default=0, description="K8s资源数")


class DGSetupRequest(BaseModel):
    """DG搭建请求"""
    config_name: str = Field(..., description="配置名称")
    dg_type: DGType = Field(..., description="DG类型")
    primary_instance_id: str = Field(..., description="主库实例ID")
    standby_instance_ids: list[str] = Field(..., description="备库实例ID列表")
    protection_mode: DGProtectionMode = Field(default=DGProtectionMode.MAX_PERFORMANCE)
    enable_fsfo: bool = Field(default=False, description="是否启用FSFO")
    observer_host: Optional[str] = Field(default=None, description="Observer主机")
    oracle_version: OracleVersion = Field(default=OracleVersion.ORACLE_19C)


class DGSetupStep(BaseModel):
    """DG搭建步骤"""
    step: int = Field(..., description="步骤序号")
    title: str = Field(..., description="步骤标题")
    description: str = Field(..., description="步骤描述")
    commands: list[str] = Field(default_factory=list, description="执行命令列表")
    status: str = Field(default="pending", description="步骤状态")


class DGSetupPlan(BaseModel):
    """DG搭建执行计划"""
    config_name: str = Field(..., description="配置名称")
    dg_type: DGType = Field(..., description="DG类型")
    oracle_version: OracleVersion = Field(..., description="Oracle版本")
    protection_mode: DGProtectionMode = Field(..., description="保护模式")
    fsfo_enabled: bool = Field(default=False, description="FSFO启用")
    steps: list[DGSetupStep] = Field(default_factory=list, description="搭建步骤列表")
    estimated_time: str = Field(default="30-60分钟", description="预估耗时")
    prerequisites: list[str] = Field(default_factory=list, description="前置条件")


class TakeoverRequest(BaseModel):
    """容灾接管请求"""
    dg_config_id: str = Field(..., description="DG配置ID")
    operation: TakeoverType = Field(..., description="操作类型")
    target_standby_id: Optional[str] = Field(default=None, description="目标备库ID")
    force: bool = Field(default=False, description="是否强制执行")
    skip_validation: bool = Field(default=False, description="跳过预检")


class TakeoverValidation(BaseModel):
    """容灾接管验证结果"""
    can_proceed: bool = Field(..., description="是否可执行")
    checks: list[dict] = Field(default_factory=list, description="检查项列表")
    warnings: list[str] = Field(default_factory=list, description="警告列表")
    errors: list[str] = Field(default_factory=list, description="错误列表")


class VersionFeatureMatrix(BaseModel):
    """版本特性支持矩阵"""
    version: OracleVersion = Field(..., description="Oracle版本")
    supports_adg: bool = Field(..., description="支持ADG")
    supports_fsfo: bool = Field(..., description="支持FSFO")
    supports_cascading: bool = Field(..., description="支持级联备库")
    supports_far_sync: bool = Field(..., description="支持Far Sync")
    supports_real_time_apply: bool = Field(..., description="支持实时Apply")
    supports_dml_overwrite: bool = Field(default=False, description="支持DML覆盖")
    max_standby_count: int = Field(default=1, description="最大备库数")
    notes: str = Field(default="", description="备注")

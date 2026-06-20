# Oracle ADG 容灾管控平台 - 核心数据服务
# 提供模拟数据生成与业务逻辑

from __future__ import annotations
import random
import uuid
from datetime import datetime, timedelta
from typing import Optional

from backend.models.schemas import (
    OracleVersion, InstanceRole, DGType, DGProtectionMode,
    HealthStatus, SyncStatus, TakeoverType, TakeoverStatus,
    LogLevel, LogType, ZFSDatasetType, K8sResourceKind,
    OracleInstance, DGConfig, SyncLog, AlertLog, AuditLog, FailoverHistory,
    ZFSDataset, K8sResource, PerformanceMetric, LogEntry,
    DashboardStats, DGSetupPlan, DGSetupStep, TakeoverValidation,
    VersionFeatureMatrix,
)


def _ts(minutes_ago: int = 0) -> str:
    """生成ISO格式时间戳"""
    dt = datetime.now() - timedelta(minutes=minutes_ago)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _gen_id(prefix: str = "") -> str:
    """生成唯一ID"""
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ============================================================
# 模拟数据生成
# ============================================================

class DataStore:
    """统一数据存储，模拟数据库"""

    def __init__(self):
        self.instances: dict[str, OracleInstance] = {}
        self.dg_configs: dict[str, DGConfig] = {}
        self.sync_logs: list[SyncLog] = []
        self.alert_logs: list[AlertLog] = []
        self.failover_history: list[FailoverHistory] = []
        self.zfs_datasets: list[ZFSDataset] = []
        self.k8s_resources: list[K8sResource] = []
        self.performance_metrics: dict[str, list[PerformanceMetric]] = {}
        self.log_entries: list[LogEntry] = []
        self.audit_logs: list[AuditLog] = []
        self._initialized = False

    def initialize(self):
        """初始化所有模拟数据"""
        if self._initialized:
            return
        self._init_instances()
        self._init_dg_configs()
        self._init_sync_logs()
        self._init_alert_logs()
        self._init_audit_logs()
        self._init_failover_history()
        self._init_zfs_datasets()
        self._init_k8s_resources()
        self._init_performance_metrics()
        self._init_log_entries()
        self._initialized = True

    def _init_instances(self):
        """初始化Oracle实例"""
        instances_data = [
            # 主库
            {"id": "inst-01", "name": "PROD-DB01", "version": OracleVersion.ORACLE_19C,
             "role": InstanceRole.PRIMARY, "host": "192.168.1.10", "port": 1521,
             "db_unique_name": "PROD_DB01", "open_mode": "READ WRITE",
             "health": HealthStatus.HEALTHY, "cpu_usage": 42.3, "memory_usage": 68.7,
             "dg_config_id": "dg-01"},
            {"id": "inst-02", "name": "PROD-DB02", "version": OracleVersion.ORACLE_23C,
             "role": InstanceRole.PRIMARY, "host": "192.168.1.20", "port": 1521,
             "db_unique_name": "PROD_DB02", "open_mode": "READ WRITE",
             "health": HealthStatus.HEALTHY, "cpu_usage": 35.1, "memory_usage": 55.2,
             "dg_config_id": "dg-02"},
            {"id": "inst-03", "name": "PROD-DB03", "version": OracleVersion.ORACLE_11G,
             "role": InstanceRole.PRIMARY, "host": "192.168.1.30", "port": 1521,
             "db_unique_name": "PROD_DB03", "open_mode": "READ WRITE",
             "health": HealthStatus.WARNING, "cpu_usage": 78.5, "memory_usage": 82.1,
             "dg_config_id": "dg-03"},
            {"id": "inst-04", "name": "PROD-DB04", "version": OracleVersion.ORACLE_26AI,
             "role": InstanceRole.PRIMARY, "host": "192.168.1.40", "port": 1521,
             "db_unique_name": "PROD_DB04", "open_mode": "READ WRITE",
             "health": HealthStatus.HEALTHY, "cpu_usage": 22.8, "memory_usage": 45.6,
             "dg_config_id": "dg-04"},
            {"id": "inst-05", "name": "PROD-DB05", "version": OracleVersion.ORACLE_10G,
             "role": InstanceRole.PRIMARY, "host": "192.168.1.50", "port": 1521,
             "db_unique_name": "PROD_DB05", "open_mode": "READ WRITE",
             "health": HealthStatus.HEALTHY, "cpu_usage": 31.2, "memory_usage": 52.8,
             "dg_config_id": "dg-05"},
            # 备库
            {"id": "inst-06", "name": "DR-DB01", "version": OracleVersion.ORACLE_19C,
             "role": InstanceRole.STANDBY, "host": "192.168.2.10", "port": 1521,
             "db_unique_name": "DR_DB01", "open_mode": "READ ONLY WITH APPLY",
             "health": HealthStatus.HEALTHY, "cpu_usage": 18.4, "memory_usage": 42.3,
             "dg_config_id": "dg-01"},
            {"id": "inst-07", "name": "DR-DB02", "version": OracleVersion.ORACLE_23C,
             "role": InstanceRole.STANDBY, "host": "192.168.2.20", "port": 1521,
             "db_unique_name": "DR_DB02", "open_mode": "READ ONLY WITH APPLY",
             "health": HealthStatus.HEALTHY, "cpu_usage": 15.2, "memory_usage": 38.7,
             "dg_config_id": "dg-02"},
            {"id": "inst-08", "name": "DR-DB03", "version": OracleVersion.ORACLE_11G,
             "role": InstanceRole.STANDBY, "host": "192.168.2.30", "port": 1521,
             "db_unique_name": "DR_DB03", "open_mode": "MOUNTED",
             "health": HealthStatus.CRITICAL, "cpu_usage": 5.1, "memory_usage": 12.4,
             "dg_config_id": "dg-03"},
            {"id": "inst-09", "name": "DR-DB04A", "version": OracleVersion.ORACLE_26AI,
             "role": InstanceRole.STANDBY, "host": "192.168.2.40", "port": 1521,
             "db_unique_name": "DR_DB04A", "open_mode": "READ ONLY WITH APPLY",
             "health": HealthStatus.HEALTHY, "cpu_usage": 12.3, "memory_usage": 35.8,
             "dg_config_id": "dg-04"},
            {"id": "inst-10", "name": "DR-DB04B", "version": OracleVersion.ORACLE_26AI,
             "role": InstanceRole.STANDBY, "host": "192.168.3.40", "port": 1521,
             "db_unique_name": "DR_DB04B", "open_mode": "READ ONLY WITH APPLY",
             "health": HealthStatus.WARNING, "cpu_usage": 45.6, "memory_usage": 62.3,
             "dg_config_id": "dg-04"},
            {"id": "inst-11", "name": "DR-DB05", "version": OracleVersion.ORACLE_10G,
             "role": InstanceRole.STANDBY, "host": "192.168.2.50", "port": 1521,
             "db_unique_name": "DR_DB05", "open_mode": "READ ONLY",
             "health": HealthStatus.HEALTHY, "cpu_usage": 8.9, "memory_usage": 28.5,
             "dg_config_id": "dg-05"},
        ]
        for d in instances_data:
            inst = OracleInstance(**d)
            self.instances[inst.id] = inst

    def _init_dg_configs(self):
        """初始化DG配置"""
        configs_data = [
            {"id": "dg-01", "name": "PROD-19C-ADG", "dg_type": DGType.ADG,
             "protection_mode": DGProtectionMode.MAX_AVAILABILITY,
             "primary_id": "inst-01", "standby_ids": ["inst-06"],
             "health": HealthStatus.HEALTHY,
             "transport_lag": "0s", "apply_lag": "1s",
             "fsfo_enabled": False, "sync_rate": 99.8},
            {"id": "dg-02", "name": "PROD-23C-FSFO", "dg_type": DGType.FSFO,
             "protection_mode": DGProtectionMode.MAX_AVAILABILITY,
             "primary_id": "inst-02", "standby_ids": ["inst-07"],
             "health": HealthStatus.HEALTHY,
             "transport_lag": "0s", "apply_lag": "0s",
             "fsfo_enabled": True, "observer_host": "observer-01.dr.local",
             "sync_rate": 100.0},
            {"id": "dg-03", "name": "PROD-11G-DG", "dg_type": DGType.DG,
             "protection_mode": DGProtectionMode.MAX_PERFORMANCE,
             "primary_id": "inst-03", "standby_ids": ["inst-08"],
             "health": HealthStatus.CRITICAL,
             "transport_lag": "120s", "apply_lag": "300s",
             "fsfo_enabled": False, "sync_rate": 45.2},
            {"id": "dg-04", "name": "PROD-26AI-ADG", "dg_type": DGType.ADG,
             "protection_mode": DGProtectionMode.MAX_PROTECTION,
             "primary_id": "inst-04", "standby_ids": ["inst-09", "inst-10"],
             "health": HealthStatus.WARNING,
             "transport_lag": "0s", "apply_lag": "5s",
             "fsfo_enabled": True, "observer_host": "observer-02.dr.local",
             "sync_rate": 96.5},
            {"id": "dg-05", "name": "PROD-10G-DG", "dg_type": DGType.DG,
             "protection_mode": DGProtectionMode.MAX_PERFORMANCE,
             "primary_id": "inst-05", "standby_ids": ["inst-11"],
             "health": HealthStatus.HEALTHY,
             "transport_lag": "2s", "apply_lag": "8s",
             "fsfo_enabled": False, "sync_rate": 92.1},
        ]
        for d in configs_data:
            cfg = DGConfig(**d, created_at=_ts(random.randint(10000, 50000)))
            self.dg_configs[cfg.id] = cfg

    def _init_sync_logs(self):
        """初始化同步日志"""
        dg_ids = list(self.dg_configs.keys())
        statuses = [SyncStatus.VALID, SyncStatus.VALID, SyncStatus.VALID,
                    SyncStatus.GAP, SyncStatus.APPLYING]
        seq = 1000
        for i in range(50):
            dg_id = random.choice(dg_ids)
            cfg = self.dg_configs[dg_id]
            standby = None
            for sid in cfg.standby_ids:
                standby = self.instances.get(sid)
                if standby:
                    break
            primary_inst = self.instances.get(cfg.primary_id)
            src = primary_inst.name if primary_inst else "PRIMARY"
            dst = standby.name if standby else "STANDBY"
            self.sync_logs.append(SyncLog(
                id=f"sync-{i+1:03d}",
                dg_config_id=dg_id,
                thread=random.choice([1, 2]),
                sequence=seq + i,
                standby_name=standby.name if standby else "UNKNOWN",
                status=random.choice(statuses),
                transport_lag=f"{random.randint(0, 10)}s" if random.random() > 0.3 else None,
                apply_lag=f"{random.randint(0, 30)}s" if random.random() > 0.2 else None,
                received_time=_ts(random.randint(1, 300)),
                applied_time=_ts(random.randint(0, 60)) if random.random() > 0.3 else None,
                source=src,
                destination=dst,
                lag_seconds=random.randint(0, 30),
                size_mb=random.choice([8, 16, 32, 64, 128]),
                timestamp=_ts(random.randint(1, 300)),
            ))

    def _init_alert_logs(self):
        """初始化告警日志"""
        alerts_data = [
            {"id": "alert-01", "level": LogLevel.CRITICAL, "instance_id": "inst-08",
             "dg_config_id": "dg-03", "message": "DR-DB03 与主库同步中断超过5分钟",
             "source": "DMON"},
            {"id": "alert-02", "level": LogLevel.WARNING, "instance_id": "inst-10",
             "dg_config_id": "dg-04", "message": "DR-DB04B Apply延迟超过5秒阈值",
             "source": "Broker"},
            {"id": "alert-03", "level": LogLevel.WARNING, "instance_id": "inst-03",
             "message": "PROD-DB03 CPU使用率超过75%", "source": "ORACLE"},
            {"id": "alert-04", "level": LogLevel.INFO, "dg_config_id": "dg-02",
             "message": "PROD-23C-FSFO FSFO Observer 心跳正常", "source": "Observer"},
            {"id": "alert-05", "level": LogLevel.ERROR, "instance_id": "inst-08",
             "dg_config_id": "dg-03", "message": "DR-DB03 ORA-12154 TNS解析失败",
             "source": "TNS"},
            {"id": "alert-06", "level": LogLevel.WARNING, "instance_id": "inst-10",
             "dg_config_id": "dg-04", "message": "DR-DB04B 磁盘使用率达到80%",
             "source": "ORACLE"},
            {"id": "alert-07", "level": LogLevel.INFO, "dg_config_id": "dg-01",
             "message": "PROD-19C-ADG Redo传输正常，延迟 <1s", "source": "Broker"},
            {"id": "alert-08", "level": LogLevel.ERROR, "instance_id": "inst-08",
             "dg_config_id": "dg-03", "message": "DR-DB03 ORA-01034 Oracle不可用",
             "source": "DMON"},
            {"id": "alert-09", "level": LogLevel.INFO, "dg_config_id": "dg-04",
             "message": "PROD-26AI-ADG 自动GAP恢复已启动", "source": "Broker"},
            {"id": "alert-10", "level": LogLevel.WARNING, "instance_id": "inst-03",
             "dg_config_id": "dg-03", "message": "PROD-DB03 内存使用率超过80%",
             "source": "ORACLE"},
        ]
        for i, d in enumerate(alerts_data):
            self.alert_logs.append(AlertLog(**d, timestamp=_ts(i * 5 + 1)))

    def _init_audit_logs(self):
        """初始化审计日志"""
        audit_data = [
            {"id": "audit-01", "action": "SWITCHOVER", "resource_type": "dg_config",
             "resource_id": "dg-01", "user": "admin", "result": "success",
             "details": "PROD-19C-ADG 计划内Switchover演练", "timestamp": _ts(1440)},
            {"id": "audit-02", "action": "FAILOVER", "resource_type": "dg_config",
             "resource_id": "dg-03", "user": "system", "result": "success",
             "details": "PROD-11G-DG 主库故障自动Failover", "timestamp": _ts(720)},
            {"id": "audit-03", "action": "LOGIN", "resource_type": "session",
             "resource_id": "session-01", "user": "admin", "result": "success",
             "details": "管理员登录系统", "timestamp": _ts(60)},
            {"id": "audit-04", "action": "CONFIG_UPDATE", "resource_type": "dg_config",
             "resource_id": "dg-04", "user": "admin", "result": "success",
             "details": "更新PROD-26AI-ADG保护模式为最大可用", "timestamp": _ts(120)},
            {"id": "audit-05", "action": "SNAPSHOT_CREATE", "resource_type": "zfs_dataset",
             "resource_id": "zfs-01", "user": "system", "result": "success",
             "details": "ZFS自动快照: tank/oracle/datafile@auto_20240115", "timestamp": _ts(30)},
            {"id": "audit-06", "action": "REINSTATE", "resource_type": "dg_config",
             "resource_id": "dg-01", "user": "admin", "result": "success",
             "details": "PROD-19C-ADG 恢复原主库", "timestamp": _ts(1410)},
            {"id": "audit-07", "action": "SCALE_OUT", "resource_type": "k8s_resource",
             "resource_id": "k8s-01", "user": "admin", "result": "success",
             "details": "oracle-primary 扩容至2副本", "timestamp": _ts(180)},
            {"id": "audit-08", "action": "LOGIN", "resource_type": "session",
             "resource_id": "session-02", "user": "operator1", "result": "failed",
             "details": "登录失败: 密码错误", "timestamp": _ts(45)},
            {"id": "audit-09", "action": "PARAM_CHANGE", "resource_type": "oracle_instance",
             "resource_id": "inst-01", "user": "dba_user", "result": "success",
             "details": "修改参数 log_archive_dest_2", "timestamp": _ts(90)},
            {"id": "audit-10", "action": "BACKUP", "resource_type": "zfs_dataset",
             "resource_id": "zfs-03", "user": "system", "result": "success",
             "details": "归档日志备份: tank/oracle/archive_log", "timestamp": _ts(15)},
        ]
        for d in audit_data:
            self.audit_logs.append(AuditLog(**d))

    def _init_failover_history(self):
        """初始化容灾操作历史"""
        history_data = [
            {"id": "fo-01", "dg_config_id": "dg-01", "dg_config_name": "PROD-19C-ADG",
             "operation": TakeoverType.SWITCHOVER, "status": TakeoverStatus.COMPLETED,
             "source": "PROD-DB01", "target": "DR-DB01",
             "operator": "admin", "start_time": _ts(1440), "end_time": _ts(1435),
             "duration": "5分钟", "notes": "计划内Switchover演练"},
            {"id": "fo-02", "dg_config_id": "dg-03", "dg_config_name": "PROD-11G-DG",
             "operation": TakeoverType.FAILOVER, "status": TakeoverStatus.COMPLETED,
             "source": "PROD-DB03", "target": "DR-DB03",
             "operator": "system", "start_time": _ts(720), "end_time": _ts(715),
             "duration": "5分钟", "notes": "主库故障自动Failover"},
            {"id": "fo-03", "dg_config_id": "dg-02", "dg_config_name": "PROD-23C-FSFO",
             "operation": TakeoverType.SWITCHOVER, "status": TakeoverStatus.COMPLETED,
             "source": "PROD-DB02", "target": "DR-DB02",
             "operator": "admin", "start_time": _ts(4320), "end_time": _ts(4315),
             "duration": "5分钟", "notes": "季度Switchover测试"},
            {"id": "fo-04", "dg_config_id": "dg-01", "dg_config_name": "PROD-19C-ADG",
             "operation": TakeoverType.REINSTATE, "status": TakeoverStatus.COMPLETED,
             "source": "DR-DB01", "target": "PROD-DB01",
             "operator": "admin", "start_time": _ts(1410), "end_time": _ts(1405),
             "duration": "5分钟", "notes": "Switchover后恢复原主库"},
            {"id": "fo-05", "dg_config_id": "dg-04", "dg_config_name": "PROD-26AI-ADG",
             "operation": TakeoverType.SWITCHOVER, "status": TakeoverStatus.PLANNED,
             "source": "PROD-DB04", "target": "DR-DB04A",
             "operator": "admin", "start_time": "", "notes": "计划中 - 待确认"},
        ]
        for d in history_data:
            self.failover_history.append(FailoverHistory(**d))

    def _init_zfs_datasets(self):
        """初始化ZFS数据集"""
        datasets_data = [
            {"id": "zfs-01", "name": "tank/oracle/prod-db01/data", "pool": "tank",
             "dataset_type": ZFSDatasetType.DATAFILE, "used": "256G", "avail": "744G",
             "compress_ratio": "2.15x", "mountpoint": "/oracle/prod-db01/data",
             "snapshot_count": 48},
            {"id": "zfs-02", "name": "tank/oracle/prod-db01/redo", "pool": "tank",
             "dataset_type": ZFSDatasetType.REDO_LOG, "used": "16G", "avail": "984G",
             "compress_ratio": "1.05x", "mountpoint": "/oracle/prod-db01/redo",
             "snapshot_count": 48},
            {"id": "zfs-03", "name": "tank/oracle/prod-db01/archive", "pool": "tank",
             "dataset_type": ZFSDatasetType.ARCHIVE_LOG, "used": "128G", "avail": "872G",
             "compress_ratio": "3.42x", "mountpoint": "/oracle/prod-db01/archive",
             "snapshot_count": 48},
            {"id": "zfs-04", "name": "tank/oracle/prod-db02/data", "pool": "tank",
             "dataset_type": ZFSDatasetType.DATAFILE, "used": "512G", "avail": "488G",
             "compress_ratio": "1.98x", "mountpoint": "/oracle/prod-db02/data",
             "snapshot_count": 48},
            {"id": "zfs-05", "name": "tank/oracle/prod-db03/control", "pool": "tank",
             "dataset_type": ZFSDatasetType.CONTROLFILE, "used": "512M", "avail": "999.5G",
             "compress_ratio": "1.01x", "mountpoint": "/oracle/prod-db03/control",
             "snapshot_count": 24},
            {"id": "zfs-06", "name": "tank/backup/rman", "pool": "tank",
             "dataset_type": ZFSDatasetType.BACKUP, "used": "1.2T", "avail": "3.8T",
             "compress_ratio": "4.21x", "mountpoint": "/backup/rman",
             "snapshot_count": 12},
        ]
        for d in datasets_data:
            self.zfs_datasets.append(ZFSDataset(**d))

    def _init_k8s_resources(self):
        """初始化K8s资源"""
        resources_data = [
            {"id": "k8s-01", "name": "oracle-prod-db01", "namespace": "oracle-dr",
             "kind": K8sResourceKind.STATEFULSET, "status": "Running",
             "replicas": 1, "ready_replicas": 1, "instance_id": "inst-01",
             "labels": {"app": "oracle", "instance": "prod-db01", "version": "19c"}},
            {"id": "k8s-02", "name": "oracle-prod-db02", "namespace": "oracle-dr",
             "kind": K8sResourceKind.STATEFULSET, "status": "Running",
             "replicas": 1, "ready_replicas": 1, "instance_id": "inst-02",
             "labels": {"app": "oracle", "instance": "prod-db02", "version": "23c"}},
            {"id": "k8s-03", "name": "oracle-prod-db03", "namespace": "oracle-dr",
             "kind": K8sResourceKind.STATEFULSET, "status": "Running",
             "replicas": 1, "ready_replicas": 1, "instance_id": "inst-03",
             "labels": {"app": "oracle", "instance": "prod-db03", "version": "11g"}},
            {"id": "k8s-04", "name": "oracle-dr-db01", "namespace": "oracle-dr",
             "kind": K8sResourceKind.STATEFULSET, "status": "Running",
             "replicas": 1, "ready_replicas": 1, "instance_id": "inst-06",
             "labels": {"app": "oracle", "instance": "dr-db01", "role": "standby"}},
            {"id": "k8s-05", "name": "oracle-dr-db02", "namespace": "oracle-dr",
             "kind": K8sResourceKind.STATEFULSET, "status": "Running",
             "replicas": 1, "ready_replicas": 1, "instance_id": "inst-07",
             "labels": {"app": "oracle", "instance": "dr-db02", "role": "standby"}},
            {"id": "k8s-06", "name": "oracle-dr-db03", "namespace": "oracle-dr",
             "kind": K8sResourceKind.STATEFULSET, "status": "CrashLoopBackOff",
             "replicas": 1, "ready_replicas": 0, "instance_id": "inst-08",
             "labels": {"app": "oracle", "instance": "dr-db03", "role": "standby"}},
            {"id": "k8s-07", "name": "oracle-svc-prod-db01", "namespace": "oracle-dr",
             "kind": K8sResourceKind.SERVICE, "status": "Active",
             "instance_id": "inst-01"},
            {"id": "k8s-08", "name": "oracle-svc-prod-db02", "namespace": "oracle-dr",
             "kind": K8sResourceKind.SERVICE, "status": "Active",
             "instance_id": "inst-02"},
            {"id": "k8s-09", "name": "oracle-config-common", "namespace": "oracle-dr",
             "kind": K8sResourceKind.CONFIGMAP, "status": "Active"},
            {"id": "k8s-10", "name": "oracle-pvc-prod-db01", "namespace": "oracle-dr",
             "kind": K8sResourceKind.PVC, "status": "Bound",
             "instance_id": "inst-01"},
            {"id": "k8s-11", "name": "observer-fsfo-01", "namespace": "oracle-dr",
             "kind": K8sResourceKind.DEPLOYMENT, "status": "Running",
             "replicas": 1, "ready_replicas": 1},
            {"id": "k8s-12", "name": "observer-fsfo-02", "namespace": "oracle-dr",
             "kind": K8sResourceKind.DEPLOYMENT, "status": "Running",
             "replicas": 1, "ready_replicas": 1},
            {"id": "k8s-13", "name": "oracle-dr-db04a", "namespace": "oracle-dr",
             "kind": K8sResourceKind.STATEFULSET, "status": "Running",
             "replicas": 1, "ready_replicas": 1, "instance_id": "inst-09"},
            {"id": "k8s-14", "name": "oracle-dr-db04b", "namespace": "oracle-dr",
             "kind": K8sResourceKind.STATEFULSET, "status": "Running",
             "replicas": 1, "ready_replicas": 1, "instance_id": "inst-10"},
        ]
        for d in resources_data:
            self.k8s_resources.append(K8sResource(**d))

    def _init_performance_metrics(self):
        """初始化性能指标（30分钟历史数据，每分钟一个点）"""
        for inst_id in ["inst-01", "inst-02", "inst-03", "inst-04", "inst-05"]:
            metrics = []
            base_cpu = random.uniform(20, 60)
            base_mem = random.uniform(40, 70)
            for i in range(30):
                ts = _ts(29 - i)
                cpu = max(0, min(100, base_cpu + random.uniform(-10, 10)))
                mem = max(0, min(100, base_mem + random.uniform(-5, 5)))
                base_cpu = cpu
                base_mem = mem
                metrics.append(PerformanceMetric(
                    timestamp=ts,
                    cpu_usage=round(cpu, 1),
                    memory_usage=round(mem, 1),
                    redo_rate=round(random.uniform(1.5, 25.0), 2),
                    apply_rate=round(random.uniform(1.0, 22.0), 2),
                    network_throughput=round(random.uniform(10, 100), 1),
                    iops=round(random.uniform(500, 5000), 0),
                ))
            self.performance_metrics[inst_id] = metrics

    def _init_log_entries(self):
        """初始化日志条目（终端风格）"""
        alert_entries = [
            {"level": LogLevel.INFO, "message": "Starting ORACLE instance (normal)"},
            {"level": LogLevel.INFO, "message": "ALTER DATABASE   MOUNT"},
            {"level": LogLevel.INFO, "message": "Successful mount of thread 1, with mount ID 4231768502"},
            {"level": LogLevel.INFO, "message": "Database mounted in Exclusive Mode"},
            {"level": LogLevel.INFO, "message": "Lost write protection disabled"},
            {"level": LogLevel.INFO, "message": "Physical Standby: Real Time Apply enabled"},
            {"level": LogLevel.INFO, "message": "RFS[1]: Assigned to RFS process 12345"},
            {"level": LogLevel.INFO, "message": "RFS[1]: Selected log 4 for thread 1 sequence 1024"},
            {"level": LogLevel.INFO, "message": "Recovery of Online Redo Log: Thread 1 Group 2 Seq 1024"},
            {"level": LogLevel.WARNING, "message": "ORA-16198: Remote Archive destination LAGGING"},
            {"level": LogLevel.INFO, "message": "Media Recovery Waiting for thread 1 sequence 1025"},
            {"level": LogLevel.INFO, "message": "RFS[2]: Assigned to RFS process 12346"},
            {"level": LogLevel.WARNING, "message": "TNS-12541: TNS:no listener - retrying connection"},
            {"level": LogLevel.INFO, "message": "RFS[2]: Selected log 5 for thread 1 sequence 1025"},
            {"level": LogLevel.ERROR, "message": "ORA-03113: end-of-file on communication channel"},
            {"level": LogLevel.INFO, "message": "Media Recovery Log /archive/1_1025_890123.arc"},
            {"level": LogLevel.INFO, "message": "Incomplete Recovery applied until change 12345678"},
            {"level": LogLevel.INFO, "message": "MRP0: Background Media Recovery process started"},
            {"level": LogLevel.INFO, "message": "Physical Standby: Received redo for thread 1 seq 1026"},
            {"level": LogLevel.CRITICAL, "message": "ORA-01034: ORACLE not available"},
            {"level": LogLevel.INFO, "message": "PING[ARC1]: Heartbeat ping to inst-01 successful"},
            {"level": LogLevel.INFO, "message": "ARC1: Archiving to standby 'DR-DB01'"},
            {"level": LogLevel.INFO, "message": "LNS1: Async LGWR network server process started"},
            {"level": LogLevel.INFO, "message": "RFS[3]: Opened log for thread 1 sequence 1026"},
            {"level": LogLevel.WARNING, "message": "ORA-16075: standby database recovery deferred"},
            {"level": LogLevel.INFO, "message": "Media Recovery Waiting for thread 1 sequence 1027"},
            {"level": LogLevel.INFO, "message": "ALTER SYSTEM ARCHIVE LOG"},
            {"level": LogLevel.INFO, "message": "Thread 1 advanced to log sequence 1027"},
            {"level": LogLevel.INFO, "message": "Current log# 3 seq# 1027 mem# 0: /redo/redo03.log"},
            {"level": LogLevel.ERROR, "message": "ORA-12514: TNS:listener does not currently know of service"},
        ]

        # DG Broker 日志
        broker_entries = [
            {"level": LogLevel.INFO, "message": "DMON: Starting Data Guard Broker process"},
            {"level": LogLevel.INFO, "message": "DGMGRL> show configuration"},
            {"level": LogLevel.INFO, "message": "Configuration - PROD-19C-ADG"},
            {"level": LogLevel.INFO, "message": "  Primary: PROD-DB01 as PROD-DB01"},
            {"level": LogLevel.INFO, "message": "  Physical Standby: DR-DB01 as DR-DB01"},
            {"level": LogLevel.INFO, "message": "Fast-Start Failover: DISABLED"},
            {"level": LogLevel.INFO, "message": "Configuration Status: SUCCESS"},
            {"level": LogLevel.INFO, "message": "DMON: Observer connection established"},
            {"level": LogLevel.WARNING, "message": "ORA-16810: Member has errors requiring notification"},
            {"level": LogLevel.INFO, "message": "DGMGRL> show database DR-DB01"},
            {"level": LogLevel.INFO, "message": "Database - DR-DB01"},
            {"level": LogLevel.INFO, "message": "  Intended State: APPLY-ON"},
            {"level": LogLevel.INFO, "message": "  Transport Lag: 0 seconds"},
            {"level": LogLevel.INFO, "message": "  Apply Lag: 1 second"},
            {"level": LogLevel.INFO, "message": "  Real Time Query: ON"},
            {"level": LogLevel.INFO, "message": "Instance Status: SUCCESS"},
        ]

        # 生成 Alert Log
        for i, e in enumerate(alert_entries):
            self.log_entries.append(LogEntry(
                id=f"log-a-{i+1:03d}",
                log_type=LogType.ALERT,
                instance_name="DR-DB01" if i % 2 == 0 else "PROD-DB01",
                timestamp=_ts(29 - i),
                level=e["level"],
                message=e["message"],
            ))

        # 生成 DG Broker 日志
        for i, e in enumerate(broker_entries):
            self.log_entries.append(LogEntry(
                id=f"log-b-{i+1:03d}",
                log_type=LogType.DG_BROKER,
                instance_name="observer-01",
                timestamp=_ts(29 - i),
                level=e["level"],
                message=e["message"],
            ))

        # 生成同步日志
        sync_msgs = [
            "Primary LNS1 transmitting redo thread 1 seq 1024",
            "Standby RFS1 received redo thread 1 seq 1024",
            "MRP0 applying redo thread 1 seq 1024 block 1024",
            "Primary LNS1 transmitting redo thread 1 seq 1025",
            "Standby RFS1 received redo thread 1 seq 1025",
            "GAP detected: requesting seq 1023 from primary",
            "Primary ARC0 shipping seq 1023 to standby",
            "Standby RFS2 received redo thread 1 seq 1023 (GAP fill)",
            "MRP0 applying redo thread 1 seq 1023 block 512 (GAP recovery)",
            "GAP recovery complete, resuming real-time apply",
        ]
        for i, msg in enumerate(sync_msgs):
            self.log_entries.append(LogEntry(
                id=f"log-s-{i+1:03d}",
                log_type=LogType.SYNC,
                instance_name="DR-DB01" if i % 2 == 0 else "PROD-DB01",
                timestamp=_ts(9 - i),
                level=LogLevel.WARNING if "GAP" in msg else LogLevel.INFO,
                message=msg,
            ))

        # 生成审计日志
        audit_msgs = [
            "ACTION: 'ALTER DATABASE OPEN' by SYS",
            "ACTION: 'ALTER SYSTEM SWITCH LOGFILE' by SYS",
            "ACTION: 'ALTER DATABASE RECOVER MANAGED STANDBY DATABASE CANCEL' by SYS",
            "ACTION: 'ALTER SESSION SET NLS_DATE_FORMAT' by SYSTEM",
            "ACTION: 'SELECT * FROM V$DATAGUARD_CONFIG' by MONITOR",
            "ACTION: 'ALTER SYSTEM ARCHIVE LOG CURRENT' by SYS",
            "ACTION: 'CREATE RESTORE POINT GUARANTEE_FLASHBACK' by SYS",
        ]
        for i, msg in enumerate(audit_msgs):
            self.log_entries.append(LogEntry(
                id=f"log-u-{i+1:03d}",
                log_type=LogType.AUDIT,
                instance_name="PROD-DB01",
                timestamp=_ts(29 - i * 4),
                level=LogLevel.INFO,
                message=msg,
            ))


# ============================================================
# 全局数据存储单例
# ============================================================
_store: Optional[DataStore] = None


def get_store() -> DataStore:
    """获取全局数据存储实例"""
    global _store
    if _store is None:
        _store = DataStore()
        _store.initialize()
    return _store


# ============================================================
# 业务逻辑服务
# ============================================================

class DGService:
    """Data Guard 配置管理服务"""

    @staticmethod
    def get_dashboard_stats() -> DashboardStats:
        store = get_store()
        instances = list(store.instances.values())
        configs = list(store.dg_configs.values())
        alerts = store.alert_logs
        return DashboardStats(
            total_instances=len(instances),
            primary_count=sum(1 for i in instances if i.role == InstanceRole.PRIMARY),
            standby_count=sum(1 for i in instances if i.role == InstanceRole.STANDBY),
            dg_config_count=len(configs),
            healthy_count=sum(1 for i in instances if i.health == HealthStatus.HEALTHY),
            warning_count=sum(1 for i in instances if i.health == HealthStatus.WARNING),
            critical_count=sum(1 for i in instances if i.health == HealthStatus.CRITICAL),
            total_alerts=len(alerts),
            zfs_pool_count=len(set(d.pool for d in store.zfs_datasets)),
            k8s_resource_count=len(store.k8s_resources),
        )

    @staticmethod
    def get_version_matrix() -> list[VersionFeatureMatrix]:
        return [
            VersionFeatureMatrix(version=OracleVersion.ORACLE_10G, supports_adg=False,
                supports_fsfo=False, supports_cascading=False, supports_far_sync=False,
                supports_real_time_apply=False, max_standby_count=1,
                notes="仅支持物理DG，需手动管理"),
            VersionFeatureMatrix(version=OracleVersion.ORACLE_11G, supports_adg=True,
                supports_fsfo=True, supports_cascading=True, supports_far_sync=False,
                supports_real_time_apply=True, max_standby_count=11,
                notes="首次支持ADG和FSFO"),
            VersionFeatureMatrix(version=OracleVersion.ORACLE_19C, supports_adg=True,
                supports_fsfo=True, supports_cascading=True, supports_far_sync=True,
                supports_real_time_apply=True, max_standby_count=31,
                notes="LTS版本，支持DMO在线迁移"),
            VersionFeatureMatrix(version=OracleVersion.ORACLE_23C, supports_adg=True,
                supports_fsfo=True, supports_cascading=True, supports_far_sync=True,
                supports_real_time_apply=True, supports_dml_overwrite=True,
                max_standby_count=31,
                notes="支持DML Overwrite增强ADG"),
            VersionFeatureMatrix(version=OracleVersion.ORACLE_26AI, supports_adg=True,
                supports_fsfo=True, supports_cascading=True, supports_far_sync=True,
                supports_real_time_apply=True, supports_dml_overwrite=True,
                max_standby_count=63,
                notes="AI增强自治容灾，支持自动GAP恢复"),
        ]

    @staticmethod
    def generate_setup_plan(config_name: str, dg_type: DGType,
                            oracle_version: OracleVersion,
                            protection_mode: DGProtectionMode,
                            fsfo_enabled: bool) -> DGSetupPlan:
        """生成DG搭建执行计划"""
        steps = [
            DGSetupStep(step=1, title="环境预检",
                description="验证主备库版本、网络连通性、磁盘空间",
                commands=[
                    "sqlplus / as sysdba @precheck_primary.sql",
                    "tnsping DR_DB_TNS",
                    "df -h /oracle /archive",
                ]),
            DGSetupStep(step=2, title="主库配置",
                description="开启FORCE LOGGING、ARCHIVELOG，配置参数",
                commands=[
                    "ALTER DATABASE FORCE LOGGING;",
                    "ALTER SYSTEM SET LOG_ARCHIVE_CONFIG='DG_CONFIG=(PROD,DR)' SCOPE=BOTH;",
                    "ALTER SYSTEM SET LOG_ARCHIVE_DEST_2='SERVICE=DR_DB ASYNC VALID_FOR=(ONLINE_LOGFILE,PRIMARY_ROLE) DB_UNIQUE_NAME=DR' SCOPE=BOTH;",
                    "ALTER SYSTEM SET FAL_SERVER=DR_DB SCOPE=BOTH;",
                ]),
            DGSetupStep(step=3, title="备份传输",
                description="RMAN备份主库并传输到备库",
                commands=[
                    "rman target / DUPLICATE TARGET DATABASE FOR STANDBY FROM ACTIVE DATABASE;",
                ]),
            DGSetupStep(step=4, title="备库配置与启动",
                description="配置备库参数，启动MRP进程",
                commands=[
                    "ALTER SYSTEM SET LOG_ARCHIVE_CONFIG='DG_CONFIG=(DR,PROD)' SCOPE=BOTH;",
                    "ALTER SYSTEM SET FAL_SERVER=PROD_DB SCOPE=BOTH;",
                    "ALTER DATABASE RECOVER MANAGED STANDBY DATABASE DISCONNECT FROM SESSION;",
                ]),
        ]

        if dg_type in (DGType.ADG, DGType.FSFO):
            steps.append(DGSetupStep(step=5, title="ADG/FSFO配置",
                description="启用实时Apply，配置FSFO Observer",
                commands=[
                    "ALTER DATABASE RECOVER MANAGED STANDBY DATABASE CANCEL;",
                    "ALTER DATABASE OPEN READ ONLY;",
                    "ALTER DATABASE RECOVER MANAGED STANDBY DATABASE USING CURRENT LOGFILE DISCONNECT;",
                ]))
            if fsfo_enabled:
                steps[-1].commands.extend([
                    "DGMGRL> EDIT CONFIGURATION SET FASTSTARTFAILOVERTARGET 'DR_DB';",
                    "DGMGRL> ENABLE FAST_START FAILOVER;",
                    "start observer",
                ])

        if dg_type == DGType.DG:
            steps.append(DGSetupStep(step=5, title="DG验证",
                description="验证DG配置和同步状态",
                commands=[
                    "SELECT DATABASE_ROLE, OPEN_MODE FROM V$DATABASE;",
                    "SELECT STATUS, GAP_STATUS FROM V$DATAGUARD_STATS;",
                    "ALTER SYSTEM SWITCH LOGFILE;",
                ]))

        # 版本特殊处理
        version_notes = ""
        if oracle_version == OracleVersion.ORACLE_10G:
            version_notes = "10g不支持ADG和FSFO，仅可配置物理DG"
        elif oracle_version == OracleVersion.ORACLE_26AI:
            version_notes = "26ai支持自动GAP恢复，建议启用自治容灾"

        return DGSetupPlan(
            config_name=config_name,
            dg_type=dg_type,
            oracle_version=oracle_version,
            protection_mode=protection_mode,
            fsfo_enabled=fsfo_enabled,
            steps=steps,
            estimated_time="30-60分钟",
            prerequisites=[
                "主备库Oracle版本一致",
                "网络互通（TCP 1521端口）",
                "备库磁盘空间 >= 主库数据量",
                "主库已开启ARCHIVELOG模式",
                "已创建密码文件和TNS配置",
            ] + ([version_notes] if version_notes else []),
        )

    @staticmethod
    def validate_takeover(dg_config_id: str, operation: TakeoverType) -> TakeoverValidation:
        """验证容灾接管是否可执行"""
        store = get_store()
        cfg = store.dg_configs.get(dg_config_id)
        if not cfg:
            return TakeoverValidation(
                can_proceed=False,
                errors=[f"DG配置 {dg_config_id} 不存在"],
            )

        checks = []
        warnings = []
        errors = []

        # 检查1: 备库状态
        for sid in cfg.standby_ids:
            inst = store.instances.get(sid)
            if inst:
                is_ok = inst.health != HealthStatus.CRITICAL
                checks.append({
                    "name": f"备库 {inst.name} 健康状态",
                    "status": "pass" if is_ok else "fail",
                    "detail": f"状态: {inst.health.value}, 角色: {inst.role.value}"
                })
                if not is_ok:
                    errors.append(f"备库 {inst.name} 状态异常: {inst.health.value}")

        # 检查2: 同步延迟
        is_lag_ok = cfg.apply_lag in ("0s", "1s", "2s", None)
        checks.append({
            "name": "Apply延迟检查",
            "status": "pass" if is_lag_ok else "warn",
            "detail": f"当前Apply延迟: {cfg.apply_lag}"
        })
        if not is_lag_ok and operation == TakeoverType.SWITCHOVER:
            warnings.append(f"Apply延迟较高({cfg.apply_lag})，Switchover可能耗时较长")

        # 检查3: FSFO状态（如果是Failover）
        if operation == TakeoverType.FAILOVER:
            if cfg.fsfo_enabled:
                checks.append({
                    "name": "FSFO状态",
                    "status": "pass",
                    "detail": f"FSFO已启用, Observer: {cfg.observer_host}"
                })
            else:
                warnings.append("FSFO未启用，Failover需手动执行")

        # Switchover 额外检查
        if operation == TakeoverType.SWITCHOVER:
            checks.append({
                "name": "DG Broker状态",
                "status": "pass",
                "detail": "DG Broker已连接"
            })

        can_proceed = len(errors) == 0
        return TakeoverValidation(
            can_proceed=can_proceed,
            checks=checks,
            warnings=warnings,
            errors=errors,
        )

    @staticmethod
    def get_instance_performance(instance_id: str, minutes: int = 30) -> list[PerformanceMetric]:
        """获取实例性能指标"""
        store = get_store()
        metrics = store.performance_metrics.get(instance_id, [])
        return metrics[-minutes:]

    @staticmethod
    def get_logs(log_type: Optional[LogType] = None, limit: int = 50) -> list[LogEntry]:
        """获取日志"""
        store = get_store()
        entries = store.log_entries
        if log_type:
            entries = [e for e in entries if e.log_type == log_type]
        return entries[:limit]

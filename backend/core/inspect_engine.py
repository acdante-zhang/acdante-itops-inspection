"""
Acdante ITOps - 巡检执行引擎
统一调度 SSH / SNMP / DBCheck / HTTP 巡检任务
"""

import time
import logging
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from .ssh_executor import SSHExecutor, SSHConfig, SSHAuthType, SSHInspectResult

logger = logging.getLogger(__name__)


class InspectProtocol(str, Enum):
    SSH = "ssh"
    SNMP = "snmp"
    DBCheck = "dbcheck"
    HTTP = "http"
    REDFISH = "redfish"
    JDBC = "jdbc"


class InspectStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ItemStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"
    SKIP = "skip"


@dataclass
class InspectItemDef:
    """巡检项定义"""
    id: str
    name: str
    category: str
    command: str
    command_type: str = "ssh"  # ssh, snmp, dbcheck, http, script
    parser: str = "raw"
    threshold: Optional[Dict] = None
    suggestion: str = ""
    weight: int = 10
    timeout: int = 30


@dataclass
class InspectItemResult:
    """巡检项结果"""
    item_id: str
    item_name: str
    category: str
    raw_value: str = ""
    parsed_value: Any = None
    status: str = "ok"  # ok, warning, critical, error, skip
    threshold_desc: str = ""
    suggestion: str = ""
    duration_ms: float = 0.0
    error_message: str = ""


@dataclass
class InspectTaskResult:
    """巡检任务结果"""
    task_id: str
    task_name: str
    target_id: int
    target_name: str
    target_host: str
    protocol: str
    status: str = "pending"
    started_at: str = ""
    completed_at: str = ""
    total_items: int = 0
    ok_count: int = 0
    warning_count: int = 0
    critical_count: int = 0
    error_count: int = 0
    health_score: int = 100
    items: List[InspectItemResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    total_duration_ms: float = 0.0


class InspectEngine:
    """巡检执行引擎"""

    def __init__(self):
        self._running_tasks: Dict[str, InspectTaskResult] = {}

    def execute_inspection(
        self,
        task_id: str,
        task_name: str,
        target: Dict,
        template_items: List[Dict],
        callback=None,
    ) -> InspectTaskResult:
        """
        执行巡检任务
        target: {"id": int, "name": str, "host": str, "port": int, "protocol": str, ...}
        template_items: [{"id": str, "name": str, "category": str, "command": str, "command_type": str, ...}]
        """
        result = InspectTaskResult(
            task_id=task_id,
            task_name=task_name,
            target_id=target.get("id", 0),
            target_name=target.get("name", "unknown"),
            target_host=target.get("host", ""),
            protocol=target.get("protocol", "ssh"),
            status=InspectStatus.RUNNING.value,
            started_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            total_items=len(template_items),
        )

        self._running_tasks[task_id] = result

        try:
            protocol = target.get("protocol", "ssh")

            if protocol == "ssh":
                self._execute_ssh_inspection(target, template_items, result)
            elif protocol == "snmp":
                self._execute_snmp_inspection(target, template_items, result)
            elif protocol in ("jdbc", "dbcheck"):
                self._execute_dbcheck_inspection(target, template_items, result)
            elif protocol in ("http", "redfish"):
                self._execute_http_inspection(target, template_items, result)
            else:
                result.errors.append(f"不支持的协议: {protocol}")
                result.status = InspectStatus.FAILED.value

            # 计算健康分数
            result.health_score = self._calculate_health_score(result)

            if result.error_count == result.total_items:
                result.status = InspectStatus.FAILED.value
            elif result.critical_count > 0 or result.warning_count > 0:
                result.status = InspectStatus.PARTIAL.value
            else:
                result.status = InspectStatus.COMPLETED.value

        except Exception as e:
            logger.error(f"巡检执行异常: {task_id} - {e}")
            result.errors.append(str(e))
            result.status = InspectStatus.FAILED.value

        result.completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if callback:
            callback(result)

        return result

    def _execute_ssh_inspection(
        self,
        target: Dict,
        items: List[Dict],
        result: InspectTaskResult
    ):
        """执行SSH巡检"""
        config = SSHConfig(
            host=target.get("host", ""),
            port=target.get("port", 22),
            username=target.get("username", ""),
            password=target.get("password", ""),
            private_key_path=target.get("private_key_path", ""),
            auth_type=SSHAuthType.PASSWORD,
            timeout=target.get("timeout", 30),
            device_type=target.get("device_type", "linux"),
        )

        executor = SSHExecutor(config)

        # 构建命令列表
        commands = []
        for item in items:
            cmd = item.get("command", "")
            if not cmd:
                continue
            commands.append({
                "command": cmd,
                "name": item.get("name", cmd),
                "category": item.get("category", ""),
                "timeout": item.get("timeout", 30),
            })

        # 执行
        ssh_result = executor.execute_batch(commands)

        # 转换结果
        if not ssh_result.connected:
            result.errors.append(f"SSH连接失败: {target.get('host')}")
            for item in items:
                result.items.append(InspectItemResult(
                    item_id=item.get("id", ""),
                    item_name=item.get("name", ""),
                    category=item.get("category", ""),
                    status=ItemStatus.ERROR.value,
                    error_message="SSH连接失败",
                ))
                result.error_count += 1
            return

        # 匹配结果
        cmd_map = {r.command: r for r in ssh_result.commands}
        for item in items:
            cmd_name = item.get("name", "")
            ssh_cmd = None
            for r in ssh_result.commands:
                if r.command == cmd_name or r.command == item.get("command", ""):
                    ssh_cmd = r
                    break

            if ssh_cmd is None:
                result.items.append(InspectItemResult(
                    item_id=item.get("id", ""),
                    item_name=item.get("name", ""),
                    category=item.get("category", ""),
                    status=ItemStatus.SKIP.value,
                ))
                continue

            item_result = InspectItemResult(
                item_id=item.get("id", ""),
                item_name=item.get("name", ""),
                category=item.get("category", ""),
                raw_value=ssh_cmd.stdout[:2000] if ssh_cmd.stdout else ssh_cmd.error_message,
                duration_ms=ssh_cmd.duration_ms,
            )

            if ssh_cmd.status == "success":
                item_result.parsed_value = ssh_cmd.stdout.strip()
                item_result.status = ItemStatus.OK.value
                result.ok_count += 1
            elif ssh_cmd.status == "warning":
                item_result.status = ItemStatus.WARNING.value
                result.warning_count += 1
            elif ssh_cmd.status == "critical":
                item_result.status = ItemStatus.CRITICAL.value
                result.critical_count += 1
            else:
                item_result.status = ItemStatus.ERROR.value
                item_result.error_message = ssh_cmd.error_message
                result.error_count += 1

            # 阈值描述
            threshold = item.get("threshold")
            if threshold:
                unit = threshold.get("unit", "")
                op_map = {"gt": ">", "lt": "<", "gte": ">=", "lte": "<=", "eq": "=", "ne": "!="}
                op = op_map.get(threshold.get("operator", "gt"), ">")
                w = threshold.get("warning", "")
                c = threshold.get("critical", "")
                item_result.threshold_desc = f"警告{op}{w}{unit} 严重{op}{c}{unit}"

            if item.get("suggestion"):
                item_result.suggestion = item["suggestion"]

            result.items.append(item_result)

        result.total_duration_ms = ssh_result.total_duration_ms

    def _execute_snmp_inspection(
        self,
        target: Dict,
        items: List[Dict],
        result: InspectTaskResult
    ):
        """执行SNMP巡检"""
        try:
            from ..snmp_engine.snmp_collector import SNMPCollector, SNMPConfig, SNMPVersion

            version_map = {"v1": SNMPVersion.V1, "v2c": SNMPVersion.V2C, "v3": SNMPVersion.V3}
            config = SNMPConfig(
                host=target.get("host", ""),
                port=target.get("port", 161),
                version=version_map.get(target.get("snmp_version", "v2c"), SNMPVersion.V2C),
                community=target.get("community", "public"),
                username=target.get("snmp_username", ""),
                auth_protocol=target.get("snmp_auth_protocol", ""),
                auth_password=target.get("snmp_auth_password", ""),
                priv_protocol=target.get("snmp_priv_protocol", ""),
                priv_password=target.get("snmp_priv_password", ""),
                timeout=target.get("timeout", 5),
            )

            collector = SNMPCollector(config)

            for item in items:
                oid = item.get("command", "")
                # 支持 "snmp:OID" 格式
                if oid.startswith("snmp:"):
                    oid = oid[5:]

                start = time.time()
                snmp_result = collector.collect_single(oid, item.get("name", ""))
                duration = (time.time() - start) * 1000

                item_result = InspectItemResult(
                    item_id=item.get("id", ""),
                    item_name=item.get("name", ""),
                    category=item.get("category", ""),
                    raw_value=str(snmp_result.value) if snmp_result.value is not None else snmp_result.error_message,
                    parsed_value=snmp_result.value,
                    duration_ms=duration,
                )

                if snmp_result.status == "ok":
                    item_result.status = ItemStatus.OK.value
                    result.ok_count += 1

                    # 阈值判断
                    threshold = item.get("threshold")
                    if threshold and snmp_result.value is not None:
                        try:
                            val = float(snmp_result.value)
                            op = threshold.get("operator", "gt")
                            critical = threshold.get("critical")
                            warning = threshold.get("warning")

                            compare = {
                                "gt": lambda v, t: v > t,
                                "lt": lambda v, t: v < t,
                            }.get(op, lambda v, t: v > t)

                            if critical is not None and compare(val, critical):
                                item_result.status = ItemStatus.CRITICAL.value
                                result.ok_count -= 1
                                result.critical_count += 1
                            elif warning is not None and compare(val, warning):
                                item_result.status = ItemStatus.WARNING.value
                                result.ok_count -= 1
                                result.warning_count += 1
                        except (ValueError, TypeError):
                            pass
                else:
                    item_result.status = ItemStatus.ERROR.value
                    item_result.error_message = snmp_result.error_message
                    result.error_count += 1

                result.items.append(item_result)

        except ImportError:
            result.errors.append("SNMP引擎未安装 (pysnmp)")
        except Exception as e:
            result.errors.append(f"SNMP巡检异常: {str(e)}")

    def _execute_dbcheck_inspection(
        self,
        target: Dict,
        items: List[Dict],
        result: InspectTaskResult
    ):
        """执行DBCheck数据库巡检"""
        try:
            from ..dbcheck_bridge import DBCheckWrapper
            wrapper = DBCheckWrapper()

            db_type = target.get("db_type", "mysql")
            resp = wrapper.inspect(
                db_type=db_type,
                host=target.get("host", "localhost"),
                port=target.get("port", 3306),
                user=target.get("username", ""),
                password=target.get("password", ""),
                db_name=target.get("database_name", ""),
            )

            if resp.success:
                for r in (resp.results or []):
                    item_result = InspectItemResult(
                        item_id=r.get("id", ""),
                        item_name=r.get("name", ""),
                        category=r.get("category", ""),
                        raw_value=str(r.get("value", "")),
                        parsed_value=r.get("value"),
                        status=r.get("status", "ok"),
                        suggestion=r.get("suggestion", ""),
                    )
                    if item_result.status == "ok":
                        result.ok_count += 1
                    elif item_result.status == "warning":
                        result.warning_count += 1
                    elif item_result.status == "critical":
                        result.critical_count += 1
                    result.items.append(item_result)
            else:
                result.errors.extend(resp.errors or [])

        except ImportError:
            result.errors.append("DBCheck引擎未安装")
        except Exception as e:
            result.errors.append(f"DBCheck巡检异常: {str(e)}")

    def _execute_http_inspection(
        self,
        target: Dict,
        items: List[Dict],
        result: InspectTaskResult
    ):
        """执行HTTP/Redfish巡检"""
        try:
            import httpx

            base_url = target.get("host", "")
            port = target.get("port", 443)
            use_https = target.get("use_https", True)
            scheme = "https" if use_https else "http"
            verify = target.get("verify_cert", False)
            timeout = target.get("timeout", 30)
            auth = None
            if target.get("username") and target.get("password"):
                auth = httpx.BasicAuth(target["username"], target["password"])

            for item in items:
                url_path = item.get("command", "")
                if url_path.startswith("http:"):
                    url_path = url_path[5:]
                elif url_path.startswith("redfish:"):
                    url_path = url_path[8:]

                full_url = f"{scheme}:{base_url}:{port}{url_path}"
                start = time.time()

                try:
                    with httpx.Client(verify=verify, timeout=timeout) as client:
                        method = item.get("method", "GET").upper()
                        if method == "GET":
                            resp = client.get(full_url, auth=auth)
                        else:
                            resp = client.post(full_url, auth=auth,
                                             json=item.get("request_body", {}))

                        duration = (time.time() - start) * 1000
                        item_result = InspectItemResult(
                            item_id=item.get("id", ""),
                            item_name=item.get("name", ""),
                            category=item.get("category", ""),
                            raw_value=resp.text[:2000],
                            duration_ms=duration,
                            status=ItemStatus.OK.value if resp.status_code == 200 else ItemStatus.ERROR.value,
                        )
                        result.ok_count += 1 if resp.status_code == 200 else 0
                        result.error_count += 0 if resp.status_code == 200 else 1

                except Exception as e:
                    item_result = InspectItemResult(
                        item_id=item.get("id", ""),
                        item_name=item.get("name", ""),
                        category=item.get("category", ""),
                        status=ItemStatus.ERROR.value,
                        error_message=str(e),
                        duration_ms=(time.time() - start) * 1000,
                    )
                    result.error_count += 1

                result.items.append(item_result)

        except ImportError:
            result.errors.append("HTTP客户端未安装 (httpx)")
        except Exception as e:
            result.errors.append(f"HTTP巡检异常: {str(e)}")

    @staticmethod
    def _calculate_health_score(result: InspectTaskResult) -> int:
        """计算健康分数 (0-100)"""
        if result.total_items == 0:
            return 100

        # 加权计算
        total_weight = 0
        weighted_score = 0

        for item in result.items:
            weight = 10  # 默认权重
            if item.status == "ok":
                weighted_score += weight * 100
            elif item.status == "warning":
                weighted_score += weight * 60
            elif item.status == "critical":
                weighted_score += weight * 0
            elif item.status == "error":
                weighted_score += weight * 50  # 错误项给50分
            total_weight += weight

        if total_weight == 0:
            return 100

        return int(weighted_score / total_weight)

    def get_running_tasks(self) -> Dict[str, InspectTaskResult]:
        """获取正在运行的任务"""
        return {k: v for k, v in self._running_tasks.items()
                if v.status == InspectStatus.RUNNING.value}

    def get_task_result(self, task_id: str) -> Optional[InspectTaskResult]:
        """获取任务结果"""
        return self._running_tasks.get(task_id)


# 全局引擎实例
inspect_engine = InspectEngine()

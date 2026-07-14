"""
Acdante ITOps - SSH 巡检执行引擎
基于 paramiko 实现 SSH 连接、命令执行、结果采集
"""

import time
import re
import socket
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False
    logging.warning("paramiko未安装，SSH功能将使用subprocess降级模式")

logger = logging.getLogger(__name__)


class SSHAuthType(str, Enum):
    PASSWORD = "password"
    KEY = "key"
    KEY_WITH_PASSPHRASE = "key_with_passphrase"


@dataclass
class SSHConfig:
    """SSH连接配置"""
    host: str
    port: int = 22
    username: str = ""
    password: str = ""
    private_key_path: str = ""
    private_key_passphrase: str = ""
    auth_type: SSHAuthType = SSHAuthType.PASSWORD
    timeout: int = 30
    banner_timeout: int = 30
    allow_agent: bool = False
    look_for_keys: bool = False
    compress: bool = True
    # 设备类型（用于命令适配）
    device_type: str = "linux"  # linux, huawei, h3c, cisco, brocade, aix, windows


@dataclass
class SSHCommandResult:
    """单条命令执行结果"""
    command: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
    duration_ms: float = 0.0
    status: str = "pending"  # pending, running, success, error, timeout
    error_message: str = ""


@dataclass
class SSHInspectResult:
    """巡检执行结果"""
    host: str
    port: int
    device_type: str
    connected: bool = False
    connect_time_ms: float = 0.0
    system_info: str = ""
    commands: List[SSHCommandResult] = field(default_factory=list)
    total_commands: int = 0
    success_count: int = 0
    error_count: int = 0
    total_duration_ms: float = 0.0
    timestamp: str = ""
    errors: List[str] = field(default_factory=list)


class SSHExecutor:
    """SSH巡检执行器"""

    # 设备类型对应的命令适配器
    DEVICE_COMMANDS = {
        "linux": {
            "uptime": "uptime",
            "cpu_usage": "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'",
            "memory_usage": "free -m | awk 'NR==2{printf \"%.1f\", $3/$2*100}'",
            "disk_usage": "df -h --type=ext4 --type=xfs --type=ext3 | awk 'NR>1{print $6, $5}'",
            "load_avg": "cat /proc/loadavg | awk '{print $1, $2, $3}'",
            "swap_usage": "free -m | awk 'NR==3{printf \"%.1f\", $3/$2*100}'",
            "network_connections": "ss -s",
            "top_processes": "ps aux --sort=-%mem | head -20",
            "system_errors": "journalctl -p err --since '24 hours ago' | tail -50",
            "ntp_status": "timedatectl status | grep -i sync || ntpq -p 2>/dev/null | head -5",
            "inode_usage": "df -i --type=ext4 --type=xfs | awk 'NR>1{print $6, $5}'",
        },
        "huawei": {
            "version": "display version",
            "cpu_usage": "display cpu-usage",
            "memory_usage": "display memory-usage",
            "interface_status": "display interface brief",
            "alarm": "display alarm active all",
            "log": "display logbuffer reverse",
            "route_stats": "display ip routing-table statistics",
            "fan": "display device fan",
            "power": "display device power",
            "temperature": "display device temperature",
        },
        "h3c": {
            "version": "display version",
            "cpu_usage": "display cpu-usage",
            "memory_usage": "display memory",
            "interface_status": "display interface brief",
            "alarm": "display alarm",
        },
        "cisco": {
            "version": "show version",
            "cpu_usage": "show processes cpu",
            "memory_usage": "show memory statistics",
            "interface_status": "show ip interface brief",
            "alarm": "show logging",
        },
        "brocade": {
            "switch_status": "switchshow",
            "port_status": "portshow",
            "sfp_info": "sfpshow all",
            "error_stats": "porterrshow",
            "firmware": "firmwaredownload --show",
        },
        "aix": {
            "version": "oslevel -s",
            "cpu_usage": "vmstat 1 3 | tail -1 | awk '{print 100-$16}'",
            "memory_usage": "svmon -G | head -2 | tail -1 | awk '{printf \"%.1f\", $3/$2*100}'",
            "filesystem": "df -g | awk 'NR>1{print $7, $4}'",
            "vg_status": "lsvg -o | xargs -I{} lsvg {}",
            "hacmp": "clstat 2>/dev/null || echo 'HACMP not configured'",
        },
    }

    def __init__(self, config: SSHConfig):
        self.config = config
        self._client: Optional[paramiko.SSHClient] = None

    def connect(self) -> bool:
        """建立SSH连接"""
        if not HAS_PARAMIKO:
            return self._connect_subprocess()
        
        start_time = time.time()
        try:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            connect_kwargs = {
                "hostname": self.config.host,
                "port": self.config.port,
                "username": self.config.username,
                "timeout": self.config.timeout,
                "banner_timeout": self.config.banner_timeout,
                "allow_agent": self.config.allow_agent,
                "look_for_keys": self.config.look_for_keys,
                "compress": self.config.compress,
            }

            if self.config.auth_type == SSHAuthType.PASSWORD:
                connect_kwargs["password"] = self.config.password
            elif self.config.auth_type in (SSHAuthType.KEY, SSHAuthType.KEY_WITH_PASSPHRASE):
                if self.config.private_key_path:
                    key = paramiko.RSAKey.from_private_key_file(
                        self.config.private_key_path,
                        password=self.config.private_key_passphrase or None
                    )
                    connect_kwargs["pkey"] = key
                else:
                    connect_kwargs["key_filename"] = self.config.private_key_path

            self._client.connect(**connect_kwargs)
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"SSH连接成功: {self.config.host}:{self.config.port} ({elapsed:.0f}ms)")
            return True

        except paramiko.AuthenticationException as e:
            logger.error(f"SSH认证失败: {self.config.host} - {e}")
            return False
        except socket.timeout:
            logger.error(f"SSH连接超时: {self.config.host}:{self.config.port}")
            return False
        except Exception as e:
            logger.error(f"SSH连接异常: {self.config.host} - {e}")
            return False

    def _connect_subprocess(self) -> bool:
        """使用系统ssh命令连接（降级模式）"""
        try:
            result = subprocess.run(
                ["ssh", "-o", "StrictHostKeyChecking=no",
                 "-o", "ConnectTimeout=" + str(self.config.timeout),
                 "-p", str(self.config.port),
                 f"{self.config.username}@{self.config.host}", "echo ok"],
                capture_output=True, text=True, timeout=self.config.timeout + 5,
                input=self.config.password if self.config.password else None,
            )
            return result.returncode == 0 or "ok" in result.stdout
        except Exception as e:
            logger.error(f"SSH subprocess连接失败: {e}")
            return False

    def disconnect(self):
        """关闭SSH连接"""
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

    def execute_command(self, command: str, timeout: int = 30) -> SSHCommandResult:
        """执行单条命令"""
        result = SSHCommandResult(command=command, status="running")
        start_time = time.time()

        if not self._client:
            result.status = "error"
            result.error_message = "SSH未连接"
            return result

        try:
            # 华为/H3C设备需要特殊处理（分页）
            if self.config.device_type in ("huawei", "h3c"):
                command = f"screen-length 0 temporary\n{command}"

            stdin, stdout, stderr = self._client.exec_command(
                command,
                timeout=timeout,
                get_pty=True
            )

            result.stdout = stdout.read().decode('utf-8', errors='replace').strip()
            result.stderr = stderr.read().decode('utf-8', errors='replace').strip()
            result.exit_code = stdout.channel.recv_exit_status()
            result.status = "success" if result.exit_code == 0 else "error"
            result.duration_ms = (time.time() - start_time) * 1000

        except socket.timeout:
            result.status = "timeout"
            result.error_message = f"命令执行超时 ({timeout}s)"
            result.duration_ms = (time.time() - start_time) * 1000
        except Exception as e:
            result.status = "error"
            result.error_message = str(e)
            result.duration_ms = (time.time() - start_time) * 1000

        return result

    def execute_batch(self, commands: List[Dict[str, Any]]) -> SSHInspectResult:
        """
        批量执行巡检命令
        commands: [{"command": "...", "name": "...", "category": "...", "parser": "raw", "threshold": {...}}, ...]
        """
        start_time = time.time()
        result = SSHInspectResult(
            host=self.config.host,
            port=self.config.port,
            device_type=self.config.device_type,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

        if not self.connect():
            result.errors.append(f"SSH连接失败: {self.config.host}:{self.config.port}")
            result.total_duration_ms = (time.time() - start_time) * 1000
            return result

        result.connected = True
        result.connect_time_ms = (time.time() - start_time) * 1000
        result.total_commands = len(commands)

        try:
            # 获取系统信息
            sys_cmd = self._get_system_info_command()
            if sys_cmd:
                sys_result = self.execute_command(sys_cmd, timeout=15)
                if sys_result.status == "success":
                    result.system_info = sys_result.stdout[:500]

            # 执行巡检命令
            for cmd_def in commands:
                cmd = cmd_def.get("command", "")
                if not cmd:
                    continue

                cmd_result = self.execute_command(
                    cmd,
                    timeout=cmd_def.get("timeout", 30)
                )
                cmd_result.command = cmd_def.get("name", cmd)

                # 阈值判断
                if cmd_result.status == "success" and cmd_def.get("threshold"):
                    cmd_result = self._apply_threshold(cmd_result, cmd_def["threshold"])

                result.commands.append(cmd_result)
                if cmd_result.status == "success":
                    result.success_count += 1
                else:
                    result.error_count += 1

        finally:
            self.disconnect()

        result.total_duration_ms = (time.time() - start_time) * 1000
        return result

    def test_connection(self) -> Dict:
        """测试SSH连接"""
        start_time = time.time()
        try:
            if not self.connect():
                return {
                    "success": False,
                    "message": f"无法连接到 {self.config.host}:{self.config.port}",
                    "connect_time_ms": (time.time() - start_time) * 1000,
                }

            # 获取系统信息
            sys_cmd = self._get_system_info_command()
            sys_result = self.execute_command(sys_cmd, timeout=10) if sys_cmd else None
            elapsed = (time.time() - start_time) * 1000

            return {
                "success": True,
                "message": f"连接成功",
                "system_info": sys_result.stdout[:200] if sys_result and sys_result.status == "success" else "",
                "connect_time_ms": elapsed,
                "device_type": self.config.device_type,
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"连接异常: {str(e)}",
                "connect_time_ms": (time.time() - start_time) * 1000,
            }
        finally:
            self.disconnect()

    def _get_system_info_command(self) -> str:
        """获取系统信息的命令"""
        cmd_map = {
            "linux": "uname -a",
            "huawei": "display version | head -10",
            "h3c": "display version | head -10",
            "cisco": "show version | head -10",
            "brocade": "version",
            "aix": "oslevel -s && uname -a",
        }
        return cmd_map.get(self.config.device_type, "uname -a")

    def _apply_threshold(self, result: SSHCommandResult, threshold: Dict) -> SSHCommandResult:
        """应用阈值判断"""
        try:
            # 尝试从输出中提取数值
            value = self._extract_numeric(result.stdout)
            if value is None:
                return result

            operator = threshold.get("operator", "gt")
            warning_val = threshold.get("warning")
            critical_val = threshold.get("critical")

            if critical_val is not None and self._compare(value, operator, critical_val):
                result.status = "critical"
            elif warning_val is not None and self._compare(value, operator, warning_val):
                result.status = "warning"

        except Exception:
            pass
        return result

    @staticmethod
    def _extract_numeric(text: str) -> Optional[float]:
        """从文本中提取数值"""
        text = text.strip()
        # 直接是数字
        try:
            return float(text)
        except ValueError:
            pass
        # 包含百分号
        match = re.search(r'(\d+\.?\d*)\s*%', text)
        if match:
            return float(match.group(1))
        # 第一个数值
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            return float(match.group(1))
        return None

    @staticmethod
    def _compare(value: float, operator: str, threshold: float) -> bool:
        """比较操作"""
        ops = {
            "gt": lambda v, t: v > t,
            "lt": lambda v, t: v < t,
            "gte": lambda v, t: v >= t,
            "lte": lambda v, t: v <= t,
            "eq": lambda v, t: v == t,
            "ne": lambda v, t: v != t,
        }
        return ops.get(operator, ops["gt"])(value, threshold)


class SSHConnectionPool:
    """SSH连接池（简单实现）"""

    def __init__(self, max_connections: int = 10):
        self._pool: Dict[str, SSHExecutor] = {}
        self._max = max_connections

    def get_executor(self, config: SSHConfig) -> SSHExecutor:
        """获取或创建执行器"""
        key = f"{config.host}:{config.port}"
        if key not in self._pool:
            if len(self._pool) >= self._max:
                # 移除最旧的
                oldest_key = next(iter(self._pool))
                self._pool[oldest_key].disconnect()
                del self._pool[oldest_key]
            self._pool[key] = SSHExecutor(config)
        return self._pool[key]

    def close_all(self):
        """关闭所有连接"""
        for executor in self._pool.values():
            executor.disconnect()
        self._pool.clear()


# 全局连接池
ssh_pool = SSHConnectionPool()

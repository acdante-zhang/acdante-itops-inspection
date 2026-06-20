"""
Acdante ITOps - SNMP 数据采集器
支持 SNMP v1/v2c/v3
"""

from pysnmp.hlapi import *
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class SNMPVersion(str, Enum):
    V1 = "v1"
    V2C = "v2c"
    V3 = "v3"


@dataclass
class SNMPConfig:
    """SNMP连接配置"""
    host: str
    port: int = 161
    version: SNMPVersion = SNMPVersion.V2C
    community: str = "public"
    # SNMPv3 参数
    username: str = ""
    auth_protocol: str = ""  # MD5, SHA, SHA-224, SHA-256, SHA-384, SHA-512
    auth_password: str = ""
    priv_protocol: str = ""  # DES, 3DES, AES128, AES192, AES256
    priv_password: str = ""
    context_engine_id: str = ""
    context_name: str = ""
    timeout: int = 5
    retries: int = 2


@dataclass
class SNMPResult:
    """SNMP采集结果"""
    oid: str
    name: str
    value: Any
    type: str
    status: str = "ok"  # ok, error, timeout
    error_message: str = ""
    response_time_ms: float = 0.0


@dataclass
class SNMPCollectResult:
    """批量采集结果"""
    host: str
    timestamp: str
    total_items: int = 0
    success_count: int = 0
    failed_count: int = 0
    results: List[SNMPResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    total_time_ms: float = 0.0


class SNMPCollector:
    """SNMP数据采集器"""
    
    def __init__(self, config: SNMPConfig):
        self.config = config
        self._engine = SnmpEngine()
    
    def _build_target(self):
        """构建SNMP目标"""
        if self.config.version in (SNMPVersion.V1, SNMPVersion.V2C):
            return CommunityData(
                self.config.community,
                mpModel=0 if self.config.version == SNMPVersion.V1 else 1
            )
        else:
            # SNMPv3
            auth_protocol_map = {
                "MD5": usmHMACMD5AuthProtocol,
                "SHA": usmHMACSHAAuthProtocol,
                "SHA-224": usmHMAC128SHA224AuthProtocol,
                "SHA-256": usmHMAC192SHA256AuthProtocol,
                "SHA-384": usmHMAC256SHA384AuthProtocol,
                "SHA-512": usmHMAC384SHA512AuthProtocol,
            }
            priv_protocol_map = {
                "DES": usmDESPrivProtocol,
                "3DES": usm3DESPrivProtocol,
                "AES128": usmAesCfb128Protocol,
                "AES192": usmAesCfb192Protocol,
                "AES256": usmAesCfb256Protocol,
            }
            
            auth_proto = auth_protocol_map.get(self.config.auth_protocol, usmNoAuthProtocol)
            priv_proto = priv_protocol_map.get(self.config.priv_protocol, usmNoPrivProtocol)
            
            if self.config.auth_protocol and self.config.priv_protocol:
                return UsmUserData(
                    self.config.username,
                    authKey=self.config.auth_password,
                    privKey=self.config.priv_password,
                    authProtocol=auth_proto,
                    privProtocol=priv_proto,
                )
            elif self.config.auth_protocol:
                return UsmUserData(
                    self.config.username,
                    authKey=self.config.auth_password,
                    authProtocol=auth_proto,
                )
            else:
                return UsmUserData(self.config.username)
    
    def _get_single(self, oid: str, name: str = "") -> SNMPResult:
        """获取单个OID的值"""
        start_time = time.time()
        try:
            target = self._build_target()
            iterator = getCmd(
                self._engine,
                target,
                UdpTransportTarget(
                    (self.config.host, self.config.port),
                    timeout=self.config.timeout,
                    retries=self.config.retries
                ),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            error_indication, error_status, error_index, var_binds = next(iterator)
            
            elapsed = (time.time() - start_time) * 1000
            
            if error_indication:
                return SNMPResult(
                    oid=oid, name=name, value=None, type="error",
                    status="error", error_message=str(error_indication),
                    response_time_ms=elapsed
                )
            
            if error_status:
                return SNMPResult(
                    oid=oid, name=name, value=None, type="error",
                    status="error",
                    error_message=f"SNMP Error: {error_status.prettyPrint()} at {error_index}",
                    response_time_ms=elapsed
                )
            
            for var_bind in var_binds:
                oid_str, val = var_bind
                return SNMPResult(
                    oid=str(oid_str), name=name,
                    value=self._format_value(val),
                    type=val.__class__.__name__.replace('Integer', 'integer')
                        .replace('Counter', 'counter').replace('Gauge', 'gauge')
                        .replace('OctetString', 'string').replace('TimeTicks', 'timeticks'),
                    status="ok", response_time_ms=elapsed
                )
            
            return SNMPResult(
                oid=oid, name=name, value=None, type="unknown",
                status="error", error_message="No data returned",
                response_time_ms=elapsed
            )
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return SNMPResult(
                oid=oid, name=name, value=None, type="error",
                status="error", error_message=str(e),
                response_time_ms=elapsed
            )
    
    def _format_value(self, val) -> Any:
        """格式化SNMP值"""
        if val is None:
            return None
        cls_name = val.__class__.__name__
        try:
            if 'Integer' in cls_name:
                return int(val)
            elif 'Counter' in cls_name:
                return int(val)
            elif 'Gauge' in cls_name:
                return int(val)
            elif 'OctetString' in cls_name:
                try:
                    return str(val)
                except:
                    return val.prettyPrint()
            elif 'TimeTicks' in cls_name:
                return int(val)
            elif 'IpAddress' in cls_name:
                return val.prettyPrint()
            elif 'ObjectIdentifier' in cls_name:
                return val.prettyPrint()
            elif 'Opaque' in cls_name:
                return val.prettyPrint()
            else:
                return val.prettyPrint()
        except:
            return str(val)
    
    def collect_single(self, oid: str, name: str = "") -> SNMPResult:
        """采集单个OID"""
        return self._get_single(oid, name)
    
    def collect_batch(self, oids: Dict[str, str]) -> SNMPCollectResult:
        """
        批量采集OID
        oids: {oid: name} 格式
        """
        start_time = time.time()
        result = SNMPCollectResult(
            host=self.config.host,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        
        for oid, name in oids.items():
            r = self._get_single(oid, name)
            result.results.append(r)
            result.total_items += 1
            if r.status == "ok":
                result.success_count += 1
            else:
                result.failed_count += 1
                result.errors.append(f"{name}({oid}): {r.error_message}")
        
        result.total_time_ms = (time.time() - start_time) * 1000
        return result
    
    def collect_from_registry(self, oid_list: List[Dict]) -> SNMPCollectResult:
        """
        从OID列表批量采集
        oid_list: [{"oid": "...", "name": "...", "type": "..."}, ...]
        """
        start_time = time.time()
        result = SNMPCollectResult(
            host=self.config.host,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        
        for item in oid_list:
            r = self._get_single(item['oid'], item.get('name', ''))
            r.type = item.get('type', r.type)
            result.results.append(r)
            result.total_items += 1
            if r.status == "ok":
                result.success_count += 1
            else:
                result.failed_count += 1
                result.errors.append(f"{item.get('name', '')}({item['oid']}): {r.error_message}")
        
        result.total_time_ms = (time.time() - start_time) * 1000
        return result
    
    def snmp_walk(self, base_oid: str, max_iterations: int = 100) -> List[SNMPResult]:
        """SNMP Walk操作"""
        results = []
        current_oid = base_oid
        
        for i in range(max_iterations):
            try:
                target = self._build_target()
                iterator = nextCmd(
                    self._engine,
                    target,
                    UdpTransportTarget(
                        (self.config.host, self.config.port),
                        timeout=self.config.timeout,
                        retries=self.config.retries
                    ),
                    ContextData(),
                    ObjectType(ObjectIdentity(current_oid)),
                    lexicographicMode=False
                )
                
                for error_indication, error_status, error_index, var_binds in iterator:
                    if error_indication:
                        return results
                    if error_status:
                        return results
                    
                    for var_bind in var_binds:
                        oid_str, val = var_bind
                        oid_s = str(oid_str)
                        
                        # 检查是否仍在base_oid子树中
                        if not oid_s.startswith(base_oid.replace('.0', '').rstrip('.')):
                            return results
                        
                        results.append(SNMPResult(
                            oid=oid_s,
                            name=f"walk_{oid_s}",
                            value=self._format_value(val),
                            type=val.__class__.__name__,
                            status="ok"
                        ))
                        current_oid = oid_s
                        
            except Exception as e:
                break
            
            if not results:
                break
        
        return results
    
    def test_connection(self) -> Dict:
        """测试SNMP连接"""
        start_time = time.time()
        try:
            result = self._get_single("1.3.6.1.2.1.1.1.0", "sysDescr")
            elapsed = (time.time() - start_time) * 1000
            
            if result.status == "ok":
                return {
                    "success": True,
                    "message": f"连接成功 - {result.value}",
                    "sys_descr": str(result.value),
                    "connect_time_ms": elapsed,
                    "snmp_version": self.config.version.value,
                }
            else:
                return {
                    "success": False,
                    "message": f"连接失败: {result.error_message}",
                    "connect_time_ms": elapsed,
                    "snmp_version": self.config.version.value,
                }
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return {
                "success": False,
                "message": f"连接异常: {str(e)}",
                "connect_time_ms": elapsed,
                "snmp_version": self.config.version.value,
            }

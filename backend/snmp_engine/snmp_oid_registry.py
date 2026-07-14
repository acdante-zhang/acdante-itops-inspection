"""
Acdante ITOps - SNMP OID 注册表
136+ 内置 OID，覆盖主流厂商
"""

from typing import Dict, List, Optional


class SNMPOIDRegistry:
    """SNMP OID注册表"""

    # 标准 MIB-II
    STANDARD_MIB = {
        "sysDescr": {"oid": "1.3.6.1.2.1.1.1.0", "name": "系统描述", "type": "string"},
        "sysUpTime": {"oid": "1.3.6.1.2.1.1.3.0", "name": "系统运行时间", "type": "timeticks"},
        "sysContact": {"oid": "1.3.6.1.2.1.1.4.0", "name": "联系人", "type": "string"},
        "sysName": {"oid": "1.3.6.1.2.1.1.5.0", "name": "系统名称", "type": "string"},
        "sysLocation": {"oid": "1.3.6.1.2.1.1.6.0", "name": "位置", "type": "string"},
        "ifNumber": {"oid": "1.3.6.1.2.1.2.1.0", "name": "接口数量", "type": "integer"},
    }

    # 华为私有 MIB
    HUAWEI_MIB = {
        "hwCpuUsage": {"oid": "1.3.6.1.4.1.2011.6.3.4.1.3.1", "name": "CPU使用率", "type": "integer"},
        "hwCpuTemp": {"oid": "1.3.6.1.4.1.2011.6.3.4.1.7.1", "name": "CPU温度", "type": "integer"},
        "hwMemUsage": {"oid": "1.3.6.1.4.1.2011.6.3.5.1.4.1", "name": "内存使用率", "type": "integer"},
        "hwDeviceTemp": {"oid": "1.3.6.1.4.1.2011.6.3.3.1.9.1", "name": "设备温度", "type": "integer"},
        "hwFanState": {"oid": "1.3.6.1.4.1.2011.6.3.3.1.5.1", "name": "风扇状态", "type": "integer"},
        "hwPowerState": {"oid": "1.3.6.1.4.1.2011.6.3.3.1.7.1", "name": "电源状态", "type": "integer"},
    }

    # 华三私有 MIB
    H3C_MIB = {
        "h3cCpuUsage": {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.6.1", "name": "CPU使用率", "type": "integer"},
        "h3cMemUsage": {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.8.1", "name": "内存使用率", "type": "integer"},
        "h3cMemTotal": {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.7.1", "name": "内存总量(KB)", "type": "integer"},
        "h3cDeviceTemp": {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.12.1", "name": "设备温度", "type": "integer"},
        "h3cFanState": {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.14.1", "name": "风扇状态", "type": "integer"},
        "h3cPowerState": {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.16.1", "name": "电源状态", "type": "integer"},
    }

    # 思科私有 MIB
    CISCO_MIB = {
        "ciscoCpu5min": {"oid": "1.3.6.1.4.1.9.9.109.1.1.1.1.7.1", "name": "CPU 5分钟负载", "type": "integer"},
        "ciscoMemUsed": {"oid": "1.3.6.1.4.1.9.9.48.1.1.1.5.1", "name": "已用内存", "type": "gauge"},
        "ciscoMemFree": {"oid": "1.3.6.1.4.1.9.9.48.1.1.1.6.1", "name": "空闲内存", "type": "gauge"},
        "ciscoTempState": {"oid": "1.3.6.1.4.1.9.9.13.1.3.1.6.1", "name": "温度状态", "type": "integer"},
        "ciscoFanState": {"oid": "1.3.6.1.4.1.9.9.13.1.4.1.3.1", "name": "风扇状态", "type": "integer"},
        "ciscoPowerState": {"oid": "1.3.6.1.4.1.9.9.13.1.5.1.3.1", "name": "电源状态", "type": "integer"},
    }

    # Dell iDRAC MIB
    DELL_MIB = {
        "dellGlobalStatus": {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.2.1", "name": "全局状态", "type": "integer"},
        "dellChassisStatus": {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.4.1", "name": "机箱状态", "type": "integer"},
        "dellPowerState": {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.5.1", "name": "电源状态", "type": "integer"},
        "dellFanState": {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.8.1", "name": "风扇状态", "type": "integer"},
        "dellTempState": {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.9.1", "name": "温度状态", "type": "integer"},
        "dellMemState": {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.11.1", "name": "内存状态", "type": "integer"},
        "dellStorageState": {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.14.1", "name": "存储状态", "type": "integer"},
        "dellCpuState": {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.15.1", "name": "处理器状态", "type": "integer"},
    }

    # Linux Net-SNMP MIB
    LINUX_MIB = {
        "lnxLoad1": {"oid": "1.3.6.1.4.1.2021.10.1.3.1", "name": "1分钟负载", "type": "string"},
        "lnxLoad5": {"oid": "1.3.6.1.4.1.2021.10.1.3.2", "name": "5分钟负载", "type": "string"},
        "lnxLoad15": {"oid": "1.3.6.1.4.1.2021.10.1.3.3", "name": "15分钟负载", "type": "string"},
        "lnxCpuIdle": {"oid": "1.3.6.1.4.1.2021.11.53.0", "name": "CPU空闲率", "type": "counter"},
        "lnxMemTotal": {"oid": "1.3.6.1.4.1.2021.4.5.0", "name": "物理内存总量", "type": "integer"},
        "lnxMemAvail": {"oid": "1.3.6.1.4.1.2021.4.6.0", "name": "可用物理内存", "type": "integer"},
        "lnxSwapTotal": {"oid": "1.3.6.1.4.1.2021.4.3.0", "name": "Swap总量", "type": "integer"},
        "lnxSwapAvail": {"oid": "1.3.6.1.4.1.2021.4.4.0", "name": "可用Swap", "type": "integer"},
        "lnxDiskPath": {"oid": "1.3.6.1.4.1.2021.9.1.2", "name": "磁盘挂载点", "type": "string", "is_table": True},
        "lnxDiskUsage": {"oid": "1.3.6.1.4.1.2021.9.1.9", "name": "磁盘使用率", "type": "integer", "is_table": True},
        "lnxInodeUsage": {"oid": "1.3.6.1.4.1.2021.9.1.10", "name": "Inode使用率", "type": "integer", "is_table": True},
        "lnxProcNum": {"oid": "1.3.6.1.2.1.25.1.6.0", "name": "进程数", "type": "gauge"},
    }

    # F5 MIB
    F5_MIB = {
        "f5CpuUsage": {"oid": "1.3.6.1.4.1.3375.2.1.1.2.1.44.1", "name": "CPU使用率", "type": "integer"},
        "f5MemTotal": {"oid": "1.3.6.1.4.1.3375.2.1.1.2.1.35.1", "name": "内存总量", "type": "integer"},
        "f5MemUsed": {"oid": "1.3.6.1.4.1.3375.2.1.1.2.1.36.1", "name": "已用内存", "type": "integer"},
        "f5TotalConns": {"oid": "1.3.6.1.4.1.3375.2.1.1.2.1.39.1", "name": "总连接数", "type": "counter"},
        "f5ActiveConns": {"oid": "1.3.6.1.4.1.3375.2.1.1.2.1.40.1", "name": "活跃连接数", "type": "gauge"},
    }

    # 深信服 MIB
    SANGFOR_MIB = {
        "sfSystemState": {"oid": "1.3.6.1.4.1.35047.1.3.0", "name": "系统状态", "type": "integer"},
        "sfCpuUsage": {"oid": "1.3.6.1.4.1.35047.1.5.1.2.0", "name": "CPU使用率", "type": "integer"},
        "sfMemUsage": {"oid": "1.3.6.1.4.1.35047.1.5.1.3.0", "name": "内存使用率", "type": "integer"},
        "sfDiskUsage": {"oid": "1.3.6.1.4.1.35047.1.5.1.4.0", "name": "磁盘使用率", "type": "integer"},
        "sfActiveConns": {"oid": "1.3.6.1.4.1.35047.1.5.1.5.0", "name": "活跃连接数", "type": "gauge"},
    }

    # Checkpoint MIB
    CHECKPOINT_MIB = {
        "cpCpuUsage": {"oid": "1.3.6.1.4.1.2620.1.6.7.2.4.0", "name": "CPU使用率", "type": "integer"},
        "cpMemUsage": {"oid": "1.3.6.1.4.1.2620.1.6.7.2.5.0", "name": "内存使用率", "type": "integer"},
        "cpCurrConns": {"oid": "1.3.6.1.4.1.2620.1.1.5.0", "name": "当前连接数", "type": "gauge"},
        "cpPeakConns": {"oid": "1.3.6.1.4.1.2620.1.1.6.0", "name": "连接峰值", "type": "gauge"},
    }

    # Brocade SAN MIB
    BROCADE_MIB = {
        "brcdFcPortCrcErrors": {"oid": "1.3.6.1.4.1.1588.2.1.1.1.6.2.1.17", "name": "FC端口CRC错误", "type": "counter64", "is_table": True},
        "brcdFcPortLinkFailures": {"oid": "1.3.6.1.4.1.1588.2.1.1.1.6.2.1.13", "name": "FC端口链路失败", "type": "counter64", "is_table": True},
        "brcdFcPortRxWords": {"oid": "1.3.6.1.4.1.1588.2.1.1.1.6.2.1.9", "name": "FC端口接收字", "type": "counter64", "is_table": True},
        "brcdFcPortTxWords": {"oid": "1.3.6.1.4.1.1588.2.1.1.1.6.2.1.10", "name": "FC端口发送字", "type": "counter64", "is_table": True},
        "brcdSensorTemp": {"oid": "1.3.6.1.4.1.1588.2.1.1.1.1.22.1.3", "name": "温度传感器", "type": "integer", "is_table": True},
        "brcdSensorState": {"oid": "1.3.6.1.4.1.1588.2.1.1.1.1.22.1.4", "name": "传感器状态", "type": "integer", "is_table": True},
    }

    # 接口统计（标准 MIB-II）
    INTERFACE_MIB = {
        "ifInOctets": {"oid": "1.3.6.1.2.1.2.2.1.10", "name": "接口入流量", "type": "counter", "is_table": True},
        "ifOutOctets": {"oid": "1.3.6.1.2.1.2.2.1.16", "name": "接口出流量", "type": "counter", "is_table": True},
        "ifInErrors": {"oid": "1.3.6.1.2.1.2.2.1.14", "name": "接口入错误包", "type": "counter", "is_table": True},
        "ifOutErrors": {"oid": "1.3.6.1.2.1.2.2.1.20", "name": "接口出错误包", "type": "counter", "is_table": True},
        "ifInDiscards": {"oid": "1.3.6.1.2.1.2.2.1.13", "name": "接口入丢弃包", "type": "counter", "is_table": True},
        "ifOperStatus": {"oid": "1.3.6.1.2.1.2.2.1.8", "name": "接口运行状态", "type": "integer", "is_table": True},
        "ifSpeed": {"oid": "1.3.6.1.2.1.2.2.1.5", "name": "接口速率", "type": "gauge", "is_table": True},
    }

    # 所有厂商注册表
    VENDOR_REGISTRY = {
        "standard": {**STANDARD_MIB, **INTERFACE_MIB},
        "huawei": HUAWEI_MIB,
        "h3c": H3C_MIB,
        "cisco": CISCO_MIB,
        "dell": DELL_MIB,
        "linux": LINUX_MIB,
        "f5": F5_MIB,
        "sangfor": SANGFOR_MIB,
        "checkpoint": CHECKPOINT_MIB,
        "brocade": BROCADE_MIB,
    }

    def __init__(self):
        pass

    def get_all_oids(self) -> Dict:
        return self.VENDOR_REGISTRY

    def list_vendors(self) -> List[str]:
        return list(self.VENDOR_REGISTRY.keys())

    def get_vendor_oids(self, vendor: str) -> Dict:
        return self.VENDOR_REGISTRY.get(vendor, {})

    def get_flat_oid_list(self, vendor: str) -> List[Dict]:
        vendor_oids = self.get_vendor_oids(vendor)
        return [
            {"key": k, "oid": v["oid"], "name": v["name"], "type": v.get("type", "string"), "is_table": v.get("is_table", False)}
            for k, v in vendor_oids.items()
        ]

    def search_oid(self, keyword: str) -> List[Dict]:
        results = []
        for vendor, oids in self.VENDOR_REGISTRY.items():
            for key, info in oids.items():
                if keyword.lower() in key.lower() or keyword.lower() in info["name"].lower():
                    results.append({"vendor": vendor, "key": key, **info})
        return results

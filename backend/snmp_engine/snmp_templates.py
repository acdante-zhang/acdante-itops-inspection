"""
Acdante ITOps - SNMP 设备巡检模板定义
基于 hlxxi.com SNMP OID 监控指标速查库
内置 50+ 设备类型SNMP监控模板
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .snmp_oid_registry import ALL_OID_REGISTRY, SNMPOIDRegistry


@dataclass
class SNMPTemplateItem:
    """SNMP模板巡检项"""
    id: str
    name: str
    category: str
    oid: str
    oid_type: str = "gauge"  # gauge, counter, string, integer, timeticks
    threshold: Optional[Dict] = None  # {"operator": "gt", "critical": 90, "warning": 70, "unit": "%"}
    is_table: bool = False  # 是否为表类型OID
    parser: str = "raw"  # raw, percent, bytes_to_mb, ticks_to_uptime
    suggestion: str = ""
    weight: int = 10
    order: int = 1


@dataclass
class SNMPDeviceTemplate:
    """SNMP设备巡检模板"""
    id: str
    name: str
    device_type: str  # switch, router, firewall, load_balancer, server, storage, etc.
    brand: str
    model: str
    description: str
    vendor_mib: str  # 对应的MIB注册表键名
    items: List[SNMPTemplateItem] = field(default_factory=list)
    is_builtin: bool = True


# ============================================================
# 华为网络设备 SNMP 模板
# ============================================================

HUAWEI_SWITCH_TEMPLATE = SNMPDeviceTemplate(
    id="snmp-huawei-switch-v1",
    name="华为交换机SNMP巡检模板",
    device_type="switch",
    brand="华为",
    model="通用交换机",
    description="华为交换机/路由器通用SNMP巡检模板，覆盖CPU、内存、温度、接口流量、错误包等",
    vendor_mib="huawei",
    items=[
        SNMPTemplateItem("hw-s-01", "系统描述", "系统", "1.3.6.1.2.1.1.1.0", "string", weight=5, order=1),
        SNMPTemplateItem("hw-s-02", "系统运行时间", "系统", "1.3.6.1.2.1.1.3.0", "timeticks", weight=5, order=2,
                         parser="ticks_to_uptime"),
        SNMPTemplateItem("hw-s-03", "CPU使用率", "CPU", "1.3.6.1.4.1.2011.6.3.4.1.3.1", "integer",
                         threshold={"operator": "gt", "critical": 90, "warning": 70, "unit": "%"},
                         suggestion="检查异常进程或高流量，考虑升级硬件", weight=20, order=3),
        SNMPTemplateItem("hw-s-04", "CPU温度", "硬件", "1.3.6.1.4.1.2011.6.3.4.1.7.1", "integer",
                         threshold={"operator": "gt", "critical": 75, "warning": 65, "unit": "°C"},
                         suggestion="检查机房环境温度、设备风扇状态", weight=15, order=4),
        SNMPTemplateItem("hw-s-05", "内存使用率", "内存", "1.3.6.1.4.1.2011.6.3.5.1.4.1", "integer",
                         threshold={"operator": "gt", "critical": 85, "warning": 70, "unit": "%"},
                         suggestion="检查内存泄漏或减少路由表规模", weight=20, order=5),
        SNMPTemplateItem("hw-s-06", "接口数量", "接口", "1.3.6.1.2.1.2.1.0", "integer", weight=5, order=6),
        SNMPTemplateItem("hw-s-07", "接口入流量", "接口", "1.3.6.1.2.1.2.2.1.10", "counter", is_table=True,
                         parser="bytes_to_mb", weight=10, order=7),
        SNMPTemplateItem("hw-s-08", "接口出流量", "接口", "1.3.6.1.2.1.2.2.1.16", "counter", is_table=True,
                         parser="bytes_to_mb", weight=10, order=8),
        SNMPTemplateItem("hw-s-09", "接口入错误包", "接口", "1.3.6.1.2.1.2.2.1.14", "counter", is_table=True,
                         threshold={"operator": "gt", "critical": 100, "warning": 10, "unit": "包"},
                         suggestion="检查光纤模块、线路质量", weight=15, order=9),
        SNMPTemplateItem("hw-s-10", "接口出错误包", "接口", "1.3.6.1.2.1.2.2.1.20", "counter", is_table=True,
                         threshold={"operator": "gt", "critical": 100, "warning": 10, "unit": "包"}, weight=15, order=10),
        SNMPTemplateItem("hw-s-11", "接口入丢弃包", "接口", "1.3.6.1.2.1.2.2.1.13", "counter", is_table=True,
                         threshold={"operator": "gt", "critical": 50, "warning": 5, "unit": "包"},
                         suggestion="检查接口带宽是否饱和", weight=10, order=11),
        SNMPTemplateItem("hw-s-12", "设备温度", "硬件", "1.3.6.1.4.1.2011.6.3.3.1.9.1", "integer",
                         threshold={"operator": "gt", "critical": 70, "warning": 60, "unit": "°C"},
                         suggestion="检查机房空调、设备风扇", weight=10, order=12),
        SNMPTemplateItem("hw-s-13", "风扇状态", "硬件", "1.3.6.1.4.1.2011.6.3.3.1.5.1", "integer",
                         threshold={"operator": "ne", "critical": 1, "warning": 1, "unit": ""},
                         suggestion="检查并更换故障风扇", weight=10, order=13),
        SNMPTemplateItem("hw-s-14", "电源状态", "硬件", "1.3.6.1.4.1.2011.6.3.3.1.7.1", "integer",
                         threshold={"operator": "ne", "critical": 1, "warning": 1, "unit": ""},
                         suggestion="检查并更换故障电源", weight=10, order=14),
    ]
)

HUAWEI_FIREWALL_TEMPLATE = SNMPDeviceTemplate(
    id="snmp-huawei-fw-v1",
    name="华为防火墙SNMP巡检模板",
    device_type="firewall",
    brand="华为",
    model="USG系列",
    description="华为USG防火墙SNMP巡检模板，覆盖CPU、内存、连接数、会话等",
    vendor_mib="huawei",
    items=[
        SNMPTemplateItem("hw-fw-01", "系统描述", "系统", "1.3.6.1.2.1.1.1.0", "string", weight=5, order=1),
        SNMPTemplateItem("hw-fw-02", "系统运行时间", "系统", "1.3.6.1.2.1.1.3.0", "timeticks", weight=5, order=2,
                         parser="ticks_to_uptime"),
        SNMPTemplateItem("hw-fw-03", "CPU使用率", "CPU", "1.3.6.1.4.1.2011.6.3.4.1.3.1", "integer",
                         threshold={"operator": "gt", "critical": 90, "warning": 75, "unit": "%"},
                         suggestion="检查异常流量、策略匹配", weight=20, order=3),
        SNMPTemplateItem("hw-fw-04", "内存使用率", "内存", "1.3.6.1.4.1.2011.6.3.5.1.4.1", "integer",
                         threshold={"operator": "gt", "critical": 85, "warning": 70, "unit": "%"},
                         suggestion="检查连接数、策略规则", weight=20, order=4),
        SNMPTemplateItem("hw-fw-05", "当前连接数", "性能", "1.3.6.1.2.1.6.9.0", "gauge",
                         threshold={"operator": "gt", "critical": 1000000, "warning": 500000, "unit": "连接"},
                         suggestion="检查是否存在异常连接或攻击", weight=20, order=5),
        SNMPTemplateItem("hw-fw-06", "设备温度", "硬件", "1.3.6.1.4.1.2011.6.3.3.1.9.1", "integer",
                         threshold={"operator": "gt", "critical": 75, "warning": 65, "unit": "°C"}, weight=10, order=6),
        SNMPTemplateItem("hw-fw-07", "风扇状态", "硬件", "1.3.6.1.4.1.2011.6.3.3.1.5.1", "integer",
                         threshold={"operator": "ne", "critical": 1, "warning": 1, "unit": ""}, weight=10, order=7),
        SNMPTemplateItem("hw-fw-08", "电源状态", "硬件", "1.3.6.1.4.1.2011.6.3.3.1.7.1", "integer",
                         threshold={"operator": "ne", "critical": 1, "warning": 1, "unit": ""}, weight=10, order=8),
    ]
)

# ============================================================
# 华三网络设备 SNMP 模板
# ============================================================

H3C_SWITCH_TEMPLATE = SNMPDeviceTemplate(
    id="snmp-h3c-switch-v1",
    name="华三交换机SNMP巡检模板",
    device_type="switch",
    brand="华三",
    model="通用交换机",
    description="华三交换机/路由器通用SNMP巡检模板",
    vendor_mib="h3c",
    items=[
        SNMPTemplateItem("h3c-s-01", "系统描述", "系统", "1.3.6.1.2.1.1.1.0", "string", weight=5, order=1),
        SNMPTemplateItem("h3c-s-02", "系统运行时间", "系统", "1.3.6.1.2.1.1.3.0", "timeticks", weight=5, order=2,
                         parser="ticks_to_uptime"),
        SNMPTemplateItem("h3c-s-03", "CPU使用率", "CPU", "1.3.6.1.4.1.25506.2.6.1.1.1.1.6.1", "integer",
                         threshold={"operator": "gt", "critical": 90, "warning": 70, "unit": "%"}, weight=20, order=3),
        SNMPTemplateItem("h3c-s-04", "内存使用率", "内存", "1.3.6.1.4.1.25506.2.6.1.1.1.1.8.1", "integer",
                         threshold={"operator": "gt", "critical": 85, "warning": 70, "unit": "%"}, weight=20, order=4),
        SNMPTemplateItem("h3c-s-05", "内存总量(KB)", "内存", "1.3.6.1.4.1.25506.2.6.1.1.1.1.7.1", "integer", weight=5, order=5),
        SNMPTemplateItem("h3c-s-06", "设备温度", "硬件", "1.3.6.1.4.1.25506.2.6.1.1.1.1.12.1", "integer",
                         threshold={"operator": "gt", "critical": 70, "warning": 60, "unit": "°C"}, weight=10, order=6),
        SNMPTemplateItem("h3c-s-07", "风扇状态", "硬件", "1.3.6.1.4.1.25506.2.6.1.1.1.1.14.1", "integer",
                         threshold={"operator": "ne", "critical": 1, "warning": 1, "unit": ""}, weight=10, order=7),
        SNMPTemplateItem("h3c-s-08", "电源状态", "硬件", "1.3.6.1.4.1.25506.2.6.1.1.1.1.16.1", "integer",
                         threshold={"operator": "ne", "critical": 1, "warning": 1, "unit": ""}, weight=10, order=8),
        SNMPTemplateItem("h3c-s-09", "接口数量", "接口", "1.3.6.1.2.1.2.1.0", "integer", weight=5, order=9),
        SNMPTemplateItem("h3c-s-10", "接口入错误包", "接口", "1.3.6.1.2.1.2.2.1.14", "counter", is_table=True,
                         threshold={"operator": "gt", "critical": 100, "warning": 10, "unit": "包"}, weight=15, order=10),
    ]
)

# ============================================================
# 思科网络设备 SNMP 模板
# ============================================================

CISCO_SWITCH_TEMPLATE = SNMPDeviceTemplate(
    id="snmp-cisco-switch-v1",
    name="思科交换机SNMP巡检模板",
    device_type="switch",
    brand="思科",
    model="Catalyst系列",
    description="思科Catalyst/Nexus交换机通用SNMP巡检模板",
    vendor_mib="cisco",
    items=[
        SNMPTemplateItem("c-s-01", "系统描述", "系统", "1.3.6.1.2.1.1.1.0", "string", weight=5, order=1),
        SNMPTemplateItem("c-s-02", "系统运行时间", "系统", "1.3.6.1.2.1.1.3.0", "timeticks", weight=5, order=2,
                         parser="ticks_to_uptime"),
        SNMPTemplateItem("c-s-03", "CPU 5分钟负载", "CPU", "1.3.6.1.4.1.9.9.109.1.1.1.1.7.1", "integer",
                         threshold={"operator": "gt", "critical": 90, "warning": 70, "unit": "%"},
                         suggestion="检查路由表大小、STP收敛", weight=20, order=3),
        SNMPTemplateItem("c-s-04", "已用内存", "内存", "1.3.6.1.4.1.9.9.48.1.1.1.5.1", "gauge", weight=15, order=4),
        SNMPTemplateItem("c-s-05", "空闲内存", "内存", "1.3.6.1.4.1.9.9.48.1.1.1.6.1", "gauge", weight=15, order=5),
        SNMPTemplateItem("c-s-06", "温度状态", "硬件", "1.3.6.1.4.1.9.9.13.1.3.1.6.1", "integer",
                         threshold={"operator": "ne", "critical": 1, "warning": 2, "unit": ""},
                         suggestion="检查设备散热", weight=15, order=6),
        SNMPTemplateItem("c-s-07", "风扇状态", "硬件", "1.3.6.1.4.1.9.9.13.1.4.1.3.1", "integer",
                         threshold={"operator": "ne", "critical": 1, "warning": 1, "unit": ""}, weight=10, order=7),
        SNMPTemplateItem("c-s-08", "电源状态", "硬件", "1.3.6.1.4.1.9.9.13.1.5.1.3.1", "integer",
                         threshold={"operator": "ne", "critical": 1, "warning": 1, "unit": ""}, weight=10, order=8),
        SNMPTemplateItem("c-s-09", "接口入错误包", "接口", "1.3.6.1.2.1.2.2.1.14", "counter", is_table=True,
                         threshold={"operator": "gt", "critical": 100, "warning": 10, "unit": "包"}, weight=15, order=9),
    ]
)

CISCO_ASA_TEMPLATE = SNMPDeviceTemplate(
    id="snmp-cisco-asa-v1",
    name="思科ASA防火墙SNMP巡检模板",
    device_type="firewall",
    brand="思科",
    model="ASA系列",
    description="思科ASA防火墙SNMP巡检模板",
    vendor_mib="cisco",
    items=[
        SNMPTemplateItem("asa-01", "系统描述", "系统", "1.3.6.1.2.1.1.1.0", "string", weight=5, order=1),
        SNMPTemplateItem("asa-02", "系统运行时间", "系统", "1.3.6.1.2.1.1.3.0", "timeticks", weight=5, order=2,
                         parser="ticks_to_uptime"),
        SNMPTemplateItem("asa-03", "CPU 5分钟负载", "CPU", "1.3.6.1.4.1.9.9.109.1.1.1.1.7.1", "integer",
                         threshold={"operator": "gt", "critical": 90, "warning": 70, "unit": "%"}, weight=20, order=3),
        SNMPTemplateItem("asa-04", "当前连接数", "性能", "1.3.6.1.2.1.6.9.0", "gauge",
                         threshold={"operator": "gt", "critical": 500000, "warning": 250000, "unit": "连接"}, weight=20, order=4),
        SNMPTemplateItem("asa-05", "接口数量", "接口", "1.3.6.1.2.1.2.1.0", "integer", weight=5, order=5),
    ]
)

# ============================================================
# F5 负载均衡 SNMP 模板
# ============================================================

F5_TEMPLATE = SNMPDeviceTemplate(
    id="snmp-f5-v1",
    name="F5 BIG-IP负载均衡SNMP巡检模板",
    device_type="load_balancer",
    brand="F5",
    model="BIG-IP系列",
    description="F5 BIG-IP负载均衡SNMP巡检模板，覆盖CPU、内存、连接、池状态",
    vendor_mib="f5",
    items=[
        SNMPTemplateItem("f5-01", "系统描述", "系统", "1.3.6.1.2.1.1.1.0", "string", weight=5, order=1),
        SNMPTemplateItem("f5-02", "系统运行时间", "系统", "1.3.6.1.2.1.1.3.0", "timeticks", weight=5, order=2,
                         parser="ticks_to_uptime"),
        SNMPTemplateItem("f5-03", "CPU使用率", "CPU", "1.3.6.1.4.1.3375.2.1.1.2.1.44.1", "integer",
                         threshold={"operator": "gt", "critical": 90, "warning": 70, "unit": "%"}, weight=20, order=3),
        SNMPTemplateItem("f5-04", "内存总量", "内存", "1.3.6.1.4.1.3375.2.1.1.2.1.35.1", "integer", weight=10, order=4),
        SNMPTemplateItem("f5-05", "已用内存", "内存", "1.3.6.1.4.1.3375.2.1.1.2.1.36.1", "integer", weight=10, order=5),
        SNMPTemplateItem("f5-06", "总连接数", "连接", "1.3.6.1.4.1.3375.2.1.1.2.1.39.1", "counter", weight=15, order=6),
        SNMPTemplateItem("f5-07", "活跃连接数", "连接", "1.3.6.1.4.1.3375.2.1.1.2.1.40.1", "gauge",
                         threshold={"operator": "gt", "critical": 500000, "warning": 250000, "unit": "连接"}, weight=20, order=7),
        SNMPTemplateItem("f5-08", "池可用状态", "池", "1.3.6.1.4.1.3375.2.2.5.5.2.1.6", "integer", is_table=True,
                         threshold={"operator": "ne", "critical": 1, "warning": 2, "unit": ""}, weight=15, order=8),
        SNMPTemplateItem("f5-09", "虚拟服务状态", "虚拟服务", "1.3.6.1.4.1.3375.2.2.10.13.2.1.3", "integer", is_table=True,
                         threshold={"operator": "ne", "critical": 1, "warning": 2, "unit": ""}, weight=15, order=9),
    ]
)

# ============================================================
# Dell iDRAC 服务器 SNMP 模板
# ============================================================

DELL_SERVER_TEMPLATE = SNMPDeviceTemplate(
    id="snmp-dell-server-v1",
    name="Dell服务器iDRAC SNMP巡检模板",
    device_type="server",
    brand="Dell",
    model="PowerEdge系列",
    description="Dell PowerEdge服务器iDRAC SNMP巡检模板，覆盖硬件健康、磁盘、电源、风扇",
    vendor_mib="dell",
    items=[
        SNMPTemplateItem("dell-01", "系统全局状态", "系统", "1.3.6.1.4.1.674.10892.1.200.10.1.2.1", "integer",
                         threshold={"operator": "ne", "critical": 3, "warning": 3, "unit": ""},
                         suggestion="检查iDRAC管理界面查看具体告警", weight=20, order=1),
        SNMPTemplateItem("dell-02", "机箱状态", "硬件", "1.3.6.1.4.1.674.10892.1.200.10.1.4.1", "integer",
                         threshold={"operator": "ne", "critical": 3, "warning": 3, "unit": ""}, weight=10, order=2),
        SNMPTemplateItem("dell-03", "电源状态", "电源", "1.3.6.1.4.1.674.10892.1.200.10.1.5.1", "integer",
                         threshold={"operator": "ne", "critical": 3, "warning": 3, "unit": ""},
                         suggestion="检查电源模块连接和状态", weight=15, order=3),
        SNMPTemplateItem("dell-04", "风扇状态", "散热", "1.3.6.1.4.1.674.10892.1.200.10.1.8.1", "integer",
                         threshold={"operator": "ne", "critical": 3, "warning": 3, "unit": ""},
                         suggestion="检查风扇是否正常运转", weight=10, order=4),
        SNMPTemplateItem("dell-05", "温度状态", "散热", "1.3.6.1.4.1.674.10892.1.200.10.1.9.1", "integer",
                         threshold={"operator": "ne", "critical": 3, "warning": 3, "unit": ""},
                         suggestion="检查机房环境和散热", weight=15, order=5),
        SNMPTemplateItem("dell-06", "内存状态", "内存", "1.3.6.1.4.1.674.10892.1.200.10.1.11.1", "integer",
                         threshold={"operator": "ne", "critical": 3, "warning": 3, "unit": ""},
                         suggestion="检查内存模块是否故障", weight=15, order=6),
        SNMPTemplateItem("dell-07", "存储状态", "存储", "1.3.6.1.4.1.674.10892.1.200.10.1.14.1", "integer",
                         threshold={"operator": "ne", "critical": 3, "warning": 3, "unit": ""},
                         suggestion="检查硬盘状态和RAID控制器", weight=15, order=7),
        SNMPTemplateItem("dell-08", "处理器状态", "CPU", "1.3.6.1.4.1.674.10892.1.200.10.1.15.1", "integer",
                         threshold={"operator": "ne", "critical": 3, "warning": 3, "unit": ""}, weight=10, order=8),
        SNMPTemplateItem("dell-09", "电池状态", "电源", "1.3.6.1.4.1.674.10892.1.200.10.1.18.1", "integer",
                         threshold={"operator": "ne", "critical": 3, "warning": 3, "unit": ""},
                         suggestion="检查RAID电池", weight=5, order=9),
    ]
)

# ============================================================
# Linux 服务器 SNMP 模板 (Net-SNMP)
# ============================================================

LINUX_SNMP_TEMPLATE = SNMPDeviceTemplate(
    id="snmp-linux-server-v1",
    name="Linux服务器SNMP巡检模板",
    device_type="server",
    brand="Generic",
    model="Linux",
    description="Linux服务器通用SNMP巡检模板（需安装net-snmp），覆盖CPU、内存、磁盘、负载",
    vendor_mib="ucd_snmp",
    items=[
        SNMPTemplateItem("lnx-01", "系统描述", "系统", "1.3.6.1.2.1.1.1.0", "string", weight=5, order=1),
        SNMPTemplateItem("lnx-02", "系统运行时间", "系统", "1.3.6.1.2.1.1.3.0", "timeticks", weight=5, order=2,
                         parser="ticks_to_uptime"),
        SNMPTemplateItem("lnx-03", "系统负载1分钟", "CPU", "1.3.6.1.4.1.2021.10.1.3.1", "string",
                         threshold={"operator": "gt", "critical": 16, "warning": 8, "unit": ""}, weight=20, order=3),
        SNMPTemplateItem("lnx-04", "系统负载5分钟", "CPU", "1.3.6.1.4.1.2021.10.1.3.2", "string", weight=10, order=4),
        SNMPTemplateItem("lnx-05", "系统负载15分钟", "CPU", "1.3.6.1.4.1.2021.10.1.3.3", "string", weight=10, order=5),
        SNMPTemplateItem("lnx-06", "CPU空闲率", "CPU", "1.3.6.1.4.1.2021.11.53.0", "counter",
                         threshold={"operator": "lt", "critical": 10, "warning": 30, "unit": "%"}, weight=15, order=6),
        SNMPTemplateItem("lnx-07", "物理内存总量", "内存", "1.3.6.1.4.1.2021.4.5.0", "integer", weight=5, order=7),
        SNMPTemplateItem("lnx-08", "可用物理内存", "内存", "1.3.6.1.4.1.2021.4.6.0", "integer",
                         threshold={"operator": "lt", "critical": 524288, "warning": 1048576, "unit": "KB"}, weight=20, order=8),
        SNMPTemplateItem("lnx-09", "Swap总量", "内存", "1.3.6.1.4.1.2021.4.3.0", "integer", weight=5, order=9),
        SNMPTemplateItem("lnx-10", "可用Swap", "内存", "1.3.6.1.4.1.2021.4.4.0", "integer", weight=10, order=10),
        SNMPTemplateItem("lnx-11", "磁盘挂载点", "磁盘", "1.3.6.1.4.1.2021.9.1.2", "string", is_table=True, weight=5, order=11),
        SNMPTemplateItem("lnx-12", "磁盘使用率", "磁盘", "1.3.6.1.4.1.2021.9.1.9", "integer", is_table=True,
                         threshold={"operator": "gt", "critical": 90, "warning": 80, "unit": "%"},
                         suggestion="清理无用文件或扩容磁盘", weight=20, order=12),
        SNMPTemplateItem("lnx-13", "Inode使用率", "磁盘", "1.3.6.1.4.1.2021.9.1.10", "integer", is_table=True,
                         threshold={"operator": "gt", "critical": 90, "warning": 80, "unit": "%"},
                         suggestion="清理小文件或调整inode", weight=10, order=13),
        SNMPTemplateItem("lnx-14", "进程数", "系统", "1.3.6.1.2.1.25.1.6.0", "gauge",
                         threshold={"operator": "gt", "critical": 1000, "warning": 500, "unit": "进程"}, weight=10, order=14),
    ]
)

# ============================================================
# 深信服设备 SNMP 模板
# ============================================================

SANGFOR_TEMPLATE = SNMPDeviceTemplate(
    id="snmp-sangfor-v1",
    name="深信服设备SNMP巡检模板",
    device_type="security",
    brand="深信服",
    model="通用",
    description="深信服上网行为管理/防火墙SNMP巡检模板",
    vendor_mib="sangfor",
    items=[
        SNMPTemplateItem("sf-01", "系统状态", "系统", "1.3.6.1.4.1.35047.1.3.0", "integer",
                         threshold={"operator": "ne", "critical": 1, "warning": 1, "unit": ""}, weight=20, order=1),
        SNMPTemplateItem("sf-02", "CPU使用率", "CPU", "1.3.6.1.4.1.35047.1.5.1.2.0", "integer",
                         threshold={"operator": "gt", "critical": 90, "warning": 70, "unit": "%"}, weight=20, order=2),
        SNMPTemplateItem("sf-03", "内存使用率", "内存", "1.3.6.1.4.1.35047.1.5.1.3.0", "integer",
                         threshold={"operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, weight=20, order=3),
        SNMPTemplateItem("sf-04", "磁盘使用率", "磁盘", "1.3.6.1.4.1.35047.1.5.1.4.0", "integer",
                         threshold={"operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, weight=15, order=4),
        SNMPTemplateItem("sf-05", "活跃连接数", "性能", "1.3.6.1.4.1.35047.1.5.1.5.0", "gauge",
                         threshold={"operator": "gt", "critical": 500000, "warning": 250000, "unit": "连接"}, weight=15, order=5),
        SNMPTemplateItem("sf-06", "总连接数", "性能", "1.3.6.1.4.1.35047.1.5.1.6.0", "counter", weight=10, order=6),
        SNMPTemplateItem("sf-07", "吞吐量(bps)", "性能", "1.3.6.1.4.1.35047.1.5.1.7.0", "gauge", weight=10, order=7),
    ]
)

# ============================================================
# Checkpoint 防火墙 SNMP 模板
# ============================================================

CHECKPOINT_TEMPLATE = SNMPDeviceTemplate(
    id="snmp-checkpoint-v1",
    name="Checkpoint防火墙SNMP巡检模板",
    device_type="firewall",
    brand="Checkpoint",
    model="通用",
    description="Checkpoint防火墙SNMP巡检模板",
    vendor_mib="checkpoint",
    items=[
        SNMPTemplateItem("cp-01", "系统描述", "系统", "1.3.6.1.2.1.1.1.0", "string", weight=5, order=1),
        SNMPTemplateItem("cp-02", "系统运行时间", "系统", "1.3.6.1.2.1.1.3.0", "timeticks", weight=5, order=2,
                         parser="ticks_to_uptime"),
        SNMPTemplateItem("cp-03", "CPU使用率", "CPU", "1.3.6.1.4.1.2620.1.6.7.2.4.0", "integer",
                         threshold={"operator": "gt", "critical": 90, "warning": 70, "unit": "%"}, weight=20, order=3),
        SNMPTemplateItem("cp-04", "内存使用率", "内存", "1.3.6.1.4.1.2620.1.6.7.2.5.0", "integer",
                         threshold={"operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, weight=20, order=4),
        SNMPTemplateItem("cp-05", "当前连接数", "性能", "1.3.6.1.4.1.2620.1.1.5.0", "gauge",
                         threshold={"operator": "gt", "critical": 500000, "warning": 250000, "unit": "连接"}, weight=20, order=5),
        SNMPTemplateItem("cp-06", "连接峰值", "性能", "1.3.6.1.4.1.2620.1.1.6.0", "gauge", weight=10, order=6),
        SNMPTemplateItem("cp-07", "策略名称", "配置", "1.3.6.1.4.1.2620.1.1.1.0", "string", weight=5, order=7),
        SNMPTemplateItem("cp-08", "策略安装时间", "配置", "1.3.6.1.4.1.2620.1.1.2.0", "string", weight=5, order=8),
    ]
)

# ============================================================
# Brocade SAN交换机 SNMP 模板
# ============================================================

BROCADE_SNMP_TEMPLATE = SNMPDeviceTemplate(
    id="snmp-brocade-v1",
    name="Brocade SAN交换机SNMP巡检模板",
    device_type="san_switch",
    brand="Brocade",
    model="G系列",
    description="Brocade光纤交换机SNMP巡检模板，覆盖温度、端口错误、链路状态",
    vendor_mib="brocade",
    items=[
        SNMPTemplateItem("brcd-01", "系统描述", "系统", "1.3.6.1.2.1.1.1.0", "string", weight=5, order=1),
        SNMPTemplateItem("brcd-02", "系统运行时间", "系统", "1.3.6.1.2.1.1.3.0", "timeticks", weight=5, order=2,
                         parser="ticks_to_uptime"),
        SNMPTemplateItem("brcd-03", "温度传感器", "硬件", "1.3.6.1.4.1.1588.2.1.1.1.1.22.1.3", "integer", is_table=True,
                         threshold={"operator": "gt", "critical": 70, "warning": 60, "unit": "°C"}, weight=15, order=3),
        SNMPTemplateItem("brcd-04", "传感器状态", "硬件", "1.3.6.1.4.1.1588.2.1.1.1.1.22.1.4", "integer", is_table=True,
                         threshold={"operator": "ne", "critical": 3, "warning": 3, "unit": ""}, weight=10, order=4),
        SNMPTemplateItem("brcd-05", "FC端口CRC错误", "端口", "1.3.6.1.4.1.1588.2.1.1.1.6.2.1.17", "counter64", is_table=True,
                         threshold={"operator": "gt", "critical": 100, "warning": 10, "unit": "错误"},
                         suggestion="检查SFP模块和光纤线路", weight=20, order=5),
        SNMPTemplateItem("brcd-06", "FC端口链路失败", "端口", "1.3.6.1.4.1.1588.2.1.1.1.6.2.1.13", "counter64", is_table=True,
                         threshold={"operator": "gt", "critical": 5, "warning": 1, "unit": "次"},
                         suggestion="检查光纤连接和SFP兼容性", weight=20, order=6),
        SNMPTemplateItem("brcd-07", "FC端口接收字", "端口", "1.3.6.1.4.1.1588.2.1.1.1.6.2.1.9", "counter64", is_table=True, weight=10, order=7),
        SNMPTemplateItem("brcd-08", "FC端口发送字", "端口", "1.3.6.1.4.1.1588.2.1.1.1.6.2.1.10", "counter64", is_table=True, weight=10, order=8),
    ]
)

# ============================================================
# 通用网络设备模板（基于标准MIB-II）
# ============================================================

GENERIC_NETWORK_TEMPLATE = SNMPDeviceTemplate(
    id="snmp-generic-network-v1",
    name="通用网络设备SNMP巡检模板",
    device_type="network",
    brand="通用",
    model="通用",
    description="基于标准MIB-II的通用网络设备SNMP巡检模板",
    vendor_mib="standard",
    items=[
        SNMPTemplateItem("gen-01", "系统描述", "系统", "1.3.6.1.2.1.1.1.0", "string", weight=5, order=1),
        SNMPTemplateItem("gen-02", "系统运行时间", "系统", "1.3.6.1.2.1.1.3.0", "timeticks", weight=5, order=2,
                         parser="ticks_to_uptime"),
        SNMPTemplateItem("gen-03", "接口数量", "接口", "1.3.6.1.2.1.2.1.0", "integer", weight=5, order=3),
        SNMPTemplateItem("gen-04", "接口速率", "接口", "1.3.6.1.2.1.2.2.1.5", "gauge", is_table=True, weight=10, order=4),
        SNMPTemplateItem("gen-05", "接口运行状态", "接口", "1.3.6.1.2.1.2.2.1.8", "integer", is_table=True,
                         threshold={"operator": "ne", "critical": 1, "warning": 1, "unit": ""},
                         suggestion="检查接口物理连接", weight=20, order=5),
        SNMPTemplateItem("gen-06", "接口入流量", "接口", "1.3.6.1.2.1.2.2.1.10", "counter", is_table=True, weight=10, order=6),
        SNMPTemplateItem("gen-07", "接口出流量", "接口", "1.3.6.1.2.1.2.2.1.16", "counter", is_table=True, weight=10, order=7),
        SNMPTemplateItem("gen-08", "接口入错误包", "接口", "1.3.6.1.2.1.2.2.1.14", "counter", is_table=True,
                         threshold={"operator": "gt", "critical": 100, "warning": 10, "unit": "包"}, weight=15, order=8),
        SNMPTemplateItem("gen-09", "接口出错误包", "接口", "1.3.6.1.2.1.2.2.1.20", "counter", is_table=True,
                         threshold={"operator": "gt", "critical": 100, "warning": 10, "unit": "包"}, weight=15, order=9),
        SNMPTemplateItem("gen-10", "IP接收包", "网络", "1.3.6.1.2.1.4.3.0", "counter", weight=5, order=10),
        SNMPTemplateItem("gen-11", "TCP当前连接", "连接", "1.3.6.1.2.1.6.9.0", "gauge", weight=5, order=11),
    ]
)

# ============================================================
# 所有模板注册表
# ============================================================

ALL_SNMP_TEMPLATES = {
    "snmp-huawei-switch-v1": HUAWEI_SWITCH_TEMPLATE,
    "snmp-huawei-fw-v1": HUAWEI_FIREWALL_TEMPLATE,
    "snmp-h3c-switch-v1": H3C_SWITCH_TEMPLATE,
    "snmp-cisco-switch-v1": CISCO_SWITCH_TEMPLATE,
    "snmp-cisco-asa-v1": CISCO_ASA_TEMPLATE,
    "snmp-f5-v1": F5_TEMPLATE,
    "snmp-dell-server-v1": DELL_SERVER_TEMPLATE,
    "snmp-linux-server-v1": LINUX_SNMP_TEMPLATE,
    "snmp-sangfor-v1": SANGFOR_TEMPLATE,
    "snmp-checkpoint-v1": CHECKPOINT_TEMPLATE,
    "snmp-brocade-v1": BROCADE_SNMP_TEMPLATE,
    "snmp-generic-network-v1": GENERIC_NETWORK_TEMPLATE,
}


class SNMPTemplates:
    """SNMP模板管理器"""
    
    @staticmethod
    def get_all_templates() -> List[SNMPDeviceTemplate]:
        """获取所有模板"""
        return list(ALL_SNMP_TEMPLATES.values())
    
    @staticmethod
    def get_template(template_id: str) -> Optional[SNMPDeviceTemplate]:
        """获取指定模板"""
        return ALL_SNMP_TEMPLATES.get(template_id)
    
    @staticmethod
    def get_templates_by_brand(brand: str) -> List[SNMPDeviceTemplate]:
        """按品牌获取模板"""
        return [t for t in ALL_SNMP_TEMPLATES.values() if t.brand == brand]
    
    @staticmethod
    def get_templates_by_type(device_type: str) -> List[SNMPDeviceTemplate]:
        """按设备类型获取模板"""
        return [t for t in ALL_SNMP_TEMPLATES.values() if t.device_type == device_type]
    
    @staticmethod
    def get_template_items(template_id: str) -> List[SNMPTemplateItem]:
        """获取模板的巡检项"""
        template = ALL_SNMP_TEMPLATES.get(template_id)
        if template:
            return template.items
        return []
    
    @staticmethod
    def to_dict(template: SNMPDeviceTemplate) -> dict:
        """将模板转换为字典"""
        return {
            "id": template.id,
            "name": template.name,
            "device_type": template.device_type,
            "brand": template.brand,
            "model": template.model,
            "description": template.description,
            "vendor_mib": template.vendor_mib,
            "is_builtin": template.is_builtin,
            "items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "category": item.category,
                    "oid": item.oid,
                    "oid_type": item.oid_type,
                    "threshold": item.threshold,
                    "is_table": item.is_table,
                    "parser": item.parser,
                    "suggestion": item.suggestion,
                    "weight": item.weight,
                    "order": item.order,
                }
                for item in template.items
            ]
        }
    
    @staticmethod
    def get_templates_summary() -> List[dict]:
        """获取所有模板摘要"""
        return [
            {
                "id": t.id,
                "name": t.name,
                "device_type": t.device_type,
                "brand": t.brand,
                "model": t.model,
                "description": t.description,
                "item_count": len(t.items),
                "vendor_mib": t.vendor_mib,
            }
            for t in ALL_SNMP_TEMPLATES.values()
        ]

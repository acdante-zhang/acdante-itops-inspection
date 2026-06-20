"""
Acdante ITOps - SNMP OID Registry
基于 hlxxi.com SNMP OID 监控指标速查库
包含通用标准MIB和厂商私有MIB
"""

# ============================================================
# 通用标准 MIB-II OID (RFC 1213)
# ============================================================

STANDARD_MIB = {
    "system": {
        "description": "系统信息",
        "oids": {
            "sysDescr":      {"oid": "1.3.6.1.2.1.1.1.0",  "name": "系统描述", "type": "string"},
            "sysObjectID":   {"oid": "1.3.6.1.2.1.1.2.0",  "name": "系统OID", "type": "oid"},
            "sysUpTime":     {"oid": "1.3.6.1.2.1.1.3.0",  "name": "运行时间", "type": "timeticks"},
            "sysContact":    {"oid": "1.3.6.1.2.1.1.4.0",  "name": "联系人", "type": "string"},
            "sysName":       {"oid": "1.3.6.1.2.1.1.5.0",  "name": "主机名", "type": "string"},
            "sysLocation":   {"oid": "1.3.6.1.2.1.1.6.0",  "name": "物理位置", "type": "string"},
            "sysServices":   {"oid": "1.3.6.1.2.1.1.7.0",  "name": "服务层级", "type": "integer"},
        }
    },
    "interfaces": {
        "description": "网络接口",
        "oids": {
            "ifNumber":        {"oid": "1.3.6.1.2.1.2.1.0",    "name": "接口数量", "type": "integer"},
            "ifIndex":         {"oid": "1.3.6.1.2.1.2.2.1.1",   "name": "接口索引", "type": "integer", "table": True},
            "ifDescr":         {"oid": "1.3.6.1.2.1.2.2.1.2",   "name": "接口描述", "type": "string", "table": True},
            "ifType":          {"oid": "1.3.6.1.2.1.2.2.1.3",   "name": "接口类型", "type": "integer", "table": True},
            "ifMtu":           {"oid": "1.3.6.1.2.1.2.2.1.4",   "name": "MTU", "type": "integer", "table": True},
            "ifSpeed":         {"oid": "1.3.6.1.2.1.2.2.1.5",   "name": "接口速率", "type": "gauge", "table": True},
            "ifPhysAddress":   {"oid": "1.3.6.1.2.1.2.2.1.6",   "name": "MAC地址", "type": "string", "table": True},
            "ifAdminStatus":   {"oid": "1.3.6.1.2.1.2.2.1.7",   "name": "管理状态", "type": "integer", "table": True},
            "ifOperStatus":    {"oid": "1.3.6.1.2.1.2.2.1.8",   "name": "运行状态", "type": "integer", "table": True},
            "ifInOctets":      {"oid": "1.3.6.1.2.1.2.2.1.10",  "name": "入流量(字节)", "type": "counter", "table": True},
            "ifOutOctets":     {"oid": "1.3.6.1.2.1.2.2.1.16",  "name": "出流量(字节)", "type": "counter", "table": True},
            "ifInErrors":      {"oid": "1.3.6.1.2.1.2.2.1.14",  "name": "入错误包", "type": "counter", "table": True},
            "ifOutErrors":     {"oid": "1.3.6.1.2.1.2.2.1.20",  "name": "出错误包", "type": "counter", "table": True},
            "ifInDiscards":    {"oid": "1.3.6.1.2.1.2.2.1.13",  "name": "入丢弃包", "type": "counter", "table": True},
            "ifOutDiscards":   {"oid": "1.3.6.1.2.1.2.2.1.19",  "name": "出丢弃包", "type": "counter", "table": True},
        }
    },
    "ip": {
        "description": "IP协议",
        "oids": {
            "ipForwarding":      {"oid": "1.3.6.1.2.1.4.1.0",     "name": "IP转发", "type": "integer"},
            "ipInReceives":      {"oid": "1.3.6.1.2.1.4.3.0",     "name": "IP接收包", "type": "counter"},
            "ipOutRequests":     {"oid": "1.3.6.1.2.1.4.10.0",    "name": "IP发送请求", "type": "counter"},
            "ipInDiscards":      {"oid": "1.3.6.1.2.1.4.5.0",     "name": "IP丢弃包", "type": "counter"},
        }
    },
    "tcp": {
        "description": "TCP协议",
        "oids": {
            "tcpActiveOpens":    {"oid": "1.3.6.1.2.1.6.5.0",     "name": "TCP主动连接", "type": "counter"},
            "tcpPassiveOpens":   {"oid": "1.3.6.1.2.1.6.6.0",     "name": "TCP被动连接", "type": "counter"},
            "tcpCurrEstab":      {"oid": "1.3.6.1.2.1.6.9.0",     "name": "TCP当前连接", "type": "gauge"},
            "tcpInErrs":         {"oid": "1.3.6.1.2.1.6.14.0",    "name": "TCP错误", "type": "counter"},
        }
    },
    "udp": {
        "description": "UDP协议",
        "oids": {
            "udpInDatagrams":    {"oid": "1.3.6.1.2.1.7.1.0",     "name": "UDP接收", "type": "counter"},
            "udpOutDatagrams":   {"oid": "1.3.6.1.2.1.7.4.0",     "name": "UDP发送", "type": "counter"},
            "udpInErrors":       {"oid": "1.3.6.1.2.1.7.3.0",     "name": "UDP错误", "type": "counter"},
        }
    },
    "snmp": {
        "description": "SNMP统计",
        "oids": {
            "snmpInPkts":        {"oid": "1.3.6.1.2.1.11.1.0",    "name": "SNMP接收包", "type": "counter"},
            "snmpOutPkts":       {"oid": "1.3.6.1.2.1.11.2.0",    "name": "SNMP发送包", "type": "counter"},
            "snmpInBadVersions": {"oid": "1.3.6.1.2.1.11.3.0",    "name": "SNMP版本错误", "type": "counter"},
            "snmpInBadCommunity": {"oid": "1.3.6.1.2.1.11.4.0",   "name": "SNMP团体名错误", "type": "counter"},
        }
    },
}

# ============================================================
# 主机资源 MIB (RFC 2790 - HOST-RESOURCES-MIB)
# ============================================================

HOST_RESOURCES_MIB = {
    "description": "主机资源（CPU/内存/磁盘）",
    "oids": {
        "hrSystemUptime":     {"oid": "1.3.6.1.2.1.25.1.1.0",    "name": "系统运行时间", "type": "timeticks"},
        "hrSystemNumUsers":   {"oid": "1.3.6.1.2.1.25.1.5.0",    "name": "在线用户数", "type": "gauge"},
        "hrSystemProcesses":  {"oid": "1.3.6.1.2.1.25.1.6.0",    "name": "进程数", "type": "gauge"},
        "hrSystemMaxProcesses": {"oid": "1.3.6.1.2.1.25.1.7.0",  "name": "最大进程数", "type": "integer"},
        "hrMemorySize":       {"oid": "1.3.6.1.2.1.25.2.2.0",    "name": "物理内存(KB)", "type": "integer"},
        "hrStorageTypes":     {"oid": "1.3.6.1.2.1.25.2.3.1",    "name": "存储类型", "type": "table"},
        "hrStorageDescr":     {"oid": "1.3.6.1.2.1.25.2.3.1.3",  "name": "存储描述", "type": "string", "table": True},
        "hrStorageAllocationUnits": {"oid": "1.3.6.1.2.1.25.2.3.1.4", "name": "分配单元", "type": "integer", "table": True},
        "hrStorageSize":      {"oid": "1.3.6.1.2.1.25.2.3.1.5",  "name": "存储总量", "type": "integer", "table": True},
        "hrStorageUsed":      {"oid": "1.3.6.1.2.1.25.2.3.1.6",  "name": "存储已用", "type": "integer", "table": True},
        "hrProcessorLoad":    {"oid": "1.3.6.1.2.1.25.3.3.1.2",  "name": "CPU负载(%)", "type": "integer", "table": True},
    }
}

# ============================================================
# UCD-SNMP-MIB (Net-SNMP) - Linux系统扩展
# ============================================================

UCD_SNMP_MIB = {
    "description": "Net-SNMP系统扩展（Linux/Unix）",
    "oids": {
        "laLoad":            {"oid": "1.3.6.1.4.1.2021.10.1.3",  "name": "系统负载", "type": "table"},
        "ssCpuRawUser":      {"oid": "1.3.6.1.4.1.2021.11.50.0", "name": "CPU用户态", "type": "counter"},
        "ssCpuRawSystem":    {"oid": "1.3.6.1.4.1.2021.11.52.0", "name": "CPU系统态", "type": "counter"},
        "ssCpuRawIdle":      {"oid": "1.3.6.1.4.1.2021.11.53.0", "name": "CPU空闲", "type": "counter"},
        "ssCpuRawWait":      {"oid": "1.3.6.1.4.1.2021.11.54.0", "name": "CPU等待IO", "type": "counter"},
        "ssRawInterrupts":   {"oid": "1.3.6.1.4.1.2021.11.59.0", "name": "中断次数", "type": "counter"},
        "ssRawContexts":     {"oid": "1.3.6.1.4.1.2021.11.60.0", "name": "上下文切换", "type": "counter"},
        "memTotalReal":      {"oid": "1.3.6.1.4.1.2021.4.5.0",   "name": "物理内存总量(KB)", "type": "integer"},
        "memAvailReal":      {"oid": "1.3.6.1.4.1.2021.4.6.0",   "name": "可用物理内存(KB)", "type": "integer"},
        "memTotalSwap":      {"oid": "1.3.6.1.4.1.2021.4.3.0",   "name": "Swap总量(KB)", "type": "integer"},
        "memAvailSwap":      {"oid": "1.3.6.1.4.1.2021.4.4.0",   "name": "可用Swap(KB)", "type": "integer"},
        "memBuffer":         {"oid": "1.3.6.1.4.1.2021.4.14.0",  "name": "缓冲区(KB)", "type": "integer"},
        "memCached":         {"oid": "1.3.6.1.4.1.2021.4.15.0",  "name": "缓存(KB)", "type": "integer"},
        "dskIndex":          {"oid": "1.3.6.1.4.1.2021.9.1.1",   "name": "磁盘索引", "type": "table"},
        "dskPath":           {"oid": "1.3.6.1.4.1.2021.9.1.2",   "name": "磁盘挂载点", "type": "string", "table": True},
        "dskTotal":          {"oid": "1.3.6.1.4.1.2021.9.1.6",   "name": "磁盘总量(KB)", "type": "integer", "table": True},
        "dskAvail":          {"oid": "1.3.6.1.4.1.2021.9.1.7",   "name": "磁盘可用(KB)", "type": "integer", "table": True},
        "dskUsed":           {"oid": "1.3.6.1.4.1.2021.9.1.8",   "name": "磁盘已用(KB)", "type": "integer", "table": True},
        "dskPercent":        {"oid": "1.3.6.1.4.1.2021.9.1.9",   "name": "磁盘使用率(%)", "type": "integer", "table": True},
        "dskPercentNode":    {"oid": "1.3.6.1.4.1.2021.9.1.10",  "name": "Inode使用率(%)", "type": "integer", "table": True},
    }
}

# ============================================================
# 华为私有 MIB (HUAWEI-MIB)
# ============================================================

HUAWEI_MIB = {
    "description": "华为网络设备私有MIB",
    "enterprise_oid": "1.3.6.1.4.1.2011",
    "oids": {
        "hwCpuDevDuty":        {"oid": "1.3.6.1.4.1.2011.6.3.4.1.3",   "name": "CPU使用率(%)", "type": "integer", "table": True},
        "hwCpuDevTemperature":  {"oid": "1.3.6.1.4.1.2011.6.3.4.1.7",   "name": "CPU温度(°C)", "type": "integer", "table": True},
        "hwMemDevSize":        {"oid": "1.3.6.1.4.1.2011.6.3.5.1.2",    "name": "内存总量", "type": "integer", "table": True},
        "hwMemDevFree":        {"oid": "1.3.6.1.4.1.2011.6.3.5.1.3",    "name": "空闲内存", "type": "integer", "table": True},
        "hwMemDevDuty":        {"oid": "1.3.6.1.4.1.2011.6.3.5.1.4",    "name": "内存使用率(%)", "type": "integer", "table": True},
        "hwDevFanStatus":      {"oid": "1.3.6.1.4.1.2011.6.3.3.1.5",    "name": "风扇状态", "type": "integer", "table": True},
        "hwDevPowerStatus":    {"oid": "1.3.6.1.4.1.2011.6.3.3.1.7",    "name": "电源状态", "type": "integer", "table": True},
        "hwDevTemperature":    {"oid": "1.3.6.1.4.1.2011.6.3.3.1.9",    "name": "设备温度(°C)", "type": "integer", "table": True},
        "hwEntityAdminStatus": {"oid": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.5", "name": "实体管理状态", "type": "integer", "table": True},
        "hwEntityOperStatus":  {"oid": "1.3.6.1.4.1.2011.5.25.31.1.1.1.1.6", "name": "实体运行状态", "type": "integer", "table": True},
        "hwIfFlowIn":          {"oid": "1.3.6.1.4.1.2011.5.25.32.1.1.3.1.6", "name": "接口入流量", "type": "counter64", "table": True},
        "hwIfFlowOut":         {"oid": "1.3.6.1.4.1.2011.5.25.32.1.1.3.1.7", "name": "接口出流量", "type": "counter64", "table": True},
        "hwIfCrcError":        {"oid": "1.3.6.1.4.1.2011.5.25.32.1.1.3.1.10", "name": "CRC错误", "type": "counter64", "table": True},
        "hwSysVersion":        {"oid": "1.3.6.1.4.1.2011.6.1.1.1.1.3",   "name": "系统版本", "type": "string", "table": True},
        "hwSysService":        {"oid": "1.3.6.1.4.1.2011.6.1.1.1.1.4",   "name": "系统服务", "type": "string", "table": True},
    }
}

# ============================================================
# 华三私有 MIB (H3C-MIB)
# ============================================================

H3C_MIB = {
    "description": "华三网络设备私有MIB",
    "enterprise_oid": "1.3.6.1.4.1.25506",
    "oids": {
        "hh3cCpuUsage":          {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.6",  "name": "CPU使用率(%)", "type": "integer", "table": True},
        "hh3cMemUsage":          {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.8",  "name": "内存使用率(%)", "type": "integer", "table": True},
        "hh3cMemSize":           {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.7",  "name": "内存总量", "type": "integer", "table": True},
        "hh3cDevTemperature":    {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.12", "name": "设备温度(°C)", "type": "integer", "table": True},
        "hh3cFanStatus":         {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.14", "name": "风扇状态", "type": "integer", "table": True},
        "hh3cPowerStatus":       {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.16", "name": "电源状态", "type": "integer", "table": True},
        "hh3cProcessNum":        {"oid": "1.3.6.1.4.1.25506.2.6.1.1.1.1.5",  "name": "进程数", "type": "integer", "table": True},
    }
}

# ============================================================
# 思科私有 MIB (CISCO-MIB)
# ============================================================

CISCO_MIB = {
    "description": "思科网络设备私有MIB",
    "enterprise_oid": "1.3.6.1.4.1.9",
    "oids": {
        "ciscoCpu5Min":          {"oid": "1.3.6.1.4.1.9.9.109.1.1.1.1.7",  "name": "CPU 5分钟负载(%)", "type": "integer", "table": True},
        "ciscoMemoryPoolUsed":   {"oid": "1.3.6.1.4.1.9.9.48.1.1.1.5",     "name": "已用内存", "type": "gauge", "table": True},
        "ciscoMemoryPoolFree":   {"oid": "1.3.6.1.4.1.9.9.48.1.1.1.6",     "name": "空闲内存", "type": "gauge", "table": True},
        "ciscoEnvMonTempStatus": {"oid": "1.3.6.1.4.1.9.9.13.1.3.1.6",     "name": "温度状态", "type": "integer", "table": True},
        "ciscoEnvMonFanState":   {"oid": "1.3.6.1.4.1.9.9.13.1.4.1.3",     "name": "风扇状态", "type": "integer", "table": True},
        "ciscoEnvMonSupplyState":{"oid": "1.3.6.1.4.1.9.9.13.1.5.1.3",     "name": "电源状态", "type": "integer", "table": True},
        "cpmCPUTotal5min":       {"oid": "1.3.6.1.4.1.9.9.109.1.1.1.1.7",  "name": "CPU使用率(%)", "type": "integer", "table": True},
    }
}

# ============================================================
# F5 BIG-IP 私有 MIB
# ============================================================

F5_MIB = {
    "description": "F5 BIG-IP负载均衡私有MIB",
    "enterprise_oid": "1.3.6.1.4.1.3375",
    "oids": {
        "sysCpuUsage5min":           {"oid": "1.3.6.1.4.1.3375.2.1.1.2.1.44", "name": "CPU使用率(%)", "type": "integer", "table": True},
        "sysMemoryTotal":            {"oid": "1.3.6.1.4.1.3375.2.1.1.2.1.35", "name": "内存总量", "type": "integer", "table": True},
        "sysMemoryUsed":             {"oid": "1.3.6.1.4.1.3375.2.1.1.2.1.36", "name": "已用内存", "type": "integer", "table": True},
        "sysConnectionTotal":        {"oid": "1.3.6.1.4.1.3375.2.1.1.2.1.39", "name": "总连接数", "type": "counter", "table": True},
        "sysConnectionActive":       {"oid": "1.3.6.1.4.1.3375.2.1.1.2.1.40", "name": "活跃连接数", "type": "gauge", "table": True},
        "sysGlobalStatClientCurConns": {"oid": "1.3.6.1.4.1.3375.2.1.1.2.1.40", "name": "客户端当前连接", "type": "gauge"},
        "ltmPoolStatusAvailState":   {"oid": "1.3.6.1.4.1.3375.2.2.5.5.2.1.6", "name": "池可用状态", "type": "integer", "table": True},
        "ltmPoolStatusActiveMemberCnt": {"oid": "1.3.6.1.4.1.3375.2.2.5.5.2.1.13", "name": "活跃成员数", "type": "gauge", "table": True},
        "ltmVsStatusAvailState":     {"oid": "1.3.6.1.4.1.3375.2.2.10.13.2.1.3", "name": "虚拟服务状态", "type": "integer", "table": True},
        "ltmVsStatusTotalConnections": {"oid": "1.3.6.1.4.1.3375.2.2.10.13.2.1.10", "name": "虚拟服务总连接", "type": "counter64", "table": True},
    }
}

# ============================================================
# Dell 服务器 MIB (iDRAC)
# ============================================================

DELL_MIB = {
    "description": "Dell服务器iDRAC私有MIB",
    "enterprise_oid": "1.3.6.1.4.1.674",
    "oids": {
        "dellSystemState":              {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.2.1", "name": "系统全局状态", "type": "integer"},
        "dellSystemStateChassis":       {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.4.1", "name": "机箱状态", "type": "integer"},
        "dellSystemStatePowerSupply":   {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.5.1", "name": "电源状态", "type": "integer"},
        "dellSystemStateFan":           {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.8.1", "name": "风扇状态", "type": "integer"},
        "dellSystemStateTemperature":   {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.9.1", "name": "温度状态", "type": "integer"},
        "dellSystemStateMemory":        {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.11.1", "name": "内存状态", "type": "integer"},
        "dellSystemStateStorage":       {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.14.1", "name": "存储状态", "type": "integer"},
        "dellSystemStateProcessor":     {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.15.1", "name": "处理器状态", "type": "integer"},
        "dellSystemBatteryStatus":      {"oid": "1.3.6.1.4.1.674.10892.1.200.10.1.18.1", "name": "电池状态", "type": "integer"},
    }
}

# ============================================================
# 深信服 MIB
# ============================================================

SANGFOR_MIB = {
    "description": "深信服设备私有MIB",
    "enterprise_oid": "1.3.6.1.4.1.35047",
    "oids": {
        "sangforSysStatus":         {"oid": "1.3.6.1.4.1.35047.1.3.0",   "name": "系统状态", "type": "integer"},
        "sangforCpuUsage":          {"oid": "1.3.6.1.4.1.35047.1.5.1.2", "name": "CPU使用率(%)", "type": "integer"},
        "sangforMemUsage":          {"oid": "1.3.6.1.4.1.35047.1.5.1.3", "name": "内存使用率(%)", "type": "integer"},
        "sangforDiskUsage":         {"oid": "1.3.6.1.4.1.35047.1.5.1.4", "name": "磁盘使用率(%)", "type": "integer"},
        "sangforActiveConnections": {"oid": "1.3.6.1.4.1.35047.1.5.1.5", "name": "活跃连接数", "type": "gauge"},
        "sangforTotalConnections":  {"oid": "1.3.6.1.4.1.35047.1.5.1.6", "name": "总连接数", "type": "counter"},
        "sangforThroughput":        {"oid": "1.3.6.1.4.1.35047.1.5.1.7", "name": "吞吐量(bps)", "type": "gauge"},
    }
}

# ============================================================
# Checkpoint 防火墙 MIB
# ============================================================

CHECKPOINT_MIB = {
    "description": "Checkpoint防火墙私有MIB",
    "enterprise_oid": "1.3.6.1.4.1.2620",
    "oids": {
        "fwConnTableLimit":    {"oid": "1.3.6.1.4.1.2620.1.1.4.0",   "name": "连接表限制", "type": "integer"},
        "fwConnTableCurrent":  {"oid": "1.3.6.1.4.1.2620.1.1.5.0",   "name": "当前连接数", "type": "gauge"},
        "fwConnTablePeak":     {"oid": "1.3.6.1.4.1.2620.1.1.6.0",   "name": "峰值连接数", "type": "gauge"},
        "fwCpuUsage":          {"oid": "1.3.6.1.4.1.2620.1.6.7.2.4.0", "name": "CPU使用率(%)", "type": "integer"},
        "fwMemUsage":          {"oid": "1.3.6.1.4.1.2620.1.6.7.2.5.0", "name": "内存使用率(%)", "type": "integer"},
        "fwPolicyName":        {"oid": "1.3.6.1.4.1.2620.1.1.1.0",   "name": "策略名称", "type": "string"},
        "fwInstallTime":       {"oid": "1.3.6.1.4.1.2620.1.1.2.0",   "name": "策略安装时间", "type": "string"},
    }
}

# ============================================================
# 博科 SAN交换机 MIB
# ============================================================

BROCADE_MIB = {
    "description": "Brocade SAN交换机私有MIB",
    "enterprise_oid": "1.3.6.1.4.1.1588",
    "oids": {
        "swSensorStatus":       {"oid": "1.3.6.1.4.1.1588.2.1.1.1.1.22.1.4", "name": "传感器状态", "type": "integer", "table": True},
        "swSensorTemperature":  {"oid": "1.3.6.1.4.1.1588.2.1.1.1.1.22.1.3", "name": "温度(°C)", "type": "integer", "table": True},
        "swFCPortRxWords":     {"oid": "1.3.6.1.4.1.1588.2.1.1.1.6.2.1.9",  "name": "FC端口接收字", "type": "counter64", "table": True},
        "swFCPortTxWords":     {"oid": "1.3.6.1.4.1.1588.2.1.1.1.6.2.1.10", "name": "FC端口发送字", "type": "counter64", "table": True},
        "swFCPortCrcErrors":   {"oid": "1.3.6.1.4.1.1588.2.1.1.1.6.2.1.17", "name": "CRC错误", "type": "counter64", "table": True},
        "swFCPortLinkFailures": {"oid": "1.3.6.1.4.1.1588.2.1.1.1.6.2.1.13", "name": "链路失败次数", "type": "counter64", "table": True},
    }
}

# ============================================================
# 合并所有OID注册表
# ============================================================

ALL_OID_REGISTRY = {
    "standard": STANDARD_MIB,
    "host_resources": HOST_RESOURCES_MIB,
    "ucd_snmp": UCD_SNMP_MIB,
    "huawei": HUAWEI_MIB,
    "h3c": H3C_MIB,
    "cisco": CISCO_MIB,
    "f5": F5_MIB,
    "dell": DELL_MIB,
    "sangfor": SANGFOR_MIB,
    "checkpoint": CHECKPOINT_MIB,
    "brocade": BROCADE_MIB,
}

# ============================================================
# 工具函数
# ============================================================

class SNMPOIDRegistry:
    """SNMP OID注册表查询工具"""
    
    def __init__(self):
        self.registry = ALL_OID_REGISTRY
    
    def get_all_oids(self, vendor: str = None) -> dict:
        """获取所有OID或指定厂商的OID"""
        if vendor and vendor in self.registry:
            return {vendor: self.registry[vendor]}
        return self.registry
    
    def get_oid_info(self, vendor: str, oid_name: str) -> dict:
        """获取单个OID的详细信息"""
        vendor_data = self.registry.get(vendor, {})
        for category in vendor_data.values():
            if isinstance(category, dict) and 'oids' in category:
                if oid_name in category['oids']:
                    return category['oids'][oid_name]
        return None
    
    def list_vendors(self) -> list:
        """列出所有支持的厂商"""
        return list(self.registry.keys())
    
    def search_oid(self, keyword: str) -> list:
        """搜索OID（按名称或描述）"""
        results = []
        for vendor_key, vendor_data in self.registry.items():
            # 处理两种结构
            if 'oids' in vendor_data:
                # 直接有oids
                for oid_name, oid_info in vendor_data['oids'].items():
                    if keyword.lower() in oid_name.lower() or \
                       keyword.lower() in oid_info.get('name', '').lower():
                        results.append({
                            'vendor': vendor_key,
                            'category': vendor_data.get('description', ''),
                            'oid_name': oid_name,
                            'oid': oid_info['oid'],
                            'name': oid_info['name'],
                            'type': oid_info.get('type', 'unknown'),
                        })
            else:
                for cat_key, category in vendor_data.items():
                    if isinstance(category, dict) and 'oids' in category:
                        for oid_name, oid_info in category['oids'].items():
                            if keyword.lower() in oid_name.lower() or \
                               keyword.lower() in oid_info.get('name', '').lower():
                                results.append({
                                    'vendor': vendor_key,
                                    'category': cat_key,
                                    'oid_name': oid_name,
                                    'oid': oid_info['oid'],
                                    'name': oid_info['name'],
                                    'type': oid_info.get('type', 'unknown'),
                                })
        return results
    
    def get_flat_oid_list(self, vendor: str = None) -> list:
        """获取平铺的OID列表"""
        flat_list = []
        vendors = [vendor] if vendor else list(self.registry.keys())
        for v in vendors:
            if v not in self.registry:
                continue
            vendor_data = self.registry[v]
            # 处理两种结构：有分类层级 和 直接有oids
            if 'oids' in vendor_data:
                # 直接有oids（如huawei, h3c, cisco等）
                for oid_name, oid_info in vendor_data['oids'].items():
                    flat_list.append({
                        'vendor': v,
                        'category': vendor_data.get('description', ''),
                        'oid_name': oid_name,
                        'oid': oid_info['oid'],
                        'name': oid_info['name'],
                        'type': oid_info.get('type', 'unknown'),
                        'table': oid_info.get('table', False),
                    })
            else:
                # 有分类层级（如standard, ucd_snmp等）
                for cat_key, category in vendor_data.items():
                    if isinstance(category, dict) and 'oids' in category:
                        for oid_name, oid_info in category['oids'].items():
                            flat_list.append({
                                'vendor': v,
                                'category': cat_key,
                                'oid_name': oid_name,
                                'oid': oid_info['oid'],
                                'name': oid_info['name'],
                                'type': oid_info.get('type', 'unknown'),
                                'table': oid_info.get('table', False),
                            })
        return flat_list
    
    def get_oids_by_category(self, vendor: str, category: str) -> dict:
        """按分类获取OID"""
        vendor_data = self.registry.get(vendor, {})
        return vendor_data.get(category, {}).get('oids', {})

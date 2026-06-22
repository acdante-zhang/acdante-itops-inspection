"""
Acdante ITOps - 设备巡检模板定义
定义各类设备的巡检表格结构和检查项
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class CheckItemDef:
    """巡检项定义"""
    name: str                    # 检查内容
    operation: str = ""          # 检查操作/命令
    result_hint: str = "正常 异常"  # 结果提示


@dataclass
class SectionDef:
    """巡检分区定义"""
    title: str
    section_type: str = "check"  # info / check / protocol / security / custom
    check_items: List[CheckItemDef] = field(default_factory=list)
    # 用于基本信息检查的字段 (key-value形式)
    info_fields: List[Tuple[str, str]] = field(default_factory=list)  # [(label, placeholder), ...]


# ============================================================
# 路由器巡检模板
# ============================================================
ROUTER_TEMPLATE = {
    "title": "路由器巡检报告",
    "sections": [
        SectionDef(
            title="基本信息检查",
            section_type="info",
            info_fields=[
                ("主机型号", ""),
                ("系统版本", ""),
                ("硬件配置", "模块"),
                ("", "接口数量"),
                ("", "电源数量"),
                ("", "设备运行环境"),
            ]
        ),
        SectionDef(
            title="设备运行状态检查",
            section_type="check",
            check_items=[
                CheckItemDef("设备指示灯", "目测指示灯有无红灯", "正常 异常"),
                CheckItemDef("设备运行时间检查", "判断并确认设备是否异常重启（dis ver/show ver）", "正常 异常"),
                CheckItemDef("当前及历史CPU使用率", "峰值≤70%，平时≤50%（dis cpu his/Show process cpu his）", "正常 异常"),
                CheckItemDef("内存使用率", "内存使用率≤70%（dis mem /Show mem sum）", "正常 异常"),
                CheckItemDef("风扇状态", "无报错（dis fan /Show env fan）", "正常 异常"),
                CheckItemDef("电源状态", "无报错（dis power /Show power）", "正常 异常"),
                CheckItemDef("模块温度", "模块温度≤45℃（dis env /show env temperature）", "正常 异常"),
                CheckItemDef("端口状态", "端口协商为全双工，100M/1000M链路，无大量错误报文（dis int/show int）", "正常 异常"),
                CheckItemDef("日志检查", "检查设备日志，查看有无异常报错信息（dis log/show log）", "正常 异常"),
                CheckItemDef("时钟检查", "检查设备时钟是否正确（dis clock/show clock）", "正常 异常"),
            ]
        ),
        SectionDef(
            title="常见协议检查",
            section_type="protocol",
            check_items=[
                CheckItemDef("VRRP/HSRP双机热备协议", "检查VRRP主备是否符合实际业务（dis standby /show standby brief）", "正常 异常"),
                CheckItemDef("RIP/OSPF/ISIS/BGP/静态路由", "检查路由协议邻居状态，有无冗余路由，有无错误路由条目", "正常 异常"),
                CheckItemDef("集群协议", "集群状态检查", "正常 异常"),
            ]
        ),
        SectionDef(
            title="系统安全检查",
            section_type="security",
            check_items=[
                CheckItemDef("远程登陆", "检查登陆方式、密码复杂度、限定登陆地址", "正常 异常"),
                CheckItemDef("SNMP", "是否使用了默认的团体字，是否指定了管理主机", "正常 异常"),
                CheckItemDef("日志服务器", "有无启用发送日志至日志服务器", "正常 异常"),
            ]
        ),
    ]
}

# ============================================================
# 交换机巡检模板
# ============================================================
SWITCH_TEMPLATE = {
    "title": "交换机巡检报告",
    "sections": [
        SectionDef(
            title="基本信息检查",
            section_type="info",
            info_fields=[
                ("主机型号", ""),
                ("系统版本", ""),
                ("硬件配置", "模块信息"),
                ("", "接口数量"),
                ("", "电源数量"),
                ("", "设备运行环境"),
            ]
        ),
        SectionDef(
            title="设备运行状态检查",
            section_type="check",
            check_items=[
                CheckItemDef("设备指示灯", "目测指示灯有无红灯", "正常 异常"),
                CheckItemDef("设备运行时间检查", "判断并确认设备是否异常重启（dis ver/show ver）", "正常 异常"),
                CheckItemDef("当前及历史CPU使用率", "峰值≤70%，平时≤50%（dis cpu his/Show process cpu his）", "正常 异常"),
                CheckItemDef("内存使用率", "内存使用率≤70%（dis mem /Show mem sum）", "正常 异常"),
                CheckItemDef("风扇状态", "无报错（dis fan /Show env fan）", "正常 异常"),
                CheckItemDef("电源状态", "无报错（dis power /Show power）", "正常 异常"),
                CheckItemDef("模块温度", "模块温度≤45℃（dis env /show env temperature）", "正常 异常"),
                CheckItemDef("端口状态", "端口协商为全双工，100M/1000M链路，无大量错误报文（dis int/show int）", "正常 异常"),
                CheckItemDef("日志检查", "检查设备日志，查看有无异常报错信息（dis log/show log）", "正常 异常"),
                CheckItemDef("时钟检查", "检查设备时钟是否正确（dis clock/show clock）", "正常 异常"),
            ]
        ),
        SectionDef(
            title="常见协议检查",
            section_type="protocol",
            check_items=[
                CheckItemDef("VRRP/HSRP双机热备协议", "检查VRRP主备是否符合实际业务（dis standby /show standby brief）", "正常 异常"),
                CheckItemDef("STP生成树协议", "检查生成树状态，根桥选举是否正确（dis stp brief/show spanning-tree brief）", "正常 异常"),
                CheckItemDef("OSPF/BGP路由协议", "检查路由协议邻居状态，有无错误路由条目", "正常 异常"),
                CheckItemDef("链路聚合", "检查链路聚合状态和负载均衡（dis link-aggregation/show etherchannel summary）", "正常 异常"),
                CheckItemDef("VLAN配置", "检查VLAN划分是否符合业务实际（dis vlan/show vlan brief）", "正常 异常"),
            ]
        ),
        SectionDef(
            title="系统安全检查",
            section_type="security",
            check_items=[
                CheckItemDef("远程登陆", "检查登陆方式、密码复杂度、限定登陆地址", "正常 异常"),
                CheckItemDef("SNMP", "是否使用了默认的团体字，是否指定了管理主机", "正常 异常"),
                CheckItemDef("日志服务器", "有无启用发送日志至日志服务器", "正常 异常"),
                CheckItemDef("ACL访问控制", "检查ACL规则是否符合业务实际", "正常 异常"),
            ]
        ),
    ]
}

# ============================================================
# 防火墙巡检模板
# ============================================================
FIREWALL_TEMPLATE = {
    "title": "防火墙设备巡检报告",
    "sections": [
        SectionDef(
            title="基本信息检查",
            section_type="info",
            info_fields=[
                ("主机型号", ""),
                ("序列号", ""),
                ("管理IP", ""),
                ("系统版本", ""),
                ("硬件配置", "接口数量"),
                ("", "电源数量"),
                ("", "设备运行环境"),
            ]
        ),
        SectionDef(
            title="设备运行状态检查",
            section_type="check",
            check_items=[
                CheckItemDef("设备面板指示灯状态检查", "观察面板指示灯看是否有红灯报警", "正常 异常"),
                CheckItemDef("设备性能状态检查", "查看设备CPU和内存利用率历史情况", "正常 异常"),
                CheckItemDef("设备端口状态检查", "查看设备接口状态信息及参数设置是否正常", "正常 异常"),
                CheckItemDef("设备会话信息检查", "查看设备会话数是否符合业务实际", "正常 异常"),
                CheckItemDef("设备端口流量检查", "查看设备端口流量历史是否正常，是否有突发和异常流量", "正常 异常"),
                CheckItemDef("设备访问控制规则检查", "检查设备状态检测包过滤规则是否符合业务实际、规则设置是否详细", "正常 异常"),
                CheckItemDef("设备地址转换NAT规则检查", "检查设备地址转换NAT规则是否符合业务实际、规则设置是否合理", "正常 异常"),
                CheckItemDef("设备系统及安全日志检查", "检查设备系统及安全日志是否有异常", "正常 异常"),
                CheckItemDef("设备双机热备状态检查", "检查双机热备状态是否符合业务实际", "正常 异常"),
            ]
        ),
    ]
}

# ============================================================
# 负载均衡巡检模板
# ============================================================
LOAD_BALANCER_TEMPLATE = {
    "title": "负载均衡设备巡检报告",
    "sections": [
        SectionDef(
            title="基本信息检查",
            section_type="info",
            info_fields=[
                ("主机型号", ""),
                ("管理IP", ""),
                ("系统版本", ""),
                ("硬件配置", "接口数量"),
                ("", "电源数量"),
                ("", "设备运行环境"),
            ]
        ),
        SectionDef(
            title="设备运行状态检查",
            section_type="check",
            check_items=[
                CheckItemDef("设备面板指示灯状态检查", "观察面板指示灯看是否有红灯报警", "正常 异常"),
                CheckItemDef("设备性能状态检查", "查看设备CPU和内存利用率", "正常 异常"),
                CheckItemDef("设备端口状态检查", "查看设备接口状态信息", "正常 异常"),
                CheckItemDef("负载均衡业务状态检查", "检查VS/VIP/Pool/Node状态", "正常 异常"),
                CheckItemDef("设备端口流量检查", "查看设备端口流量历史是否正常", "正常 异常"),
                CheckItemDef("SSL证书检查", "检查SSL证书有效期", "正常 异常"),
                CheckItemDef("设备系统日志检查", "检查设备系统日志是否有异常", "正常 异常"),
                CheckItemDef("设备双机热备状态检查", "检查双机热备状态是否符合业务实际", "正常 异常"),
            ]
        ),
    ]
}

# ============================================================
# IBM小型机巡检模板
# ============================================================
IBM_MINICOMPUTER_TEMPLATE = {
    "title": "IBM小型机巡检报告",
    "sections": [
        SectionDef(
            title="基本信息检查",
            section_type="info",
            info_fields=[
                ("主机型号", ""),
                ("序列号", ""),
                ("操作系统版本", ""),
                ("CPU/内存配置", ""),
                ("分区信息", ""),
            ]
        ),
        SectionDef(
            title="设备运行状态检查",
            section_type="check",
            check_items=[
                CheckItemDef("设备外观指示灯检查", "观察设备面板指示灯", "正常 异常"),
                CheckItemDef("HMC管理界面检查", "检查HMC连接状态及告警信息", "正常 异常"),
                CheckItemDef("CPU使用率检查", "CPU使用率≤70%（topas/nmon）", "正常 异常"),
                CheckItemDef("内存使用率检查", "内存使用率≤80%（svmon/vmstat）", "正常 异常"),
                CheckItemDef("文件系统使用率检查", "各文件系统使用率≤85%（df -g）", "正常 异常"),
                CheckItemDef("errpt错误日志检查", "检查errpt有无硬件或软件错误", "正常 异常"),
                CheckItemDef("网络接口状态检查", "检查网卡绑定状态和链路状态", "正常 异常"),
                CheckItemDef("电源和风扇状态检查", "检查电源和风扇冗余状态", "正常 异常"),
                CheckItemDef("系统日志检查", "检查syslog有无异常", "正常 异常"),
            ]
        ),
    ]
}

# ============================================================
# 刀片中心巡检模板
# ============================================================
BLADE_CENTER_TEMPLATE = {
    "title": "刀片中心巡检报告",
    "sections": [
        SectionDef(
            title="基本信息检查",
            section_type="info",
            info_fields=[
                ("设备型号", ""),
                ("序列号", ""),
            ]
        ),
        SectionDef(
            title="刀片中心硬件外观指示灯检查",
            section_type="check",
            check_items=[
                CheckItemDef("刀片中心外观", "是否清洁、整齐", "正常 异常"),
                CheckItemDef("刀片中心面板System Error指示灯", "观察System Error指示灯", "正常 异常"),
                CheckItemDef("刀片中心面板超温指示灯", "观察超温指示灯", "正常 异常"),
            ]
        ),
        SectionDef(
            title="刀片服务器状态",
            section_type="blade_slots",
            check_items=[]  # 动态生成
        ),
        SectionDef(
            title="刀片中心系统健康检查",
            section_type="check",
            check_items=[
                CheckItemDef("IO模块", "检查IO模块状态", "正常 异常"),
                CheckItemDef("MGT模块", "检查MGT管理模块状态", "正常 异常"),
                CheckItemDef("电源模块", "检查电源模块状态", "正常 异常"),
                CheckItemDef("电源风扇模块", "检查电源风扇状态", "正常 异常"),
                CheckItemDef("机箱风扇状态", "检查刀片机箱风扇模块状态", "正常 异常"),
                CheckItemDef("系统日志状态", "检查eventlog状态", "正常 异常"),
            ]
        ),
    ]
}

# ============================================================
# 存储设备巡检模板
# ============================================================
STORAGE_TEMPLATE = {
    "title": "存储设备巡检报告",
    "sections": [
        SectionDef(
            title="基本信息检查",
            section_type="info",
            info_fields=[
                ("设备型号", ""),
                ("序列号", ""),
                ("控制器", "MT型号"),
                ("硬盘", "类型/数量/热备"),
                ("连接方式", ""),
            ]
        ),
        SectionDef(
            title="设备运行状况",
            section_type="check_grid",  # 2列巡检结果网格
            check_items=[
                CheckItemDef("设备有无报警", ""),
                CheckItemDef("存储硬盘检查", ""),
                CheckItemDef("存储电源状态检查", ""),
                CheckItemDef("存储控制器检查", ""),
                CheckItemDef("存储通道状态检查", ""),
                CheckItemDef("存储日志检查", ""),
                CheckItemDef("存储RAID检查", ""),
                CheckItemDef("存储热备盘检查", ""),
                CheckItemDef("存储Lun使用率检查", ""),
                CheckItemDef("存储缓存检查", ""),
                CheckItemDef("外部线缆状态检查", ""),
                CheckItemDef("存储设备状态检查", ""),
            ]
        ),
    ]
}

# ============================================================
# SAN光交巡检模板
# ============================================================
SAN_SWITCH_TEMPLATE = {
    "title": "SAN交换机巡检报告",
    "sections": [
        SectionDef(
            title="基本信息检查",
            section_type="info",
            info_fields=[
                ("设备型号", ""),
                ("序列号", ""),
                ("固件版本", ""),
                ("端口数量", ""),
                ("管理IP", ""),
            ]
        ),
        SectionDef(
            title="设备运行状态检查",
            section_type="check",
            check_items=[
                CheckItemDef("设备指示灯检查", "观察设备面板指示灯", "正常 异常"),
                CheckItemDef("设备运行时间", "确认设备是否异常重启", "正常 异常"),
                CheckItemDef("端口状态检查", "检查所有端口状态，是否有errdown或异常", "正常 异常"),
                CheckItemDef("SFP模块状态", "检查SFP模块是否正常", "正常 异常"),
                CheckItemDef("Zoning配置检查", "检查Zoning配置是否符合业务实际", "正常 异常"),
                CheckItemDef("日志检查", "检查系统日志有无异常告警", "正常 异常"),
                CheckItemDef("电源和风扇检查", "检查电源和风扇状态", "正常 异常"),
            ]
        ),
    ]
}

# ============================================================
# VMware虚拟化巡检模板
# ============================================================
VMWARE_TEMPLATE = {
    "title": "Vmware虚拟化巡检报告",
    "sections": [
        SectionDef(
            title="基本信息检查",
            section_type="info",
            info_fields=[
                ("vCenter版本", ""),
                ("ESXi版本", ""),
                ("集群名称", ""),
                ("主机数量", ""),
                ("虚拟机数量", ""),
            ]
        ),
        SectionDef(
            title="集群运行状态检查",
            section_type="check",
            check_items=[
                CheckItemDef("vCenter服务状态", "检查vCenter各服务是否正常运行", "正常 异常"),
                CheckItemDef("ESXi主机状态", "检查所有ESXi主机连接状态", "正常 异常"),
                CheckItemDef("HA配置状态", "检查HA配置是否正确", "正常 异常"),
                CheckItemDef("DRS配置状态", "检查DRS配置和负载均衡", "正常 异常"),
                CheckItemDef("数据存储状态", "检查存储容量和性能", "正常 异常"),
                CheckItemDef("虚拟机状态", "检查虚拟机运行状态和资源使用", "正常 异常"),
                CheckItemDef("告警信息检查", "检查vCenter告警信息", "正常 异常"),
            ]
        ),
    ]
}

# ============================================================
# 备份系统巡检模板
# ============================================================
BACKUP_TEMPLATE = {
    "title": "备份系统巡检报告",
    "sections": [
        SectionDef(
            title="基本信息检查",
            section_type="info",
            info_fields=[
                ("备份软件", ""),
                ("服务器型号", ""),
                ("操作系统", ""),
                ("管理IP", ""),
            ]
        ),
        SectionDef(
            title="备份系统运行状态检查",
            section_type="check",
            check_items=[
                CheckItemDef("备份服务状态", "检查NetBackup服务是否正常运行", "正常 异常"),
                CheckItemDef("近期备份任务状态", "检查近期备份任务是否成功", "正常 异常"),
                CheckItemDef("存储单元状态", "检查磁带库/磁盘存储单元状态", "正常 异常"),
                CheckItemDef("磁带使用情况", "检查磁带使用率和过期情况", "正常 异常"),
                CheckItemDef("备份策略检查", "检查备份策略是否符合业务需求", "正常 异常"),
                CheckItemDef("日志检查", "检查系统日志有无异常", "正常 异常"),
            ]
        ),
    ]
}

# ============================================================
# 设备类型 -> 模板映射
# ============================================================
DEVICE_TYPE_TEMPLATE_MAP = {
    "router": ROUTER_TEMPLATE,
    "switch": SWITCH_TEMPLATE,
    "firewall": FIREWALL_TEMPLATE,
    "load_balancer": LOAD_BALANCER_TEMPLATE,
    "server": IBM_MINICOMPUTER_TEMPLATE,  # 服务器默认用IBM模板
    "storage": STORAGE_TEMPLATE,
    "san_switch": SAN_SWITCH_TEMPLATE,
    "vmware": VMWARE_TEMPLATE,
    "ibm_minicomputer": IBM_MINICOMPUTER_TEMPLATE,
    "blade_center": BLADE_CENTER_TEMPLATE,
    "backup": BACKUP_TEMPLATE,
    "ips": FIREWALL_TEMPLATE,  # IPS复用防火墙模板
    "waf": FIREWALL_TEMPLATE,  # WAF复用防火墙模板
    "vpn": FIREWALL_TEMPLATE,  # VPN复用防火墙模板
    "bastion": FIREWALL_TEMPLATE,  # 堡垒机复用防火墙模板
    "netgap": FIREWALL_TEMPLATE,  # 网闸复用防火墙模板
    "database": None,
    "other": None,
}


def get_template_for_device(device_type: str) -> dict:
    """获取设备类型对应的巡检模板"""
    return DEVICE_TYPE_TEMPLATE_MAP.get(device_type, ROUTER_TEMPLATE)


def get_template_title(device_type: str) -> str:
    """获取设备类型对应的巡检报告标题"""
    template = get_template_for_device(device_type)
    if template:
        return template["title"]
    return "设备巡检报告"

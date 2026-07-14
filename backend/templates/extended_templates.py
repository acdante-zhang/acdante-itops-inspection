"""
Acdante ITOps - 更多设备巡检模板
华为存储、F5负载均衡、Dell服务器、Windows等
"""

# ============================================================
# 华为存储巡检模板
# ============================================================

HUAWEI_STORAGE_TPL = {
    "id": "tpl-storage-huawei-v2",
    "name": "华为OceanStor存储巡检模板",
    "target_type": "storage",
    "brand": "华为",
    "version": "v2.0.0",
    "description": "华为OceanStor系列存储深度巡检，覆盖控制器、硬盘框、LUN、快照、复制等",
    "items": [
        {"id": "hw-st-01", "name": "存储系统状态", "category": "系统", "command": "show system general", "command_type": "ssh", "parser": "raw", "weight": 20, "order": 1},
        {"id": "hw-st-02", "name": "控制器状态", "category": "硬件", "command": "show controller general", "command_type": "ssh", "parser": "raw", "weight": 15, "order": 2},
        {"id": "hw-st-03", "name": "存储池使用率", "category": "存储", "command": "show storage_pool general", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, "weight": 20, "order": 3},
        {"id": "hw-st-04", "name": "LUN状态", "category": "存储", "command": "show lun general", "command_type": "ssh", "parser": "raw", "weight": 15, "order": 4},
        {"id": "hw-st-05", "name": "硬盘状态", "category": "硬件", "command": "show disk general", "command_type": "ssh", "parser": "raw", "weight": 15, "order": 5},
        {"id": "hw-st-06", "name": "电源状态", "category": "硬件", "command": "show power general", "command_type": "ssh", "parser": "raw", "weight": 10, "order": 6},
        {"id": "hw-st-07", "name": "风扇状态", "category": "硬件", "command": "show fan general", "command_type": "ssh", "parser": "raw", "weight": 10, "order": 7},
        {"id": "hw-st-08", "name": "告警信息", "category": "告警", "command": "show alarm general", "command_type": "ssh", "parser": "raw", "weight": 15, "order": 8},
    ],
}

# ============================================================
# F5负载均衡巡检模板
# ============================================================

F5_LB_TPL = {
    "id": "tpl-lb-f5-v2",
    "name": "F5 BIG-IP负载均衡巡检模板",
    "target_type": "network",
    "brand": "F5",
    "version": "v2.0.0",
    "description": "F5 BIG-IP负载均衡深度巡检，覆盖CPU、内存、连接、池、虚拟服务、证书等",
    "items": [
        {"id": "f5-01", "name": "系统版本", "category": "系统", "command": "tmsh show sys version", "command_type": "ssh", "parser": "raw", "weight": 5, "order": 1},
        {"id": "f5-02", "name": "CPU使用率", "category": "CPU", "command": "tmsh show sys cpu", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 70, "unit": "%"}, "weight": 20, "order": 2},
        {"id": "f5-03", "name": "内存使用率", "category": "内存", "command": "tmsh show sys memory", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, "weight": 20, "order": 3},
        {"id": "f5-04", "name": "活跃连接数", "category": "连接", "command": "tmsh show sys connection", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 500000, "warning": 250000, "unit": "连接"}, "weight": 15, "order": 4},
        {"id": "f5-05", "name": "池状态", "category": "池", "command": "tmsh show ltm pool", "command_type": "ssh", "parser": "raw", "weight": 20, "order": 5},
        {"id": "f5-06", "name": "虚拟服务状态", "category": "虚拟服务", "command": "tmsh show ltm virtual", "command_type": "ssh", "parser": "raw", "weight": 20, "order": 6},
        {"id": "f5-07", "name": "SSL证书状态", "category": "安全", "command": "tmsh show sys crypto cert", "command_type": "ssh", "parser": "raw", "weight": 10, "order": 7},
        {"id": "f5-08", "name": "接口状态", "category": "接口", "command": "tmsh show net interface", "command_type": "ssh", "parser": "raw", "weight": 10, "order": 8},
    ],
}

# ============================================================
# Dell iDRAC巡检模板（Redfish API）
# ============================================================

DELL_IDRAC_TPL = {
    "id": "tpl-bmc-dell-idrac-v2",
    "name": "Dell iDRAC Redfish巡检模板",
    "target_type": "bmc",
    "brand": "Dell",
    "version": "v2.0.0",
    "description": "Dell iDRAC BMC Redfish API巡检，覆盖系统、存储、散热、电源、SEL日志",
    "items": [
        {"id": "idrac-01", "name": "系统信息", "category": "系统", "command": "redfish:/redfish/v1/Systems/System.Embedded.1", "command_type": "http", "parser": "json", "weight": 10, "order": 1},
        {"id": "idrac-02", "name": "存储状态", "category": "存储", "command": "redfish:/redfish/v1/Systems/System.Embedded.1/Storage", "command_type": "http", "parser": "json", "weight": 15, "order": 2},
        {"id": "idrac-03", "name": "散热状态", "category": "硬件", "command": "redfish:/redfish/v1/Chassis/System.Embedded.1/Thermal", "command_type": "http", "parser": "json", "weight": 15, "order": 3},
        {"id": "idrac-04", "name": "电源状态", "category": "硬件", "command": "redfish:/redfish/v1/Chassis/System.Embedded.1/Power", "command_type": "http", "parser": "json", "weight": 15, "order": 4},
        {"id": "idrac-05", "name": "SEL日志", "category": "日志", "command": "redfish:/redfish/v1/Managers/iDRAC.Embedded.1/LogServices/Sel/Entries", "command_type": "http", "parser": "json", "weight": 10, "order": 5},
        {"id": "idrac-06", "name": "网络接口", "category": "网络", "command": "redfish:/redfish/v1/Managers/iDRAC.Embedded.1/EthernetInterfaces", "command_type": "http", "parser": "json", "weight": 10, "order": 6},
    ],
}

# ============================================================
# Windows服务器巡检模板
# ============================================================

WINDOWS_TPL = {
    "id": "tpl-windows-generic-v2",
    "name": "Windows Server通用巡检模板",
    "target_type": "windows",
    "brand": "Microsoft",
    "version": "v2.0.0",
    "description": "Windows Server通用巡检模板，支持PowerShell远程执行",
    "items": [
        {"id": "win-01", "name": "系统信息", "category": "系统", "command": "Get-ComputerInfo | Select-Object CsName, WindowsVersion, WindowsBuildLabEx | Format-List", "command_type": "ssh", "parser": "raw", "weight": 5, "order": 1},
        {"id": "win-02", "name": "CPU使用率", "category": "CPU", "command": "(Get-Counter '\\Processor(_Total)\\% Processor Time').CounterSamples.CookedValue", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 70, "unit": "%"}, "weight": 20, "order": 2},
        {"id": "win-03", "name": "内存使用率", "category": "内存", "command": "$os = Get-CimInstance Win32_OperatingSystem; [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory)/$os.TotalVisibleMemorySize*100,2)", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, "weight": 20, "order": 3},
        {"id": "win-04", "name": "磁盘使用率", "category": "磁盘", "command": "Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select-Object DeviceID, @{N='UsedPercent';E={[math]::Round(($_.Size-$_.FreeSpace)/$_.Size*100,1)}} | Format-Table -AutoSize", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, "weight": 20, "order": 4},
        {"id": "win-05", "name": "事件日志错误", "category": "安全", "command": "Get-EventLog -LogName System -EntryType Error -Newest 10 | Format-List TimeGenerated, Source, Message", "command_type": "ssh", "parser": "raw", "weight": 15, "order": 5},
        {"id": "win-06", "name": "自动服务状态", "category": "服务", "command": "Get-Service | Where-Object {$_.StartType -eq 'Automatic' -and $_.Status -ne 'Running'} | Format-Table Name, Status -AutoSize", "command_type": "ssh", "parser": "raw", "suggestion": "有自动启动的服务未运行，检查是否异常", "weight": 15, "order": 6},
        {"id": "win-07", "name": "系统运行时间", "category": "系统", "command": "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime", "command_type": "ssh", "parser": "raw", "weight": 5, "order": 7},
    ],
}

# ============================================================
# AIX服务器巡检模板
# ============================================================

AIX_TPL = {
    "id": "tpl-aix-generic-v2",
    "name": "AIX通用巡检模板",
    "target_type": "aix",
    "brand": "IBM",
    "version": "v2.0.0",
    "description": "IBM AIX操作系统深度巡检，覆盖CPU、内存、VG、文件系统、HACMP等",
    "items": [
        {"id": "aix-01", "name": "系统版本", "category": "系统", "command": "oslevel -s", "command_type": "ssh", "parser": "raw", "weight": 5, "order": 1},
        {"id": "aix-02", "name": "CPU使用率", "category": "CPU", "command": "vmstat 1 3 | tail -1 | awk '{print 100-$16}'", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 70, "unit": "%"}, "weight": 20, "order": 2},
        {"id": "aix-03", "name": "内存使用率", "category": "内存", "command": "svmon -G | head -2 | tail -1 | awk '{printf \"%.1f\", $3/$2*100}'", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, "weight": 20, "order": 3},
        {"id": "aix-04", "name": "文件系统使用率", "category": "磁盘", "command": "df -g | awk 'NR>1{print $7, $4}'", "command_type": "ssh", "parser": "raw", "threshold": {"operator": "gt", "critical": 90, "warning": 80, "unit": "%"}, "weight": 15, "order": 4},
        {"id": "aix-05", "name": "VG状态", "category": "存储", "command": "lsvg -o | xargs -I{} sh -c 'echo \"=== {} ===\"; lsvg {}'", "command_type": "ssh", "parser": "raw", "weight": 15, "order": 5},
        {"id": "aix-06", "name": "HACMP状态", "category": "集群", "command": "clstat 2>/dev/null || /usr/es/sbin/cluster/utilities/clRGinfo 2>/dev/null || echo 'HACMP not configured'", "command_type": "ssh", "parser": "raw", "weight": 15, "order": 6},
        {"id": "aix-07", "name": "Paging Space", "category": "内存", "command": "lsps -a", "command_type": "ssh", "parser": "raw", "weight": 10, "order": 7},
        {"id": "aix-08", "name": "网络接口", "category": "网络", "command": "entstat -d ent0 2>/dev/null | head -20 || ifconfig -a", "command_type": "ssh", "parser": "raw", "weight": 5, "order": 8},
    ],
}

# ============================================================
# 注册所有扩展模板
# ============================================================

EXTENDED_TEMPLATES = [
    HUAWEI_STORAGE_TPL,
    F5_LB_TPL,
    DELL_IDRAC_TPL,
    WINDOWS_TPL,
    AIX_TPL,
]


def get_extended_templates():
    return EXTENDED_TEMPLATES

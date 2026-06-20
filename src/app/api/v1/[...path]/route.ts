import { NextRequest, NextResponse } from 'next/server';

// ============================================================
// Mock Data Store — Acdante ITOps Inspection Platform
// ============================================================

const now = new Date();
const ago = (h: number) => new Date(now.getTime() - h * 3600000).toISOString();

// --- Targets ---
const targets = [
  { id: 1, name: "生产核心交换机-A", type: "network", brand: "华为", model: "CE12800", version: "V200R019C10", location: "A栋核心机房", connection_params: { protocol: "ssh", host: "10.0.1.1", port: 22, username: "netop", timeout: 30 }, offline_mode: false, status: "active", health_score: 92, last_inspection_at: ago(2), created_at: ago(720), updated_at: ago(1), tags: ["核心", "华为"] },
  { id: 2, name: "汇聚交换机-B3", type: "network", brand: "华三", model: "S12500", version: "R2606", location: "B栋汇聚机房", connection_params: { protocol: "ssh", host: "10.0.2.1", port: 22, username: "netop", timeout: 30 }, offline_mode: false, status: "active", health_score: 88, last_inspection_at: ago(3), created_at: ago(480), updated_at: ago(2), tags: ["汇聚", "华三"] },
  { id: 3, name: "ORACLE-PROD-DB1", type: "oracle", brand: "Oracle", model: "Database", version: "19c", location: "A栋数据库机房", connection_params: { protocol: "jdbc", host: "192.168.1.100", port: 1521, username: "monitor", database_name: "PRODDB", timeout: 30 }, offline_mode: false, status: "active", health_score: 75, last_inspection_at: ago(1), created_at: ago(960), updated_at: ago(0.5), tags: ["生产", "RAC"] },
  { id: 4, name: "ORACLE-TEST-DB2", type: "oracle", brand: "Oracle", model: "Database", version: "12c", location: "B栋数据库机房", connection_params: { protocol: "jdbc", host: "192.168.1.101", port: 1521, username: "monitor", database_name: "TESTDB", timeout: 30 }, offline_mode: false, status: "active", health_score: 95, last_inspection_at: ago(4), created_at: ago(720), updated_at: ago(1), tags: ["测试"] },
  { id: 5, name: "APP-SERVER-01", type: "linux", brand: "Dell", model: "PowerEdge R740", version: "RHEL 8.6", location: "A栋应用机房", connection_params: { protocol: "ssh", host: "192.168.2.10", port: 22, username: "root", timeout: 30 }, offline_mode: false, status: "active", health_score: 90, last_inspection_at: ago(0.5), created_at: ago(360), updated_at: ago(0.25), tags: ["应用", "RHEL"] },
  { id: 6, name: "APP-SERVER-02", type: "linux", brand: "联想", model: "ThinkSystem SR650", version: "Ubuntu 22.04", location: "A栋应用机房", connection_params: { protocol: "ssh", host: "192.168.2.11", port: 22, username: "root", timeout: 30 }, offline_mode: false, status: "active", health_score: 85, last_inspection_at: ago(1), created_at: ago(240), updated_at: ago(0.75), tags: ["应用", "Ubuntu"] },
  { id: 7, name: "WIN-FILE-SVR", type: "windows", brand: "HP", model: "ProLiant DL380", version: "Windows Server 2019", location: "B栋文件机房", connection_params: { protocol: "ssh", host: "192.168.3.10", port: 5985, username: "admin", timeout: 60 }, offline_mode: true, status: "active", health_score: 78, last_inspection_at: ago(24), created_at: ago(960), updated_at: ago(24), tags: ["文件服务", "Windows"] },
  { id: 8, name: "SAN-SWITCH-A", type: "san_switch", brand: "Brocade", model: "G630", version: "v9.2.1", location: "A栋存储机房", connection_params: { protocol: "ssh", host: "10.0.10.1", port: 22, username: "admin", timeout: 30 }, offline_mode: false, status: "active", health_score: 96, last_inspection_at: ago(6), created_at: ago(1440), updated_at: ago(6), tags: ["SAN", "Brocade"] },
  { id: 9, name: "STORAGE-V5000", type: "storage", brand: "华为", model: "OceanStor V5000", version: "V300R006", location: "A栋存储机房", connection_params: { protocol: "http", host: "10.0.10.100", port: 8088, username: "admin", timeout: 30 }, offline_mode: false, status: "active", health_score: 91, last_inspection_at: ago(8), created_at: ago(1440), updated_at: ago(8), tags: ["存储", "华为"] },
  { id: 10, name: "BMC-R740-01", type: "bmc", brand: "Dell", model: "iDRAC9", version: "6.10.80", location: "A栋应用机房", connection_params: { protocol: "redfish", host: "192.168.2.210", port: 443, username: "root", timeout: 30 }, offline_mode: false, status: "active", health_score: 98, last_inspection_at: ago(12), created_at: ago(720), updated_at: ago(12), tags: ["BMC", "iDRAC"] },
  { id: 11, name: "MySQL-PROD-01", type: "mysql", brand: "Oracle", model: "MySQL", version: "8.0.35", location: "B栋数据库机房", connection_params: { protocol: "jdbc", host: "192.168.1.200", port: 3306, username: "monitor", database_name: "production", timeout: 30 }, offline_mode: false, status: "active", health_score: 87, last_inspection_at: ago(2), created_at: ago(180), updated_at: ago(2), tags: ["生产", "MySQL"] },
  { id: 12, name: "AIX-ERP-SVR", type: "aix", brand: "IBM", model: "Power S924", version: "AIX 7.2 TL5", location: "C栋ERP机房", connection_params: { protocol: "ssh", host: "192.168.4.10", port: 22, username: "root", timeout: 60 }, offline_mode: false, status: "active", health_score: 82, last_inspection_at: ago(12), created_at: ago(2160), updated_at: ago(12), tags: ["ERP", "AIX"] },
  { id: 13, name: "FW-CORE-01", type: "network", brand: "华为", model: "USG6680E", version: "V600R006C20", location: "A栋核心机房", connection_params: { protocol: "ssh", host: "10.0.1.254", port: 22, username: "fwadmin", timeout: 30 }, offline_mode: false, status: "active", health_score: 94, last_inspection_at: ago(4), created_at: ago(960), updated_at: ago(4), tags: ["防火墙", "核心"] },
  { id: 14, name: "LB-F5-01", type: "network", brand: "F5", model: "BIG-IP i5800", version: "v17.1.0.2", location: "A栋核心机房", connection_params: { protocol: "ssh", host: "10.0.1.100", port: 22, username: "admin", timeout: 30 }, offline_mode: false, status: "active", health_score: 89, last_inspection_at: ago(3), created_at: ago(720), updated_at: ago(3), tags: ["负载均衡", "F5"] },
  { id: 15, name: "PG-PROD-01", type: "postgres", brand: "PostgreSQL", model: "PG", version: "15.4", location: "B栋数据库机房", connection_params: { protocol: "jdbc", host: "192.168.1.150", port: 5432, username: "monitor", database_name: "production", timeout: 30 }, offline_mode: false, status: "active", health_score: 93, last_inspection_at: ago(2), created_at: ago(120), updated_at: ago(2), tags: ["生产", "PostgreSQL"] },
];

let nextTargetId = 16;

// --- Templates ---
const templates = [
  {
    id: "tpl-linux-generic-v1", name: "Linux通用巡检模板", target_type: "linux", brand: "Generic", version: "v1.0.0", description: "适用于RHEL/CentOS/Ubuntu等主流Linux发行版的通用巡检模板", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "li-01", name: "系统运行时间", category: "系统信息", command: "uptime", command_type: "ssh", is_read_only: true, warning_text: "", parser: "raw", threshold: null, weight: 5, order: 1 },
      { id: "li-02", name: "CPU使用率", category: "CPU", command: "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'", command_type: "ssh", is_read_only: true, warning_text: "", parser: "regex", threshold: { metric: "cpu_usage", operator: "gt", critical: 90, warning: 70, unit: "%" }, suggestion: "检查占用CPU高的进程，考虑优化或扩容", weight: 20, order: 2 },
      { id: "li-03", name: "内存使用率", category: "内存", command: "free -m | awk 'NR==2{printf \"%.1f\", $3/$2*100}'", command_type: "ssh", is_read_only: true, warning_text: "", parser: "raw", threshold: { metric: "mem_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, suggestion: "检查内存占用高的进程，考虑增加内存或优化应用", weight: 20, order: 3 },
      { id: "li-04", name: "磁盘使用率", category: "磁盘", command: "df -h --type=ext4 --type=xfs --type=ext3 | awk 'NR>1{print $6, $5}'", command_type: "ssh", is_read_only: true, warning_text: "", parser: "raw", threshold: { metric: "disk_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, suggestion: "清理无用文件、扩容磁盘或归档旧数据", weight: 20, order: 4 },
      { id: "li-05", name: "磁盘Inode使用率", category: "磁盘", command: "df -i --type=ext4 --type=xfs | awk 'NR>1{print $6, $5}'", command_type: "ssh", is_read_only: true, warning_text: "", parser: "raw", threshold: { metric: "inode_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, suggestion: "删除小文件或调整文件系统", weight: 10, order: 5 },
      { id: "li-06", name: "系统负载", category: "CPU", command: "cat /proc/loadavg | awk '{print $1, $2, $3}'", command_type: "ssh", is_read_only: true, warning_text: "", parser: "raw", threshold: { metric: "load_avg", operator: "gt", critical: 16, warning: 8, unit: "" }, suggestion: "系统负载过高，检查CPU核心数和运行进程", weight: 15, order: 6 },
      { id: "li-07", name: "Swap使用率", category: "内存", command: "free -m | awk 'NR==3{printf \"%.1f\", $3/$2*100}'", command_type: "ssh", is_read_only: true, warning_text: "", parser: "raw", threshold: { metric: "swap_usage", operator: "gt", critical: 80, warning: 50, unit: "%" }, suggestion: "检查内存泄漏或增加物理内存", weight: 10, order: 7 },
      { id: "li-08", name: "网络连接状态", category: "网络", command: "ss -s", command_type: "ssh", is_read_only: true, warning_text: "", parser: "raw", weight: 5, order: 8 },
      { id: "li-09", name: "关键进程检查", category: "进程", command: "ps aux --sort=-%mem | head -20", command_type: "ssh", is_read_only: true, warning_text: "", parser: "raw", weight: 10, order: 9 },
      { id: "li-10", name: "系统日志错误", category: "安全", command: "journalctl -p err --since '24 hours ago' | tail -50", command_type: "ssh", is_read_only: true, warning_text: "", parser: "raw", weight: 15, order: 10 },
      { id: "li-11", name: "安全补丁状态", category: "安全", command: "yum check-update --security 2>/dev/null || apt list --upgradable 2>/dev/null | head -20", command_type: "ssh", is_read_only: true, warning_text: "", parser: "raw", weight: 5, order: 11 },
      { id: "li-12", name: "NTP时钟同步", category: "配置", command: "timedatectl status | grep -i sync || ntpq -p 2>/dev/null | head -5", command_type: "ssh", is_read_only: true, warning_text: "", parser: "raw", weight: 5, order: 12 },
    ]
  },
  {
    id: "tpl-oracle-19c-v1", name: "Oracle 19c巡检模板", target_type: "oracle", brand: "Oracle", version: "v1.0.0", description: "Oracle 19c数据库健康巡检，包含实例状态、表空间、性能指标、安全配置等", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "oi-01", name: "数据库实例状态", category: "实例", command: "SELECT STATUS, DATABASE_STATUS FROM V$INSTANCE", command_type: "sql", is_read_only: true, warning_text: "", parser: "raw", weight: 20, order: 1 },
      { id: "oi-02", name: "表空间使用率", category: "存储", command: "SELECT TABLESPACE_NAME, ROUND(USED_PCT,2) FROM DBA_TABLESPACE_USAGE_METRICS", command_type: "sql", is_read_only: true, warning_text: "", parser: "raw", threshold: { metric: "tbs_usage", operator: "gt", critical: 95, warning: 85, unit: "%" }, suggestion: "扩容表空间或清理历史数据", weight: 20, order: 2 },
      { id: "oi-03", name: "SGA/PGA使用率", category: "内存", command: "SELECT NAME, ROUND(VALUE/1024/1024,2) SIZE_MB FROM V$SGAINFO", command_type: "sql", is_read_only: true, warning_text: "", parser: "raw", weight: 10, order: 3 },
      { id: "oi-04", name: "活跃会话数", category: "会话", command: "SELECT COUNT(*) FROM V$SESSION WHERE STATUS='ACTIVE'", command_type: "sql", is_read_only: true, warning_text: "", parser: "raw", threshold: { metric: "active_sessions", operator: "gt", critical: 500, warning: 300, unit: "" }, weight: 15, order: 4 },
      { id: "oi-05", name: "锁阻塞检测", category: "锁", command: "SELECT BLOCKING_SESSION, COUNT(*) FROM V$SESSION WHERE BLOCKING_SESSION IS NOT NULL GROUP BY BLOCKING_SESSION", command_type: "sql", is_read_only: true, warning_text: "", parser: "raw", weight: 20, order: 5 },
      { id: "oi-06", name: "RMAN备份状态", category: "备份", command: "SELECT STATUS, START_TIME, END_TIME FROM V$RMAN_BACKUP_JOB_DETAILS WHERE START_TIME > SYSDATE-7", command_type: "sql", is_read_only: true, warning_text: "", parser: "raw", weight: 15, order: 6 },
      { id: "oi-07", name: "归档日志空间", category: "存储", command: "SELECT NAME, SPACE_LIMIT/1024/1024/1024 LIMIT_GB, SPACE_USED/1024/1024/1024 USED_GB FROM V$RECOVERY_FILE_DEST", command_type: "sql", is_read_only: true, warning_text: "", parser: "raw", threshold: { metric: "arch_usage", operator: "gt", critical: 90, warning: 75, unit: "%" }, weight: 10, order: 7 },
      { id: "oi-08", name: "无效对象检查", category: "对象", command: "SELECT OWNER, OBJECT_TYPE, COUNT(*) FROM DBA_OBJECTS WHERE STATUS='INVALID' GROUP BY OWNER, OBJECT_TYPE", command_type: "sql", is_read_only: true, warning_text: "", parser: "raw", weight: 5, order: 8 },
    ]
  },
  {
    id: "tpl-oracle-11g-v1", name: "Oracle 11g巡检模板", target_type: "oracle", brand: "Oracle", version: "v1.0.0", description: "Oracle 11g数据库巡检模板，参考DBCheck巡检脚本", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "o11g-01", name: "数据库基本信息", category: "实例", command: "SELECT d.DBID, d.NAME, d.DATABASE_ROLE FROM V$DATABASE d, V$INSTANCE i", command_type: "sql", is_read_only: true, parser: "raw", weight: 10, order: 1 },
      { id: "o11g-02", name: "表空间使用率", category: "存储", command: "SELECT TABLESPACE_NAME, ROUND((1-NVL(FREE_BYTES,0)/TOTAL_BYTES)*100,2) FROM DBA_TABLESPACE_USAGE", command_type: "sql", is_read_only: true, parser: "raw", threshold: { metric: "tbs_usage", operator: "gt", critical: 95, warning: 85, unit: "%" }, weight: 20, order: 2 },
      { id: "o11g-03", name: "SGA统计", category: "内存", command: "SELECT NAME, VALUE/1024/1024 SIZE_MB FROM V$SGA", command_type: "sql", is_read_only: true, parser: "raw", weight: 10, order: 3 },
      { id: "o11g-04", name: "TOP 10 SQL", category: "性能", command: "SELECT SQL_ID, EXECUTIONS, ELAPSED_TIME/1000000 ELAPSED_SEC FROM V$SQLAREA ORDER BY ELAPSED_TIME DESC WHERE ROWNUM<=10", command_type: "sql", is_read_only: true, parser: "raw", weight: 10, order: 4 },
      { id: "o11g-05", name: "备份状态", category: "备份", command: "SELECT * FROM V$RMAN_BACKUP_JOB_DETAILS ORDER BY START_TIME DESC WHERE ROWNUM<=5", command_type: "sql", is_read_only: true, parser: "raw", weight: 15, order: 5 },
    ]
  },
  {
    id: "tpl-oracle-12c-v1", name: "Oracle 12c巡检模板", target_type: "oracle", brand: "Oracle", version: "v1.0.0", description: "Oracle 12c数据库巡检模板，支持CDB/PDB架构", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "o12c-01", name: "CDB/PDB状态", category: "实例", command: "SELECT CON_ID, NAME, OPEN_MODE FROM V$PDBS", command_type: "sql", is_read_only: true, parser: "raw", weight: 20, order: 1 },
      { id: "o12c-02", name: "表空间使用率", category: "存储", command: "SELECT CON_ID, TABLESPACE_NAME, ROUND(USED_PCT,2) FROM CDB_TABLESPACE_USAGE_METRICS", command_type: "sql", is_read_only: true, parser: "raw", threshold: { metric: "tbs_usage", operator: "gt", critical: 95, warning: 85, unit: "%" }, weight: 20, order: 2 },
      { id: "o12c-03", name: "AWR性能概览", category: "性能", command: "SELECT SNAP_ID, BEGIN_INTERVAL_TIME FROM DBA_HIST_SNAPSHOT ORDER BY SNAP_ID DESC FETCH FIRST 5 ROWS ONLY", command_type: "sql", is_read_only: true, parser: "raw", weight: 10, order: 3 },
    ]
  },
  {
    id: "tpl-network-huawei-v1", name: "华为网络设备巡检模板", target_type: "network", brand: "华为", version: "v1.0.0", description: "华为交换机/路由器/防火墙通用巡检模板", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "hw-01", name: "设备版本信息", category: "系统", command: "display version", command_type: "ssh", is_read_only: true, parser: "raw", weight: 5, order: 1 },
      { id: "hw-02", name: "CPU使用率", category: "CPU", command: "display cpu-usage", command_type: "ssh", is_read_only: true, parser: "regex", threshold: { metric: "cpu_usage", operator: "gt", critical: 90, warning: 70, unit: "%" }, suggestion: "检查异常进程或流量", weight: 20, order: 2 },
      { id: "hw-03", name: "内存使用率", category: "内存", command: "display memory-usage", command_type: "ssh", is_read_only: true, parser: "regex", threshold: { metric: "mem_usage", operator: "gt", critical: 85, warning: 70, unit: "%" }, weight: 20, order: 3 },
      { id: "hw-04", name: "接口状态", category: "接口", command: "display interface brief", command_type: "ssh", is_read_only: true, parser: "raw", weight: 15, order: 4 },
      { id: "hw-05", name: "告警信息", category: "告警", command: "display alarm active all", command_type: "ssh", is_read_only: true, parser: "raw", weight: 15, order: 5 },
      { id: "hw-06", name: "日志缓冲", category: "日志", command: "display logbuffer reverse", command_type: "ssh", is_read_only: true, parser: "raw", weight: 10, order: 6 },
      { id: "hw-07", name: "路由表摘要", category: "路由", command: "display ip routing-table statistics", command_type: "ssh", is_read_only: true, parser: "raw", weight: 5, order: 7 },
      { id: "hw-08", name: "风扇状态", category: "硬件", command: "display device fan", command_type: "ssh", is_read_only: true, parser: "raw", weight: 5, order: 8 },
      { id: "hw-09", name: "电源状态", category: "硬件", command: "display device power", command_type: "ssh", is_read_only: true, parser: "raw", weight: 5, order: 9 },
      { id: "hw-10", name: "温度信息", category: "硬件", command: "display device temperature", command_type: "ssh", is_read_only: true, parser: "raw", threshold: { metric: "temperature", operator: "gt", critical: 70, warning: 60, unit: "°C" }, weight: 5, order: 10 },
    ]
  },
  {
    id: "tpl-network-h3c-v1", name: "华三网络设备巡检模板", target_type: "network", brand: "华三", version: "v1.0.0", description: "华三交换机/路由器通用巡检模板", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "h3c-01", name: "设备版本", category: "系统", command: "display version", command_type: "ssh", is_read_only: true, parser: "raw", weight: 5, order: 1 },
      { id: "h3c-02", name: "CPU使用率", category: "CPU", command: "display cpu-usage", command_type: "ssh", is_read_only: true, parser: "raw", threshold: { metric: "cpu_usage", operator: "gt", critical: 90, warning: 70, unit: "%" }, weight: 20, order: 2 },
      { id: "h3c-03", name: "内存使用率", category: "内存", command: "display memory", command_type: "ssh", is_read_only: true, parser: "raw", threshold: { metric: "mem_usage", operator: "gt", critical: 85, warning: 70, unit: "%" }, weight: 20, order: 3 },
      { id: "h3c-04", name: "接口状态", category: "接口", command: "display interface brief", command_type: "ssh", is_read_only: true, parser: "raw", weight: 15, order: 4 },
      { id: "h3c-05", name: "告警信息", category: "告警", command: "display alarm", command_type: "ssh", is_read_only: true, parser: "raw", weight: 15, order: 5 },
    ]
  },
  {
    id: "tpl-san-brocade-v1", name: "Brocade SAN交换机巡检模板", target_type: "san_switch", brand: "Brocade", version: "v1.0.0", description: "Brocade光纤交换机健康巡检模板", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "br-01", name: "交换机状态", category: "系统", command: "switchshow", command_type: "ssh", is_read_only: true, parser: "raw", weight: 10, order: 1 },
      { id: "br-02", name: "端口状态", category: "端口", command: "portshow", command_type: "ssh", is_read_only: true, parser: "raw", weight: 15, order: 2 },
      { id: "br-03", name: "SFP信息", category: "硬件", command: "sfpshow all", command_type: "ssh", is_read_only: true, parser: "raw", weight: 10, order: 3 },
      { id: "br-04", name: "错误统计", category: "错误", command: "porterrshow", command_type: "ssh", is_read_only: true, parser: "raw", weight: 20, order: 4 },
      { id: "br-05", name: "固件版本", category: "系统", command: "firmwaredownload --show", command_type: "ssh", is_read_only: true, parser: "raw", weight: 5, order: 5 },
    ]
  },
  {
    id: "tpl-storage-huawei-v1", name: "华为存储巡检模板", target_type: "storage", brand: "华为", version: "v1.0.0", description: "华为OceanStor系列存储巡检模板", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "st-hw-01", name: "存储系统状态", category: "系统", command: "show system general", command_type: "ssh", is_read_only: true, parser: "raw", weight: 15, order: 1 },
      { id: "st-hw-02", name: "存储池使用率", category: "存储", command: "show storage_pool general", command_type: "ssh", is_read_only: true, parser: "raw", threshold: { metric: "pool_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, weight: 20, order: 2 },
      { id: "st-hw-03", name: "LUN状态", category: "存储", command: "show lun general", command_type: "ssh", is_read_only: true, parser: "raw", weight: 15, order: 3 },
      { id: "st-hw-04", name: "硬盘状态", category: "硬件", command: "show disk general", command_type: "ssh", is_read_only: true, parser: "raw", weight: 15, order: 4 },
      { id: "st-hw-05", name: "控制器状态", category: "硬件", command: "show controller general", command_type: "ssh", is_read_only: true, parser: "raw", weight: 10, order: 5 },
    ]
  },
  {
    id: "tpl-windows-generic-v1", name: "Windows通用巡检模板", target_type: "windows", brand: "Microsoft", version: "v1.0.0", description: "Windows Server通用巡检模板，支持离线采集模式", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "win-01", name: "系统信息", category: "系统", command: "Get-ComputerInfo | Select-Object CsName, WindowsVersion", command_type: "script", is_read_only: true, parser: "raw", weight: 5, order: 1 },
      { id: "win-02", name: "CPU使用率", category: "CPU", command: "Get-Counter '\\Processor(_Total)\\% Processor Time'", command_type: "script", is_read_only: true, parser: "raw", threshold: { metric: "cpu_usage", operator: "gt", critical: 90, warning: 70, unit: "%" }, weight: 20, order: 2 },
      { id: "win-03", name: "内存使用率", category: "内存", command: "$os = Get-CimInstance Win32_OperatingSystem; [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory)/$os.TotalVisibleMemorySize*100,2)", command_type: "script", is_read_only: true, parser: "raw", threshold: { metric: "mem_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, weight: 20, order: 3 },
      { id: "win-04", name: "磁盘使用率", category: "磁盘", command: "Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3'", command_type: "script", is_read_only: true, parser: "raw", threshold: { metric: "disk_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, weight: 20, order: 4 },
      { id: "win-05", name: "事件日志错误", category: "安全", command: "Get-EventLog -LogName System -EntryType Error -Newest 20", command_type: "script", is_read_only: true, parser: "raw", weight: 15, order: 5 },
      { id: "win-06", name: "服务状态", category: "服务", command: "Get-Service | Where-Object {$_.StartType -eq 'Automatic' -and $_.Status -ne 'Running'}", command_type: "script", is_read_only: true, parser: "raw", weight: 10, order: 6 },
    ]
  },
  {
    id: "tpl-bmc-dell-idrac-v1", name: "Dell iDRAC巡检模板", target_type: "bmc", brand: "Dell", version: "v1.0.0", description: "Dell iDRAC BMC巡检模板（Redfish API）", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "idrac-01", name: "系统信息", category: "系统", command: "/redfish/v1/Systems/System.Embedded.1", command_type: "http", is_read_only: true, parser: "jsonpath", weight: 5, order: 1 },
      { id: "idrac-02", name: "硬盘状态", category: "存储", command: "/redfish/v1/Systems/System.Embedded.1/Storage", command_type: "http", is_read_only: true, parser: "jsonpath", weight: 15, order: 2 },
      { id: "idrac-03", name: "风扇状态", category: "硬件", command: "/redfish/v1/Chassis/System.Embedded.1/Thermal", command_type: "http", is_read_only: true, parser: "jsonpath", weight: 10, order: 3 },
      { id: "idrac-04", name: "电源状态", category: "硬件", command: "/redfish/v1/Chassis/System.Embedded.1/Power", command_type: "http", is_read_only: true, parser: "jsonpath", weight: 10, order: 4 },
      { id: "idrac-05", name: "SEL日志", category: "日志", command: "/redfish/v1/Managers/iDRAC.Embedded.1/LogServices/Sel/Entries", command_type: "http", is_read_only: true, parser: "jsonpath", weight: 10, order: 5 },
    ]
  },
  {
    id: "tpl-aix-generic-v1", name: "AIX通用巡检模板", target_type: "aix", brand: "IBM", version: "v1.0.0", description: "IBM AIX操作系统巡检模板", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "aix-01", name: "系统版本", category: "系统", command: "oslevel -s", command_type: "ssh", is_read_only: true, parser: "raw", weight: 5, order: 1 },
      { id: "aix-02", name: "CPU使用率", category: "CPU", command: "vmstat 1 3 | tail -1 | awk '{print 100-$16}'", command_type: "ssh", is_read_only: true, parser: "raw", threshold: { metric: "cpu_usage", operator: "gt", critical: 90, warning: 70, unit: "%" }, weight: 20, order: 2 },
      { id: "aix-03", name: "内存使用率", category: "内存", command: "svmon -G | head -2 | tail -1 | awk '{printf \"%.1f\", $3/$2*100}'", command_type: "ssh", is_read_only: true, parser: "raw", weight: 20, order: 3 },
      { id: "aix-04", name: "文件系统使用率", category: "磁盘", command: "df -g | awk 'NR>1{print $7, $4}'", command_type: "ssh", is_read_only: true, parser: "raw", threshold: { metric: "fs_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, weight: 15, order: 4 },
      { id: "aix-05", name: "VG状态", category: "存储", command: "lsvg -o | xargs -I{} lsvg {}", command_type: "ssh", is_read_only: true, parser: "raw", weight: 10, order: 5 },
      { id: "aix-06", name: "HACMP状态", category: "集群", command: "clstat 2>/dev/null || echo 'HACMP not configured'", command_type: "ssh", is_read_only: true, parser: "raw", weight: 10, order: 6 },
    ]
  },
  {
    id: "tpl-mysql-8-v1", name: "MySQL 8.0巡检模板", target_type: "mysql", brand: "Oracle", version: "v1.0.0", description: "MySQL 8.0数据库巡检模板", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "my8-01", name: "实例状态", category: "实例", command: "SHOW GLOBAL STATUS LIKE 'Threads_connected'; SHOW GLOBAL STATUS LIKE 'Threads_running'", command_type: "sql", is_read_only: true, parser: "raw", weight: 15, order: 1 },
      { id: "my8-02", name: "InnoDB缓冲池", category: "内存", command: "SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool%'", command_type: "sql", is_read_only: true, parser: "raw", weight: 15, order: 2 },
      { id: "my8-03", name: "慢查询统计", category: "性能", command: "SHOW GLOBAL STATUS LIKE 'Slow_queries'", command_type: "sql", is_read_only: true, parser: "raw", weight: 15, order: 3 },
      { id: "my8-04", name: "主从复制状态", category: "复制", command: "SHOW SLAVE STATUS\\G", command_type: "sql", is_read_only: true, parser: "raw", weight: 20, order: 4 },
      { id: "my8-05", name: "连接数", category: "连接", command: "SHOW VARIABLES LIKE 'max_connections'; SHOW GLOBAL STATUS LIKE 'Max_used_connections'", command_type: "sql", is_read_only: true, parser: "raw", threshold: { metric: "conn_usage", operator: "gt", critical: 90, warning: 75, unit: "%" }, weight: 15, order: 5 },
    ]
  },
  {
    id: "tpl-pg-15-v1", name: "PostgreSQL 15巡检模板", target_type: "postgres", brand: "PostgreSQL", version: "v1.0.0", description: "PostgreSQL 15数据库巡检模板", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "pg-01", name: "连接数", category: "连接", command: "SELECT count(*) FROM pg_stat_activity; SHOW max_connections", command_type: "sql", is_read_only: true, parser: "raw", weight: 15, order: 1 },
      { id: "pg-02", name: "数据库大小", category: "存储", command: "SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database WHERE datistemplate = false", command_type: "sql", is_read_only: true, parser: "raw", weight: 15, order: 2 },
      { id: "pg-03", name: "复制状态", category: "复制", command: "SELECT * FROM pg_stat_replication", command_type: "sql", is_read_only: true, parser: "raw", weight: 15, order: 3 },
      { id: "pg-04", name: "死锁检查", category: "锁", command: "SELECT * FROM pg_locks WHERE NOT granted", command_type: "sql", is_read_only: true, parser: "raw", weight: 20, order: 4 },
    ]
  },
];

// --- Tasks ---
const tasks = [
  { id: "task-001", name: "每日核心网络巡检", template_id: "tpl-network-huawei-v1", target_ids: [1, 13, 14], schedule_type: "daily", status: "completed", last_run_at: ago(2), next_run_at: ago(-22), notify_email: ["ops@company.com"], created_by: "admin", created_at: ago(720), updated_at: ago(2) },
  { id: "task-002", name: "Oracle生产库巡检", template_id: "tpl-oracle-19c-v1", target_ids: [3], schedule_type: "hourly", status: "completed", last_run_at: ago(1), next_run_at: ago(-0), notify_email: ["dba@company.com"], created_by: "admin", created_at: ago(480), updated_at: ago(1) },
  { id: "task-003", name: "Linux服务器周巡检", template_id: "tpl-linux-generic-v1", target_ids: [5, 6], schedule_type: "weekly", status: "completed", last_run_at: ago(48), next_run_at: ago(-120), created_by: "engineer", created_at: ago(240), updated_at: ago(48) },
  { id: "task-004", name: "存储设备月巡检", template_id: "tpl-storage-huawei-v1", target_ids: [9], schedule_type: "monthly", status: "pending", next_run_at: ago(-168), created_by: "admin", created_at: ago(720), updated_at: ago(720) },
  { id: "task-005", name: "SAN交换机巡检", template_id: "tpl-san-brocade-v1", target_ids: [8], schedule_type: "daily", status: "running", last_run_at: ago(0.08), created_by: "engineer", created_at: ago(360), updated_at: ago(0.08) },
  { id: "task-006", name: "MySQL数据库巡检", template_id: "tpl-mysql-8-v1", target_ids: [11], schedule_type: "daily", status: "completed", last_run_at: ago(3), next_run_at: ago(-21), created_by: "admin", created_at: ago(180), updated_at: ago(3) },
];

let nextTaskNum = 7;

// --- Results ---
const results = [
  { id: 1, task_id: "task-001", target_id: 1, target_name: "生产核心交换机-A", item_id: "hw-01", item_name: "设备版本信息", category: "系统", raw_value: "Huawei CE12800 V200R019C10", parsed_value: "CE12800 V200R019C10", status: "ok", threshold: "", suggestion: "", executed_at: ago(2), duration_ms: 230 },
  { id: 2, task_id: "task-001", target_id: 1, target_name: "生产核心交换机-A", item_id: "hw-02", item_name: "CPU使用率", category: "CPU", raw_value: "15%", parsed_value: 15, status: "ok", threshold: "警告>70% 严重>90%", suggestion: "", executed_at: ago(2), duration_ms: 180 },
  { id: 3, task_id: "task-001", target_id: 1, target_name: "生产核心交换机-A", item_id: "hw-03", item_name: "内存使用率", category: "内存", raw_value: "62%", parsed_value: 62, status: "ok", threshold: "警告>70% 严重>85%", suggestion: "", executed_at: ago(2), duration_ms: 190 },
  { id: 4, task_id: "task-002", target_id: 3, target_name: "ORACLE-PROD-DB1", item_id: "oi-01", item_name: "数据库实例状态", category: "实例", raw_value: "STATUS=OPEN, DATABASE_STATUS=ACTIVE", parsed_value: "OPEN/ACTIVE", status: "ok", threshold: "", suggestion: "", executed_at: ago(1), duration_ms: 450 },
  { id: 5, task_id: "task-002", target_id: 3, target_name: "ORACLE-PROD-DB1", item_id: "oi-02", item_name: "表空间使用率", category: "存储", raw_value: "USERS: 92.5%, SYSAUX: 78.3%, SYSTEM: 65.1%", parsed_value: "USERS=92.5%", status: "warning", threshold: "警告>85% 严重>95%", suggestion: "USERS表空间使用率偏高，建议扩容或清理数据", executed_at: ago(1), duration_ms: 680 },
  { id: 6, task_id: "task-002", target_id: 3, target_name: "ORACLE-PROD-DB1", item_id: "oi-05", item_name: "锁阻塞检测", category: "锁", raw_value: "SID 156 阻塞 3 个会话，持锁时间 600s", parsed_value: "1个阻塞源", status: "critical", threshold: ">0 即告警", suggestion: "检查SID 156会话是否正常，必要时Kill该会话", executed_at: ago(1), duration_ms: 520 },
  { id: 7, task_id: "task-003", target_id: 5, target_name: "APP-SERVER-01", item_id: "li-02", item_name: "CPU使用率", category: "CPU", raw_value: "45.2%", parsed_value: 45.2, status: "ok", threshold: "警告>70% 严重>90%", suggestion: "", executed_at: ago(48), duration_ms: 310 },
  { id: 8, task_id: "task-003", target_id: 5, target_name: "APP-SERVER-01", item_id: "li-04", item_name: "磁盘使用率", category: "磁盘", raw_value: "/ 85%, /data 91%, /log 72%", parsed_value: "/data=91%", status: "warning", threshold: "警告>80% 严重>90%", suggestion: "/data分区使用率91%，建议清理或扩容", executed_at: ago(48), duration_ms: 290 },
  { id: 9, task_id: "task-003", target_id: 6, target_name: "APP-SERVER-02", item_id: "li-03", item_name: "内存使用率", category: "内存", raw_value: "87.3%", parsed_value: 87.3, status: "warning", threshold: "警告>80% 严重>90%", suggestion: "内存使用率偏高，检查内存泄漏", executed_at: ago(48), duration_ms: 280 },
  { id: 10, task_id: "task-006", target_id: 11, target_name: "MySQL-PROD-01", item_id: "my8-04", item_name: "主从复制状态", category: "复制", raw_value: "Slave_IO=Yes, Slave_SQL=Yes, Seconds_Behind=0", parsed_value: "正常,延迟0s", status: "ok", threshold: "", suggestion: "", executed_at: ago(3), duration_ms: 420 },
];

// --- Reports ---
const reports = [
  { id: "rpt-001", task_id: "task-001", task_name: "每日核心网络巡检", target_ids: [1, 13, 14], format: "html", health_score: 92, total_items: 30, ok_count: 27, warning_count: 2, critical_count: 1, summary: "核心网络设备整体健康，防火墙CPU使用率偏高需关注", generated_at: ago(2), download_url: "/api/v1/reports/rpt-001/download?format=html" },
  { id: "rpt-002", task_id: "task-002", task_name: "Oracle生产库巡检", target_ids: [3], format: "html", health_score: 75, total_items: 8, ok_count: 5, warning_count: 1, critical_count: 2, summary: "ORACLE-PROD-DB1存在锁阻塞和表空间使用率告警，需紧急处理", generated_at: ago(1), download_url: "/api/v1/reports/rpt-002/download?format=html" },
  { id: "rpt-003", task_id: "task-003", task_name: "Linux服务器周巡检", target_ids: [5, 6], format: "html", health_score: 85, total_items: 24, ok_count: 20, warning_count: 3, critical_count: 1, summary: "服务器整体健康，APP-SERVER-01磁盘使用率需关注", generated_at: ago(48), download_url: "/api/v1/reports/rpt-003/download?format=html" },
  { id: "rpt-004", task_id: "task-006", task_name: "MySQL数据库巡检", target_ids: [11], format: "html", health_score: 87, total_items: 5, ok_count: 4, warning_count: 1, critical_count: 0, summary: "MySQL主从复制正常，慢查询数略有上升", generated_at: ago(3), download_url: "/api/v1/reports/rpt-004/download?format=html" },
];

// --- Knowledge ---
const knowledge = [
  { id: "kb-001", title: "Oracle锁阻塞排查指南", category: "数据库", target_type: "oracle", symptom: "会话等待enq: TX - row lock contention，业务响应缓慢", cause: "一个会话持有行锁未释放，阻塞其他会话的DML操作", solution: "1. 查询V$SESSION定位阻塞源会话\n2. 与业务确认是否可以Kill\n3. ALTER SYSTEM KILL SESSION 'sid,serial#' IMMEDIATE\n4. 优化应用逻辑，避免长事务", reference: "https://docs.oracle.com/en/database/oracle/oracle-database/19/cncpt/locks.html", severity: "critical", tags: ["Oracle", "锁", "性能"] },
  { id: "kb-002", title: "Linux磁盘使用率告警处理", category: "操作系统", target_type: "linux", symptom: "磁盘使用率超过80%告警阈值", cause: "日志文件过大、临时文件未清理、数据增长过快", solution: "1. du -sh /* | sort -rh 定位大目录\n2. 清理旧日志\n3. 清理临时文件\n4. 归档历史数据\n5. 必要时扩展磁盘容量", severity: "warning", tags: ["Linux", "磁盘"] },
  { id: "kb-003", title: "网络设备CPU使用率过高", category: "网络设备", target_type: "network", symptom: "交换机/路由器CPU使用率持续超过70%", cause: "路由表过大、ACL规则过多、广播风暴、硬件转发异常", solution: "1. 检查CPU占用最高的进程\n2. 检查路由表规模\n3. 优化ACL规则\n4. 检查是否有环路\n5. 确认硬件转发正常", severity: "warning", tags: ["网络", "CPU"] },
  { id: "kb-004", title: "Oracle表空间不足处理", category: "数据库", target_type: "oracle", symptom: "表空间使用率超过85%", cause: "数据增长过快、未设置自动扩展、碎片率高", solution: "1. ALTER TABLESPACE xxx ADD DATAFILE\n2. 开启AUTOEXTEND\n3. 清理历史分区数据\n4. 重建高碎片率索引", severity: "warning", tags: ["Oracle", "表空间"] },
  { id: "kb-005", title: "SAN交换机端口错误处理", category: "存储", target_type: "san_switch", symptom: "porterrshow显示错误计数增长", cause: "光模块故障、光纤线路衰减、SFP兼容性问题", solution: "1. 检查SFP模块状态和型号兼容性\n2. 清洁光纤连接器\n3. 测量光功率\n4. 更换故障SFP或光纤线", severity: "critical", tags: ["SAN", "Brocade"] },
  { id: "kb-006", title: "MySQL主从延迟处理", category: "数据库", target_type: "mysql", symptom: "Seconds_Behind_Master持续增长", cause: "大事务、从库性能不足、网络延迟、单线程复制瓶颈", solution: "1. 检查是否有大事务\n2. 确认从库性能\n3. 开启多线程复制\n4. 检查网络延迟", severity: "warning", tags: ["MySQL", "复制"] },
  { id: "kb-007", title: "AIX文件系统扩容", category: "操作系统", target_type: "aix", symptom: "文件系统使用率超过80%", cause: "数据增长、日志积累", solution: "1. chfs -a size=+10G /filesystem\n2. 确认VG中有足够空闲空间\n3. 清理无用文件", severity: "warning", tags: ["AIX", "文件系统"] },
  { id: "kb-008", title: "BMC iDRAC无法访问处理", category: "硬件管理", target_type: "bmc", symptom: "iDRAC Web界面无法访问", cause: "iDRAC服务挂起、网络配置变更、固件Bug", solution: "1. 尝试SSH登录iDRAC\n2. racadm racreset soft\n3. 检查网络配置\n4. 升级iDRAC固件", severity: "warning", tags: ["iDRAC", "BMC"] },
];

// ============================================================
// Route Handler
// ============================================================

type RouteHandler = (req: NextRequest, params: string[]) => Promise<NextResponse>;

const routes: Record<string, Record<string, RouteHandler>> = {
  GET: {
    "health": async () => NextResponse.json({ status: "healthy", service: "Acdante ITOps Inspection Platform", version: "1.0.0", timestamp: new Date().toISOString() }),
    "dashboard/stats": async () => NextResponse.json(getDashboardStats()),
    "targets": async (req) => {
      const url = new URL(req.url);
      const type = url.searchParams.get("type");
      const filtered = type ? targets.filter(t => t.type === type) : targets;
      return NextResponse.json({ targets: filtered });
    },
    "templates": async (req) => {
      const url = new URL(req.url);
      const type = url.searchParams.get("type");
      const filtered = type ? templates.filter(t => t.target_type === type) : templates;
      return NextResponse.json({ templates: filtered });
    },
    "tasks": async () => NextResponse.json({ tasks }),
    "results": async (req) => {
      const url = new URL(req.url);
      const taskId = url.searchParams.get("task_id") || "";
      const targetId = parseInt(url.searchParams.get("target_id") || "0");
      let filtered = results;
      if (taskId) filtered = filtered.filter(r => r.task_id === taskId);
      if (targetId) filtered = filtered.filter(r => r.target_id === targetId);
      return NextResponse.json({ results: filtered });
    },
    "reports": async () => NextResponse.json({ reports }),
    "knowledge": async () => NextResponse.json({ entries: knowledge }),
  },
  POST: {
    "targets": async (req) => {
      const body = await req.json();
      const newTarget = { ...body, id: nextTargetId++, status: "active", health_score: 100, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), tags: body.tags || [] };
      targets.push(newTarget);
      return NextResponse.json(newTarget, { status: 201 });
    },
    "tasks": async (req) => {
      const body = await req.json();
      const newTask = { ...body, id: `task-${String(nextTaskNum++).padStart(3, '0')}`, status: "pending", created_at: new Date().toISOString(), updated_at: new Date().toISOString() };
      tasks.push(newTask);
      return NextResponse.json(newTask, { status: 201 });
    },
    "reports/generate": async (req) => {
      const body = await req.json();
      return NextResponse.json({ id: `rpt-gen-${Date.now()}`, task_id: body.task_id, format: body.format || "html", health_score: 85, total_items: 10, ok_count: 8, warning_count: 1, critical_count: 1, summary: "巡检报告已生成", generated_at: new Date().toISOString() }, { status: 201 });
    },
  },
};

function getDashboardStats() {
  const typeCounts: Record<string, number> = {};
  targets.forEach(t => { typeCounts[t.type] = (typeCounts[t.type] || 0) + 1; });
  const targetsByType = Object.entries(typeCounts).map(([type, count]) => ({ type, count }));

  const criticalIssues = results.filter(r => r.status === "critical").length;
  const warningIssues = results.filter(r => r.status === "warning").length;
  const runningTasks = tasks.filter(t => t.status === "running").length;

  return {
    total_targets: targets.length,
    active_targets: targets.filter(t => t.status === "active").length,
    total_templates: templates.length,
    total_tasks: tasks.length,
    running_tasks: runningTasks,
    today_reports: reports.length,
    critical_issues: criticalIssues,
    warning_issues: warningIssues,
    targets_by_type: targetsByType,
    recent_tasks: [
      { id: "task-005", name: "SAN交换机巡检", status: "running", started_at: ago(0.08), progress: 60 },
      { id: "task-002", name: "Oracle生产库巡检", status: "completed", started_at: ago(1), progress: 100 },
      { id: "task-001", name: "每日核心网络巡检", status: "completed", started_at: ago(2), progress: 100 },
      { id: "task-006", name: "MySQL数据库巡检", status: "completed", started_at: ago(3), progress: 100 },
    ],
    recent_alerts: [
      { id: 1, severity: "critical", message: "ORACLE-PROD-DB1 检测到锁阻塞：SID 156阻塞3个会话", target: "ORACLE-PROD-DB1", time: ago(0.5) },
      { id: 2, severity: "warning", message: "APP-SERVER-01 /data分区使用率91%，接近阈值", target: "APP-SERVER-01", time: ago(1) },
      { id: 3, severity: "warning", message: "APP-SERVER-02 内存使用率87.3%，超过警告阈值", target: "APP-SERVER-02", time: ago(48) },
      { id: 4, severity: "info", message: "SAN-SWITCH-A 巡检任务正在执行中", target: "SAN-SWITCH-A", time: ago(0.08) },
      { id: 5, severity: "info", message: "MySQL-PROD-01 主从复制状态正常", target: "MySQL-PROD-01", time: ago(3) },
    ],
    health_trend: [
      { date: "01-03", health_score: 88, critical: 1, warning: 3 },
      { date: "01-04", health_score: 91, critical: 0, warning: 2 },
      { date: "01-05", health_score: 85, critical: 2, warning: 4 },
      { date: "01-06", health_score: 90, critical: 1, warning: 2 },
      { date: "01-07", health_score: 87, critical: 1, warning: 3 },
      { date: "01-08", health_score: 89, critical: 1, warning: 2 },
      { date: "01-09", health_score: 86, critical: 2, warning: 3 },
    ],
  };
}

// ============================================================
// Catch-all Route Handler
// ============================================================

export async function GET(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  return handleRequest(request, path);
}

export async function POST(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  return handleRequest(request, path);
}

export async function PUT(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  return handleRequest(request, path);
}

export async function DELETE(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  return handleRequest(request, path);
}

async function handleRequest(request: NextRequest, pathSegments: string[]) {
  const path = pathSegments.join('/');
  const method = request.method;

  // Handle specific resource routes
  // GET /api/v1/targets/:id
  if (method === 'GET' && path.match(/^targets\/\d+$/)) {
    const id = parseInt(path.split('/')[1]);
    const target = targets.find(t => t.id === id);
    if (!target) return NextResponse.json({ error: "巡检对象不存在" }, { status: 404 });
    return NextResponse.json(target);
  }

  // POST /api/v1/targets/:id/test
  if (method === 'POST' && path.match(/^targets\/\d+\/test$/)) {
    const id = parseInt(path.split('/')[1]);
    const target = targets.find(t => t.id === id);
    if (!target) return NextResponse.json({ error: "巡检对象不存在" }, { status: 404 });
    return NextResponse.json({ success: true, message: `连接 ${target.name} (${target.connection_params.host}:${target.connection_params.port}) 成功`, version: target.version, connect_time_ms: Math.floor(Math.random() * 80) + 10 });
  }

  // PUT /api/v1/targets/:id
  if (method === 'PUT' && path.match(/^targets\/\d+$/)) {
    const id = parseInt(path.split('/')[1]);
    const body = await request.json();
    const idx = targets.findIndex(t => t.id === id);
    if (idx === -1) return NextResponse.json({ error: "巡检对象不存在" }, { status: 404 });
    targets[idx] = { ...targets[idx], ...body, id, updated_at: new Date().toISOString() };
    return NextResponse.json(targets[idx]);
  }

  // DELETE /api/v1/targets/:id
  if (method === 'DELETE' && path.match(/^targets\/\d+$/)) {
    const id = parseInt(path.split('/')[1]);
    const idx = targets.findIndex(t => t.id === id);
    if (idx !== -1) targets.splice(idx, 1);
    return NextResponse.json({ message: "已删除" });
  }

  // GET /api/v1/templates/:id
  if (method === 'GET' && path.match(/^templates\/[\w-]+$/) && !path.startsWith('templates/')) {
    const id = path.split('/')[1];
    const template = templates.find(t => t.id === id);
    if (!template) return NextResponse.json({ error: "模板不存在" }, { status: 404 });
    return NextResponse.json(template);
  }
  if (method === 'GET' && path.startsWith('templates/')) {
    const id = path.replace('templates/', '');
    const template = templates.find(t => t.id === id);
    if (!template) return NextResponse.json({ error: "模板不存在" }, { status: 404 });
    return NextResponse.json(template);
  }

  // GET /api/v1/tasks/:id
  if (method === 'GET' && path.startsWith('tasks/') && !path.includes('/run')) {
    const id = path.replace('tasks/', '');
    const task = tasks.find(t => t.id === id);
    if (!task) return NextResponse.json({ error: "任务不存在" }, { status: 404 });
    return NextResponse.json(task);
  }

  // POST /api/v1/tasks/:id/run
  if (method === 'POST' && path.match(/^tasks\/[\w-]+\/run$/)) {
    const id = path.split('/')[1];
    const task = tasks.find(t => t.id === id);
    if (!task) return NextResponse.json({ error: "任务不存在" }, { status: 404 });
    task.status = "running";
    task.last_run_at = new Date().toISOString();
    return NextResponse.json({ task, message: "任务已触发执行" });
  }

  // GET /api/v1/reports/:id
  if (method === 'GET' && path.startsWith('reports/') && !path.includes('/download')) {
    const id = path.replace('reports/', '');
    const report = reports.find(r => r.id === id);
    if (!report) return NextResponse.json({ error: "报告不存在" }, { status: 404 });
    return NextResponse.json(report);
  }

  // GET /api/v1/reports/:id/download
  if (method === 'GET' && path.includes('/download')) {
    const id = path.split('/')[1];
    const report = reports.find(r => r.id === id);
    if (!report) return NextResponse.json({ error: "报告不存在" }, { status: 404 });
    const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${report.task_name}</title><style>body{font-family:Arial,sans-serif;margin:40px;color:#333}.header{background:linear-gradient(135deg,#1e293b,#334155);color:#fff;padding:30px;border-radius:8px;margin-bottom:20px}.header h1{margin:0;font-size:24px}.stats{display:flex;gap:16px;margin:20px 0}.stat{flex:1;padding:16px;border-radius:8px;text-align:center}.stat-ok{background:#dcfce7;color:#166534}.stat-warn{background:#fef3c7;color:#92400e}.stat-crit{background:#fecaca;color:#991b1b}table{width:100%;border-collapse:collapse;margin:16px 0}th,td{border:1px solid #e2e8f0;padding:8px 12px;text-align:left;font-size:14px}th{background:#f8fafc;font-weight:600}.footer{margin-top:30px;padding-top:16px;border-top:1px solid #e2e8f0;font-size:12px;color:#94a3b8;text-align:center}</style></head><body><div class="header"><h1>${report.task_name}</h1><p>Acdante ITOps Inspection Platform | 生成时间: ${report.generated_at}</p></div><div class="stats"><div class="stat stat-ok"><h3>${report.ok_count}</h3><p>正常</p></div><div class="stat stat-warn"><h3>${report.warning_count}</h3><p>警告</p></div><div class="stat stat-crit"><h3>${report.critical_count}</h3><p>严重</p></div><div class="stat" style="background:#f0f9ff;color:#075985"><h3>${report.health_score}</h3><p>健康度</p></div></div><h2>摘要</h2><p>${report.summary}</p><div class="footer">Acdante ITOps Inspection Platform v1.0.0 | Powered by Acdante AI</div></body></html>`;
    return new NextResponse(html, { headers: { 'content-type': 'text/html; charset=utf-8', 'content-disposition': `attachment; filename="${id}.html"` } });
  }

  // GET /api/v1/knowledge/:id
  if (method === 'GET' && path.startsWith('knowledge/')) {
    const id = path.replace('knowledge/', '');
    const entry = knowledge.find(e => e.id === id);
    if (!entry) return NextResponse.json({ error: "知识条目不存在" }, { status: 404 });
    return NextResponse.json(entry);
  }

  // Try generic routes
  const methodRoutes = routes[method];
  if (methodRoutes && methodRoutes[path]) {
    return methodRoutes[path](request, []);
  }

  return NextResponse.json({ error: `Not found: ${method} ${path}` }, { status: 404 });
}

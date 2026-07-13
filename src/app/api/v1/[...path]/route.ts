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
  // ============ DBCheck 数据库巡检模板 (v3.0) ============
  // 以下数据库模板由 DBCheck 引擎驱动，提供 70-130+ 项专业巡检
  {
    id: "tpl-dbcheck-oracle-v3", name: "Oracle 全量巡检 (DBCheck引擎)", target_type: "oracle", brand: "Oracle", version: "v3.0.0", description: "基于DBCheck v2.6.0引擎的Oracle数据库全量巡检，涵盖实例状态、表空间、ASM、DataGuard、AWR、备份恢复、安全审计、性能诊断等130+巡检项。支持10g/11g/12c/19c/21c全版本自适应。", is_builtin: true, created_by: "system (DBCheck)", created_at: ago(720), updated_at: ago(0.1),
    is_dbcheck: true, dbcheck_type: "oracle", item_count: 130,
    items: [
      { id: "dbo-01", name: "数据库实例状态", category: "实例", command: "dbcheck:instance_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 20, order: 1 },
      { id: "dbo-02", name: "表空间使用率", category: "存储", command: "dbcheck:tablespace_usage", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "tbs_usage", operator: "gt", critical: 95, warning: 85, unit: "%" }, suggestion: "扩容表空间或清理历史数据", weight: 20, order: 2 },
      { id: "dbo-03", name: "ASM磁盘组状态", category: "存储", command: "dbcheck:asm_diskgroup", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 3 },
      { id: "dbo-04", name: "DataGuard同步状态", category: "容灾", command: "dbcheck:dataguard_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 4 },
      { id: "dbo-05", name: "DG同步延迟", category: "容灾", command: "dbcheck:dg_lag", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "dg_lag", operator: "gt", critical: 60, warning: 10, unit: "秒" }, weight: 15, order: 5 },
      { id: "dbo-06", name: "SGA/PGA使用率", category: "内存", command: "dbcheck:sga_pga", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 6 },
      { id: "dbo-07", name: "活跃会话数", category: "会话", command: "dbcheck:active_sessions", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "sessions", operator: "gt", critical: 500, warning: 300, unit: "" }, weight: 10, order: 7 },
      { id: "dbo-08", name: "锁阻塞检测", category: "锁", command: "dbcheck:lock_blocking", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 20, order: 8, suggestion: "检查阻塞会话，必要时终止" },
      { id: "dbo-09", name: "RMAN备份状态", category: "备份", command: "dbcheck:rman_backup", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 9 },
      { id: "dbo-10", name: "归档日志空间", category: "存储", command: "dbcheck:archive_log", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "arch_usage", operator: "gt", critical: 90, warning: 75, unit: "%" }, weight: 10, order: 10 },
      { id: "dbo-11", name: "AWR性能概览", category: "性能", command: "dbcheck:awr_overview", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 11 },
      { id: "dbo-12", name: "无效对象检查", category: "对象", command: "dbcheck:invalid_objects", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 5, order: 12 },
      { id: "dbo-13", name: "Redo日志切换频率", category: "日志", command: "dbcheck:redo_switch", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 13 },
      { id: "dbo-14", name: "Undo表空间状态", category: "存储", command: "dbcheck:undo_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 14 },
      { id: "dbo-15", name: "用户权限审计", category: "安全", command: "dbcheck:user_audit", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 15 },
    ]
  },
  {
    id: "tpl-dbcheck-mysql-v3", name: "MySQL 全量巡检 (DBCheck引擎)", target_type: "mysql", brand: "Oracle", version: "v3.0.0", description: "基于DBCheck v2.6.0引擎的MySQL数据库全量巡检，涵盖主从复制、InnoDB缓冲池、慢查询、连接池、锁等待、binlog、安全配置等80+巡检项。支持5.7/8.0/8.4版本。", is_builtin: true, created_by: "system (DBCheck)", created_at: ago(720), updated_at: ago(0.1),
    is_dbcheck: true, dbcheck_type: "mysql", item_count: 80,
    items: [
      { id: "dbm-01", name: "数据库实例状态", category: "实例", command: "dbcheck:instance_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 20, order: 1 },
      { id: "dbm-02", name: "InnoDB缓冲池命中率", category: "内存", command: "dbcheck:innodb_buffer_pool", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "buffer_hit", operator: "lt", critical: 95, warning: 98, unit: "%" }, suggestion: "增加innodb_buffer_pool_size", weight: 20, order: 2 },
      { id: "dbm-03", name: "主从复制状态", category: "复制", command: "dbcheck:replication_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 20, order: 3 },
      { id: "dbm-04", name: "慢查询统计", category: "性能", command: "dbcheck:slow_queries", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 4 },
      { id: "dbm-05", name: "连接数使用率", category: "连接", command: "dbcheck:connection_usage", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "conn_usage", operator: "gt", critical: 90, warning: 75, unit: "%" }, suggestion: "增加max_connections或优化连接池", weight: 15, order: 5 },
      { id: "dbm-06", name: "表锁等待", category: "锁", command: "dbcheck:table_locks", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 6 },
      { id: "dbm-07", name: "binlog状态", category: "日志", command: "dbcheck:binlog_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 7 },
      { id: "dbm-08", name: "查询缓存命中率", category: "缓存", command: "dbcheck:query_cache", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 8 },
      { id: "dbm-09", name: "表状态检查", category: "对象", command: "dbcheck:table_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 9 },
    ]
  },
  {
    id: "tpl-dbcheck-pg-v3", name: "PostgreSQL 全量巡检 (DBCheck引擎)", target_type: "postgres", brand: "PostgreSQL", version: "v3.0.0", description: "基于DBCheck v2.6.0引擎的PostgreSQL数据库全量巡检，涵盖归档模式、缓存命中率、死元组、复制状态、锁等待、连接数、配置基线等70+巡检项。支持12/13/14/15/16版本。", is_builtin: true, created_by: "system (DBCheck)", created_at: ago(720), updated_at: ago(0.1),
    is_dbcheck: true, dbcheck_type: "postgresql", item_count: 70,
    items: [
      { id: "dbp-01", name: "数据库实例状态", category: "实例", command: "dbcheck:instance_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 20, order: 1 },
      { id: "dbp-02", name: "缓存命中率", category: "缓存", command: "dbcheck:cache_hit_ratio", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "cache_hit", operator: "lt", critical: 95, warning: 98, unit: "%" }, suggestion: "增加shared_buffers", weight: 20, order: 2 },
      { id: "dbp-03", name: "死元组比例", category: "存储", command: "dbcheck:dead_tuples", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "dead_tuples", operator: "gt", critical: 20, warning: 10, unit: "%" }, suggestion: "执行VACUUM或调整autovacuum参数", weight: 15, order: 3 },
      { id: "dbp-04", name: "复制状态", category: "复制", command: "dbcheck:replication", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 4 },
      { id: "dbp-05", name: "连接数使用率", category: "连接", command: "dbcheck:connection_usage", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "conn_usage", operator: "gt", critical: 90, warning: 75, unit: "%" }, weight: 15, order: 5 },
      { id: "dbp-06", name: "锁等待", category: "锁", command: "dbcheck:lock_waiting", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 6 },
      { id: "dbp-07", name: "归档模式", category: "备份", command: "dbcheck:archive_mode", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 7 },
      { id: "dbp-08", name: "数据库大小", category: "存储", command: "dbcheck:db_size", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 8 },
    ]
  },
  {
    id: "tpl-dbcheck-sqlserver-v3", name: "SQL Server 全量巡检 (DBCheck引擎)", target_type: "mssql", brand: "Microsoft", version: "v3.0.0", description: "基于DBCheck v2.6.0引擎的SQL Server数据库全量巡检，涵盖等待统计、锁与阻塞、备份状态、文件使用率、索引健康、安全审计等60+巡检项。支持2016/2017/2019/2022版本。", is_builtin: true, created_by: "system (DBCheck)", created_at: ago(720), updated_at: ago(0.1),
    is_dbcheck: true, dbcheck_type: "sqlserver", item_count: 60,
    items: [
      { id: "dbs-01", name: "数据库状态", category: "实例", command: "dbcheck:instance_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 20, order: 1 },
      { id: "dbs-02", name: "等待统计", category: "性能", command: "dbcheck:wait_stats", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 20, order: 2 },
      { id: "dbs-03", name: "锁与阻塞", category: "锁", command: "dbcheck:lock_blocking", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 20, order: 3 },
      { id: "dbs-04", name: "备份状态", category: "备份", command: "dbcheck:backup_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 4 },
      { id: "dbs-05", name: "文件使用率", category: "存储", command: "dbcheck:file_usage", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "file_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, weight: 15, order: 5 },
      { id: "dbs-06", name: "索引碎片", category: "对象", command: "dbcheck:index_frag", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 6 },
    ]
  },
  // ============ 新增国产数据库 DBCheck 模板 ============
  {
    id: "tpl-dbcheck-dm8-v3", name: "达梦DM8 全量巡检 (DBCheck引擎)", target_type: "dm8", brand: "达梦", version: "v3.0.0", description: "基于DBCheck v2.6.0引擎的达梦DM8数据库全量巡检，涵盖表空间、SGA/PGA、缓冲池、配置基线、索引健康、备份状态等70+巡检项。", is_builtin: true, created_by: "system (DBCheck)", created_at: ago(720), updated_at: ago(0.1),
    is_dbcheck: true, dbcheck_type: "dm8", item_count: 70,
    items: [
      { id: "dbd-01", name: "数据库实例状态", category: "实例", command: "dbcheck:instance_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 20, order: 1 },
      { id: "dbd-02", name: "表空间使用率", category: "存储", command: "dbcheck:tablespace_usage", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "tbs_usage", operator: "gt", critical: 95, warning: 85, unit: "%" }, weight: 20, order: 2 },
      { id: "dbd-03", name: "SGA/PGA使用率", category: "内存", command: "dbcheck:sga_pga", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 3 },
      { id: "dbd-04", name: "缓冲池命中率", category: "缓存", command: "dbcheck:buffer_hit", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 4 },
      { id: "dbd-05", name: "配置基线检查", category: "配置", command: "dbcheck:config_baseline", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 5 },
      { id: "dbd-06", name: "索引健康检查", category: "对象", command: "dbcheck:index_health", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 6 },
      { id: "dbd-07", name: "备份状态", category: "备份", command: "dbcheck:backup_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 7 },
    ]
  },
  {
    id: "tpl-dbcheck-tidb-v3", name: "TiDB 全量巡检 (DBCheck引擎)", target_type: "tidb", brand: "PingCAP", version: "v3.0.0", description: "基于DBCheck v2.6.0引擎的TiDB分布式数据库全量巡检，涵盖Placement Rules、TiCDC状态、PD心跳、Follower延迟、慢查询分析、连接池等60+巡检项。", is_builtin: true, created_by: "system (DBCheck)", created_at: ago(720), updated_at: ago(0.1),
    is_dbcheck: true, dbcheck_type: "tidb", item_count: 60,
    items: [
      { id: "dbt-01", name: "集群状态概览", category: "集群", command: "dbcheck:cluster_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 20, order: 1 },
      { id: "dbt-02", name: "Placement Rules", category: "配置", command: "dbcheck:placement_rules", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 2 },
      { id: "dbt-03", name: "TiCDC状态", category: "复制", command: "dbcheck:ticdc_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 3 },
      { id: "dbt-04", name: "PD心跳", category: "集群", command: "dbcheck:pd_heartbeat", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 4 },
      { id: "dbt-05", name: "Follower延迟", category: "复制", command: "dbcheck:follower_lag", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "follower_lag", operator: "gt", critical: 60, warning: 10, unit: "秒" }, weight: 15, order: 5 },
      { id: "dbt-06", name: "慢查询分析", category: "性能", command: "dbcheck:slow_query", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 6 },
      { id: "dbt-07", name: "连接数使用率", category: "连接", command: "dbcheck:connection_usage", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 7 },
    ]
  },
  {
    id: "tpl-dbcheck-kingbase-v3", name: "KingbaseES 全量巡检 (DBCheck引擎)", target_type: "kingbase", brand: "人大金仓", version: "v3.0.0", description: "基于DBCheck v2.6.0引擎的KingbaseES数据库全量巡检，涵盖实例状态、表空间、复制状态、锁等待、配置基线等50+巡检项。", is_builtin: true, created_by: "system (DBCheck)", created_at: ago(720), updated_at: ago(0.1),
    is_dbcheck: true, dbcheck_type: "kingbase", item_count: 50,
    items: [
      { id: "dbk-01", name: "实例状态", category: "实例", command: "dbcheck:instance_status", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 20, order: 1 },
      { id: "dbk-02", name: "表空间使用率", category: "存储", command: "dbcheck:tablespace_usage", command_type: "dbcheck", is_read_only: true, parser: "raw", threshold: { metric: "tbs_usage", operator: "gt", critical: 95, warning: 85, unit: "%" }, weight: 20, order: 2 },
      { id: "dbk-03", name: "复制状态", category: "复制", command: "dbcheck:replication", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 3 },
      { id: "dbk-04", name: "锁等待", category: "锁", command: "dbcheck:lock_waiting", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 15, order: 4 },
      { id: "dbk-05", name: "配置基线", category: "配置", command: "dbcheck:config_baseline", command_type: "dbcheck", is_read_only: true, parser: "raw", weight: 10, order: 5 },
    ]
  },
  // ============ 保留的非数据库模板 ============
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
  // ============ SNMP 巡检模板（新增） ============
  {
    id: "tpl-snmp-huawei-switch-v1", name: "华为交换机SNMP巡检模板", target_type: "network", brand: "华为", version: "v2.0.0", description: "华为交换机/路由器SNMP巡检模板，通过SNMP协议采集CPU、内存、温度、接口流量、错误包等", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "snmp-hw-01", name: "系统描述", category: "系统", command: "snmp:1.3.6.1.2.1.1.1.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 5, order: 1 },
      { id: "snmp-hw-02", name: "系统运行时间", category: "系统", command: "snmp:1.3.6.1.2.1.1.3.0", command_type: "snmp", is_read_only: true, parser: "ticks_to_uptime", weight: 5, order: 2 },
      { id: "snmp-hw-03", name: "CPU使用率(%)", category: "CPU", command: "snmp:1.3.6.1.4.1.2011.6.3.4.1.3.1", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "cpu_usage", operator: "gt", critical: 90, warning: 70, unit: "%" }, suggestion: "检查异常进程或高流量，考虑升级硬件", weight: 20, order: 3 },
      { id: "snmp-hw-04", name: "CPU温度(°C)", category: "硬件", command: "snmp:1.3.6.1.4.1.2011.6.3.4.1.7.1", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "temperature", operator: "gt", critical: 75, warning: 65, unit: "°C" }, suggestion: "检查机房环境温度、设备风扇状态", weight: 15, order: 4 },
      { id: "snmp-hw-05", name: "内存使用率(%)", category: "内存", command: "snmp:1.3.6.1.4.1.2011.6.3.5.1.4.1", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "mem_usage", operator: "gt", critical: 85, warning: 70, unit: "%" }, suggestion: "检查内存泄漏或减少路由表规模", weight: 20, order: 5 },
      { id: "snmp-hw-06", name: "接口入错误包", category: "接口", command: "snmp:1.3.6.1.2.1.2.2.1.14", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "if_in_errors", operator: "gt", critical: 100, warning: 10, unit: "包" }, suggestion: "检查光纤模块、线路质量", weight: 15, order: 6 },
      { id: "snmp-hw-07", name: "设备温度", category: "硬件", command: "snmp:1.3.6.1.4.1.2011.6.3.3.1.9.1", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "temperature", operator: "gt", critical: 70, warning: 60, unit: "°C" }, weight: 10, order: 7 },
      { id: "snmp-hw-08", name: "风扇状态", category: "硬件", command: "snmp:1.3.6.1.4.1.2011.6.3.3.1.5.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 10, order: 8 },
      { id: "snmp-hw-09", name: "电源状态", category: "硬件", command: "snmp:1.3.6.1.4.1.2011.6.3.3.1.7.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 10, order: 9 },
    ]
  },
  {
    id: "tpl-snmp-h3c-switch-v1", name: "华三交换机SNMP巡检模板", target_type: "network", brand: "华三", version: "v2.0.0", description: "华三交换机/路由器SNMP巡检模板，通过SNMP协议采集CPU、内存、温度等", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "snmp-h3c-01", name: "系统描述", category: "系统", command: "snmp:1.3.6.1.2.1.1.1.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 5, order: 1 },
      { id: "snmp-h3c-02", name: "系统运行时间", category: "系统", command: "snmp:1.3.6.1.2.1.1.3.0", command_type: "snmp", is_read_only: true, parser: "ticks_to_uptime", weight: 5, order: 2 },
      { id: "snmp-h3c-03", name: "CPU使用率(%)", category: "CPU", command: "snmp:1.3.6.1.4.1.25506.2.6.1.1.1.1.6.1", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "cpu_usage", operator: "gt", critical: 90, warning: 70, unit: "%" }, weight: 20, order: 3 },
      { id: "snmp-h3c-04", name: "内存使用率(%)", category: "内存", command: "snmp:1.3.6.1.4.1.25506.2.6.1.1.1.1.8.1", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "mem_usage", operator: "gt", critical: 85, warning: 70, unit: "%" }, weight: 20, order: 4 },
      { id: "snmp-h3c-05", name: "设备温度(°C)", category: "硬件", command: "snmp:1.3.6.1.4.1.25506.2.6.1.1.1.1.12.1", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "temperature", operator: "gt", critical: 70, warning: 60, unit: "°C" }, weight: 10, order: 5 },
      { id: "snmp-h3c-06", name: "风扇状态", category: "硬件", command: "snmp:1.3.6.1.4.1.25506.2.6.1.1.1.1.14.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 10, order: 6 },
      { id: "snmp-h3c-07", name: "接口入错误包", category: "接口", command: "snmp:1.3.6.1.2.1.2.2.1.14", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "if_in_errors", operator: "gt", critical: 100, warning: 10, unit: "包" }, weight: 15, order: 7 },
    ]
  },
  {
    id: "tpl-snmp-cisco-switch-v1", name: "思科交换机SNMP巡检模板", target_type: "network", brand: "思科", version: "v2.0.0", description: "思科Catalyst/Nexus交换机SNMP巡检模板", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "snmp-cisco-01", name: "系统描述", category: "系统", command: "snmp:1.3.6.1.2.1.1.1.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 5, order: 1 },
      { id: "snmp-cisco-02", name: "系统运行时间", category: "系统", command: "snmp:1.3.6.1.2.1.1.3.0", command_type: "snmp", is_read_only: true, parser: "ticks_to_uptime", weight: 5, order: 2 },
      { id: "snmp-cisco-03", name: "CPU 5分钟负载(%)", category: "CPU", command: "snmp:1.3.6.1.4.1.9.9.109.1.1.1.1.7.1", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "cpu_usage", operator: "gt", critical: 90, warning: 70, unit: "%" }, suggestion: "检查路由表大小、STP收敛", weight: 20, order: 3 },
      { id: "snmp-cisco-04", name: "已用内存", category: "内存", command: "snmp:1.3.6.1.4.1.9.9.48.1.1.1.5.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 15, order: 4 },
      { id: "snmp-cisco-05", name: "温度状态", category: "硬件", command: "snmp:1.3.6.1.4.1.9.9.13.1.3.1.6.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 15, order: 5 },
      { id: "snmp-cisco-06", name: "风扇状态", category: "硬件", command: "snmp:1.3.6.1.4.1.9.9.13.1.4.1.3.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 10, order: 6 },
      { id: "snmp-cisco-07", name: "接口入错误包", category: "接口", command: "snmp:1.3.6.1.2.1.2.2.1.14", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "if_in_errors", operator: "gt", critical: 100, warning: 10, unit: "包" }, weight: 15, order: 7 },
    ]
  },
  {
    id: "tpl-snmp-f5-v1", name: "F5 BIG-IP负载均衡SNMP巡检模板", target_type: "network", brand: "F5", version: "v2.0.0", description: "F5 BIG-IP负载均衡SNMP巡检模板，覆盖CPU、内存、连接、池状态", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "snmp-f5-01", name: "系统描述", category: "系统", command: "snmp:1.3.6.1.2.1.1.1.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 5, order: 1 },
      { id: "snmp-f5-02", name: "系统运行时间", category: "系统", command: "snmp:1.3.6.1.2.1.1.3.0", command_type: "snmp", is_read_only: true, parser: "ticks_to_uptime", weight: 5, order: 2 },
      { id: "snmp-f5-03", name: "CPU使用率(%)", category: "CPU", command: "snmp:1.3.6.1.4.1.3375.2.1.1.2.1.44.1", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "cpu_usage", operator: "gt", critical: 90, warning: 70, unit: "%" }, weight: 20, order: 3 },
      { id: "snmp-f5-04", name: "总连接数", category: "连接", command: "snmp:1.3.6.1.4.1.3375.2.1.1.2.1.39.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 15, order: 4 },
      { id: "snmp-f5-05", name: "活跃连接数", category: "连接", command: "snmp:1.3.6.1.4.1.3375.2.1.1.2.1.40.1", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "active_conns", operator: "gt", critical: 500000, warning: 250000, unit: "连接" }, weight: 20, order: 5 },
      { id: "snmp-f5-06", name: "池可用状态", category: "池", command: "snmp:1.3.6.1.4.1.3375.2.2.5.5.2.1.6", command_type: "snmp", is_read_only: true, parser: "raw", weight: 15, order: 6 },
      { id: "snmp-f5-07", name: "虚拟服务状态", category: "虚拟服务", command: "snmp:1.3.6.1.4.1.3375.2.2.10.13.2.1.3", command_type: "snmp", is_read_only: true, parser: "raw", weight: 15, order: 7 },
    ]
  },
  {
    id: "tpl-snmp-dell-server-v1", name: "Dell服务器iDRAC SNMP巡检模板", target_type: "bmc", brand: "Dell", version: "v2.0.0", description: "Dell PowerEdge服务器iDRAC SNMP巡检模板，覆盖硬件健康、磁盘、电源、风扇", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "snmp-dell-01", name: "系统全局状态", category: "系统", command: "snmp:1.3.6.1.4.1.674.10892.1.200.10.1.2.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 20, order: 1, suggestion: "检查iDRAC管理界面查看具体告警" },
      { id: "snmp-dell-02", name: "电源状态", category: "电源", command: "snmp:1.3.6.1.4.1.674.10892.1.200.10.1.5.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 15, order: 2, suggestion: "检查电源模块连接和状态" },
      { id: "snmp-dell-03", name: "风扇状态", category: "散热", command: "snmp:1.3.6.1.4.1.674.10892.1.200.10.1.8.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 10, order: 3, suggestion: "检查风扇是否正常运转" },
      { id: "snmp-dell-04", name: "温度状态", category: "散热", command: "snmp:1.3.6.1.4.1.674.10892.1.200.10.1.9.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 15, order: 4, suggestion: "检查机房环境和散热" },
      { id: "snmp-dell-05", name: "内存状态", category: "内存", command: "snmp:1.3.6.1.4.1.674.10892.1.200.10.1.11.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 15, order: 5, suggestion: "检查内存模块是否故障" },
      { id: "snmp-dell-06", name: "存储状态", category: "存储", command: "snmp:1.3.6.1.4.1.674.10892.1.200.10.1.14.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 15, order: 6, suggestion: "检查硬盘状态和RAID控制器" },
      { id: "snmp-dell-07", name: "处理器状态", category: "CPU", command: "snmp:1.3.6.1.4.1.674.10892.1.200.10.1.15.1", command_type: "snmp", is_read_only: true, parser: "raw", weight: 10, order: 7 },
    ]
  },
  {
    id: "tpl-snmp-linux-server-v1", name: "Linux服务器SNMP巡检模板", target_type: "linux", brand: "Generic", version: "v2.0.0", description: "Linux服务器通用SNMP巡检模板（需安装net-snmp），覆盖CPU、内存、磁盘、负载", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "snmp-lnx-01", name: "系统描述", category: "系统", command: "snmp:1.3.6.1.2.1.1.1.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 5, order: 1 },
      { id: "snmp-lnx-02", name: "系统运行时间", category: "系统", command: "snmp:1.3.6.1.2.1.1.3.0", command_type: "snmp", is_read_only: true, parser: "ticks_to_uptime", weight: 5, order: 2 },
      { id: "snmp-lnx-03", name: "系统负载1分钟", category: "CPU", command: "snmp:1.3.6.1.4.1.2021.10.1.3.1", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "load_avg", operator: "gt", critical: 16, warning: 8, unit: "" }, weight: 20, order: 3 },
      { id: "snmp-lnx-04", name: "可用物理内存(KB)", category: "内存", command: "snmp:1.3.6.1.4.1.2021.4.6.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 20, order: 4, suggestion: "内存不足，检查内存泄漏或增加内存" },
      { id: "snmp-lnx-05", name: "磁盘使用率(%)", category: "磁盘", command: "snmp:1.3.6.1.4.1.2021.9.1.9", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "disk_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, suggestion: "清理无用文件或扩容磁盘", weight: 20, order: 5 },
      { id: "snmp-lnx-06", name: "Inode使用率(%)", category: "磁盘", command: "snmp:1.3.6.1.4.1.2021.9.1.10", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "inode_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, weight: 10, order: 6 },
      { id: "snmp-lnx-07", name: "进程数", category: "系统", command: "snmp:1.3.6.1.2.1.25.1.6.0", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "processes", operator: "gt", critical: 1000, warning: 500, unit: "进程" }, weight: 10, order: 7 },
    ]
  },
  {
    id: "tpl-snmp-sangfor-v1", name: "深信服设备SNMP巡检模板", target_type: "network", brand: "深信服", version: "v2.0.0", description: "深信服上网行为管理/防火墙SNMP巡检模板", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "snmp-sf-01", name: "系统状态", category: "系统", command: "snmp:1.3.6.1.4.1.35047.1.3.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 20, order: 1 },
      { id: "snmp-sf-02", name: "CPU使用率(%)", category: "CPU", command: "snmp:1.3.6.1.4.1.35047.1.5.1.2.0", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "cpu_usage", operator: "gt", critical: 90, warning: 70, unit: "%" }, weight: 20, order: 2 },
      { id: "snmp-sf-03", name: "内存使用率(%)", category: "内存", command: "snmp:1.3.6.1.4.1.35047.1.5.1.3.0", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "mem_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, weight: 20, order: 3 },
      { id: "snmp-sf-04", name: "磁盘使用率(%)", category: "磁盘", command: "snmp:1.3.6.1.4.1.35047.1.5.1.4.0", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "disk_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, weight: 15, order: 4 },
      { id: "snmp-sf-05", name: "活跃连接数", category: "性能", command: "snmp:1.3.6.1.4.1.35047.1.5.1.5.0", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "active_conns", operator: "gt", critical: 500000, warning: 250000, unit: "连接" }, weight: 15, order: 5 },
    ]
  },
  {
    id: "tpl-snmp-checkpoint-v1", name: "Checkpoint防火墙SNMP巡检模板", target_type: "network", brand: "Checkpoint", version: "v2.0.0", description: "Checkpoint防火墙SNMP巡检模板", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "snmp-cp-01", name: "系统描述", category: "系统", command: "snmp:1.3.6.1.2.1.1.1.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 5, order: 1 },
      { id: "snmp-cp-02", name: "系统运行时间", category: "系统", command: "snmp:1.3.6.1.2.1.1.3.0", command_type: "snmp", is_read_only: true, parser: "ticks_to_uptime", weight: 5, order: 2 },
      { id: "snmp-cp-03", name: "CPU使用率(%)", category: "CPU", command: "snmp:1.3.6.1.4.1.2620.1.6.7.2.4.0", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "cpu_usage", operator: "gt", critical: 90, warning: 70, unit: "%" }, weight: 20, order: 3 },
      { id: "snmp-cp-04", name: "内存使用率(%)", category: "内存", command: "snmp:1.3.6.1.4.1.2620.1.6.7.2.5.0", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "mem_usage", operator: "gt", critical: 90, warning: 80, unit: "%" }, weight: 20, order: 4 },
      { id: "snmp-cp-05", name: "当前连接数", category: "性能", command: "snmp:1.3.6.1.4.1.2620.1.1.5.0", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "connections", operator: "gt", critical: 500000, warning: 250000, unit: "连接" }, weight: 20, order: 5 },
    ]
  },
  {
    id: "tpl-snmp-brocade-v1", name: "Brocade SAN交换机SNMP巡检模板", target_type: "san_switch", brand: "Brocade", version: "v2.0.0", description: "Brocade光纤交换机SNMP巡检模板，覆盖温度、端口错误、链路状态", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "snmp-brcd-01", name: "系统描述", category: "系统", command: "snmp:1.3.6.1.2.1.1.1.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 5, order: 1 },
      { id: "snmp-brcd-02", name: "系统运行时间", category: "系统", command: "snmp:1.3.6.1.2.1.1.3.0", command_type: "snmp", is_read_only: true, parser: "ticks_to_uptime", weight: 5, order: 2 },
      { id: "snmp-brcd-03", name: "FC端口CRC错误", category: "端口", command: "snmp:1.3.6.1.4.1.1588.2.1.1.1.6.2.1.17", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "crc_errors", operator: "gt", critical: 100, warning: 10, unit: "错误" }, suggestion: "检查SFP模块和光纤线路", weight: 20, order: 3 },
      { id: "snmp-brcd-04", name: "FC端口链路失败", category: "端口", command: "snmp:1.3.6.1.4.1.1588.2.1.1.1.6.2.1.13", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "link_failures", operator: "gt", critical: 5, warning: 1, unit: "次" }, suggestion: "检查光纤连接和SFP兼容性", weight: 20, order: 4 },
      { id: "snmp-brcd-05", name: "温度传感器(°C)", category: "硬件", command: "snmp:1.3.6.1.4.1.1588.2.1.1.1.1.22.1.3", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "temperature", operator: "gt", critical: 70, warning: 60, unit: "°C" }, weight: 15, order: 5 },
    ]
  },
  {
    id: "tpl-snmp-generic-network-v1", name: "通用网络设备SNMP巡检模板", target_type: "network", brand: "通用", version: "v2.0.0", description: "基于标准MIB-II的通用网络设备SNMP巡检模板，适用于所有支持SNMP的网络设备", is_builtin: true, created_by: "system", created_at: ago(720), updated_at: ago(1),
    items: [
      { id: "snmp-gen-01", name: "系统描述", category: "系统", command: "snmp:1.3.6.1.2.1.1.1.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 5, order: 1 },
      { id: "snmp-gen-02", name: "系统运行时间", category: "系统", command: "snmp:1.3.6.1.2.1.1.3.0", command_type: "snmp", is_read_only: true, parser: "ticks_to_uptime", weight: 5, order: 2 },
      { id: "snmp-gen-03", name: "接口数量", category: "接口", command: "snmp:1.3.6.1.2.1.2.1.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 5, order: 3 },
      { id: "snmp-gen-04", name: "接口运行状态", category: "接口", command: "snmp:1.3.6.1.2.1.2.2.1.8", command_type: "snmp", is_read_only: true, parser: "raw", weight: 20, order: 4, suggestion: "检查接口物理连接" },
      { id: "snmp-gen-05", name: "接口入错误包", category: "接口", command: "snmp:1.3.6.1.2.1.2.2.1.14", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "if_in_errors", operator: "gt", critical: 100, warning: 10, unit: "包" }, weight: 15, order: 5 },
      { id: "snmp-gen-06", name: "接口出错误包", category: "接口", command: "snmp:1.3.6.1.2.1.2.2.1.20", command_type: "snmp", is_read_only: true, parser: "raw", threshold: { metric: "if_out_errors", operator: "gt", critical: 100, warning: 10, unit: "包" }, weight: 15, order: 6 },
      { id: "snmp-gen-07", name: "TCP当前连接数", category: "连接", command: "snmp:1.3.6.1.2.1.6.9.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 10, order: 7 },
      { id: "snmp-gen-08", name: "SNMP接收包统计", category: "SNMP", command: "snmp:1.3.6.1.2.1.11.1.0", command_type: "snmp", is_read_only: true, parser: "raw", weight: 5, order: 8 },
    ]
  },
];

// --- Tasks ---
const tasks = [
  { id: "task-001", name: "每日核心网络巡检", template_id: "tpl-network-huawei-v1", target_ids: [1, 13, 14], schedule_type: "daily", status: "completed", last_run_at: ago(2), next_run_at: ago(-22), notify_email: ["ops@company.com"], created_by: "admin", created_at: ago(720), updated_at: ago(2) },
  { id: "task-002", name: "Oracle生产库巡检", template_id: "tpl-dbcheck-oracle-v3", target_ids: [3], schedule_type: "hourly", status: "completed", last_run_at: ago(1), next_run_at: ago(-0), notify_email: ["dba@company.com"], created_by: "admin", created_at: ago(480), updated_at: ago(1) },
  { id: "task-003", name: "Linux服务器周巡检", template_id: "tpl-linux-generic-v1", target_ids: [5, 6], schedule_type: "weekly", status: "completed", last_run_at: ago(48), next_run_at: ago(-120), created_by: "engineer", created_at: ago(240), updated_at: ago(48) },
  { id: "task-004", name: "存储设备月巡检", template_id: "tpl-storage-huawei-v1", target_ids: [9], schedule_type: "monthly", status: "pending", next_run_at: ago(-168), created_by: "admin", created_at: ago(720), updated_at: ago(720) },
  { id: "task-005", name: "SAN交换机巡检", template_id: "tpl-san-brocade-v1", target_ids: [8], schedule_type: "daily", status: "running", last_run_at: ago(0.08), created_by: "engineer", created_at: ago(360), updated_at: ago(0.08) },
  { id: "task-006", name: "MySQL数据库巡检", template_id: "tpl-dbcheck-mysql-v3", target_ids: [11], schedule_type: "daily", status: "completed", last_run_at: ago(3), next_run_at: ago(-21), created_by: "admin", created_at: ago(180), updated_at: ago(3) },
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
// HTTP Integration Mock Data
// ============================================================

interface HTTPDeviceData {
  id: string; name: string; brand: string; model: string; base_url: string; port: number;
  use_https: boolean; auth_type: string; username: string; password_enc: string;
  login_url: string; username_field: string; password_field: string; submit_selector: string;
  tls_min_version: string; tls_max_version: string; verify_cert: boolean;
  accept_self_signed: boolean; custom_headers: Record<string, string>; cipher_suites: string[];
  timeout: number; status: string; cert_status: string; cert_expiry: string | null;
  last_check: string | null; compat_mode: boolean; tags: string[]; created_at: string;
}

interface SSLCertData {
  id: string; device_id: string; device_name: string; subject: string; issuer: string;
  serial: string; valid_from: string; valid_to: string; status: string;
  is_self_signed: boolean; key_size: number; signature_algorithm: string;
  san: string[]; imported: boolean; trusted: boolean;
}

interface HTTPInspItem {
  id: string; device_id: string; name: string; category: string; method: string;
  url_path: string; request_body: string; content_type: string;
  parser_type: string; parser_expression: string;
  threshold: { operator: string; critical: number; warning: number; unit: string } | null;
  is_read_only: boolean; weight: number; order: number;
  screenshot_config?: {
    url_path: string; navigation_mode: 'url' | 'menu';
    menu_selectors: string[]; wait_condition: 'networkidle' | 'selector' | 'timeout';
    wait_timeout: number; wait_selector: string;
    capture_area: 'full_page' | 'viewport' | 'selector';
    capture_selector: string; viewport_width: number; viewport_height: number;
    word_template_position: string; word_section_title: string;
  };
}

interface HTTPExecLog {
  id: string; device_id: string; device_name: string; started_at: string;
  completed_at: string | null; status: string;
  total_items: number; completed_items: number; ok_count: number; warning_count: number;
  critical_count: number; error_count: number; cert_warning: string | null;
}

const httpDevices: HTTPDeviceData[] = [
  { id: "http-dev-001", name: "\u603B\u90E8\u9632\u706B\u5899-USG6625", brand: "huawei_fw", model: "USG6625", base_url: "10.0.1.254", port: 443, use_https: true, auth_type: "form", username: "admin", password_enc: "encrypted:***", login_url: "/api/v1/sys/user/login", username_field: "username", password_field: "password", submit_selector: "button[type=submit]", tls_min_version: "TLSv1.2", tls_max_version: "TLSv1.3", verify_cert: true, accept_self_signed: false, custom_headers: { "X-Requested-With": "XMLHttpRequest" }, cipher_suites: [], timeout: 30, status: "connected", cert_status: "self_signed", cert_expiry: "2027-03-15T00:00:00Z", last_check: ago(0.5), compat_mode: false, tags: ["\u6838\u5FC3\u7F51\u7EDC", "\u9632\u706B\u5899"], created_at: ago(720) },
  { id: "http-dev-002", name: "\u8FB9\u754C\u5B89\u5168\u7F51\u5173-Sangfor", brand: "sangfor", model: "AF-1000", base_url: "10.0.2.10", port: 443, use_https: true, auth_type: "form", username: "admin", password_enc: "encrypted:***", login_url: "/cgi-bin/login.cgi", username_field: "user", password_field: "pwd", submit_selector: "#login-btn", tls_min_version: "TLSv1.2", tls_max_version: "TLSv1.3", verify_cert: false, accept_self_signed: true, custom_headers: {}, cipher_suites: [], timeout: 30, status: "connected", cert_status: "self_signed", cert_expiry: "2026-12-01T00:00:00Z", last_check: ago(1), compat_mode: false, tags: ["\u8FB9\u754C\u5B89\u5168"], created_at: ago(600) },
  { id: "http-dev-003", name: "\u8001\u65E7\u9632\u706B\u5899-TopSec", brand: "topsec", model: "NGFW3000", base_url: "10.0.3.1", port: 443, use_https: true, auth_type: "form", username: "admin", password_enc: "encrypted:***", login_url: "/login", username_field: "userName", password_field: "passWord", submit_selector: "#submit", tls_min_version: "TLSv1.0", tls_max_version: "TLSv1.2", verify_cert: false, accept_self_signed: true, custom_headers: {}, cipher_suites: ["RSA_AES_128_CBC_SHA", "RSA_AES_256_CBC_SHA"], timeout: 60, status: "connected", cert_status: "expiring", cert_expiry: "2026-08-20T00:00:00Z", last_check: ago(2), compat_mode: true, tags: ["\u8001\u8BBE\u5907", "\u517C\u5BB9\u6A21\u5F0F"], created_at: ago(1440) },
  { id: "http-dev-004", name: "FortiGate-60F", brand: "fortinet", model: "FG-60F", base_url: "10.0.4.1", port: 443, use_https: true, auth_type: "form", username: "admin", password_enc: "encrypted:***", login_url: "/logincheck", username_field: "username", password_field: "password", submit_selector: "input[type=submit]", tls_min_version: "TLSv1.2", tls_max_version: "TLSv1.3", verify_cert: true, accept_self_signed: false, custom_headers: {}, cipher_suites: [], timeout: 30, status: "disconnected", cert_status: "valid", cert_expiry: "2028-06-10T00:00:00Z", last_check: ago(24), compat_mode: false, tags: ["\u5206\u652F\u673A\u623F"], created_at: ago(360) },
  { id: "http-dev-005", name: "\u542F\u660E\u661F\u8FB9\u754C\u9632\u706B\u5899", brand: "venusec", model: "Venusense-GF", base_url: "10.0.5.100", port: 443, use_https: true, auth_type: "form", username: "admin", password_enc: "encrypted:***", login_url: "/login.html", username_field: "username", password_field: "password", submit_selector: "#loginBtn", tls_min_version: "TLSv1.1", tls_max_version: "TLSv1.2", verify_cert: false, accept_self_signed: true, custom_headers: {}, cipher_suites: ["RSA_AES_128_CBC_SHA"], timeout: 45, status: "error", cert_status: "expired", cert_expiry: "2025-12-31T00:00:00Z", last_check: ago(48), compat_mode: true, tags: ["\u8001\u8BBE\u5907", "\u5F85\u66F4\u6362"], created_at: ago(2160) },
];

const httpCerts: SSLCertData[] = [
  { id: "cert-001", device_id: "http-dev-001", device_name: "\u603B\u90E8\u9632\u706B\u5899-USG6625", subject: "CN=10.0.1.254, O=Huawei, OU=IT", issuer: "CN=10.0.1.254, O=Huawei", serial: "0A:1B:2C:3D:4E:5F", valid_from: "2024-03-15T00:00:00Z", valid_to: "2027-03-15T00:00:00Z", status: "self_signed", is_self_signed: true, key_size: 2048, signature_algorithm: "SHA256withRSA", san: ["10.0.1.254", "usg6625.local"], imported: false, trusted: true },
  { id: "cert-002", device_id: "http-dev-002", device_name: "\u8FB9\u754C\u5B89\u5168\u7F51\u5173-Sangfor", subject: "CN=10.0.2.10, O=Sangfor", issuer: "CN=10.0.2.10, O=Sangfor", serial: "11:22:33:44:55:66", valid_from: "2023-12-01T00:00:00Z", valid_to: "2026-12-01T00:00:00Z", status: "self_signed", is_self_signed: true, key_size: 2048, signature_algorithm: "SHA256withRSA", san: ["10.0.2.10"], imported: false, trusted: true },
  { id: "cert-003", device_id: "http-dev-003", device_name: "\u8001\u65E7\u9632\u706B\u5899-TopSec", subject: "CN=topsec.local, O=TopSec", issuer: "CN=TopSec CA", serial: "AA:BB:CC:DD:EE:FF", valid_from: "2023-08-20T00:00:00Z", valid_to: "2026-08-20T00:00:00Z", status: "expiring", is_self_signed: false, key_size: 1024, signature_algorithm: "SHA1withRSA", san: ["topsec.local", "10.0.3.1"], imported: true, trusted: true },
  { id: "cert-004", device_id: "http-dev-004", device_name: "FortiGate-60F", subject: "CN=10.0.4.1, O=Fortinet", issuer: "CN=Fortinet CA, O=Fortinet", serial: "FF:EE:DD:CC:BB:AA", valid_from: "2025-06-10T00:00:00Z", valid_to: "2028-06-10T00:00:00Z", status: "valid", is_self_signed: false, key_size: 4096, signature_algorithm: "SHA256withRSA", san: ["10.0.4.1", "fortigate.local"], imported: false, trusted: true },
  { id: "cert-005", device_id: "http-dev-005", device_name: "\u542F\u660E\u661F\u8FB9\u754C\u9632\u706B\u5899", subject: "CN=venus.local, O=Venustech", issuer: "CN=venus.local, O=Venustech", serial: "00:11:22:33:44:55", valid_from: "2022-01-01T00:00:00Z", valid_to: "2025-12-31T00:00:00Z", status: "expired", is_self_signed: true, key_size: 1024, signature_algorithm: "SHA1withRSA", san: ["venus.local", "10.0.5.100"], imported: true, trusted: false },
];

const httpItems: HTTPInspItem[] = [
  { id: "hi-001", device_id: "http-dev-001", name: "\u7CFB\u7EDF\u7248\u672C\u4FE1\u606F", category: "\u7CFB\u7EDF\u4FE1\u606F", method: "GET", url_path: "/api/v1/sys/info", request_body: "", content_type: "application/json", parser_type: "json_path", parser_expression: "$.data.version", threshold: null, is_read_only: true, weight: 5, order: 1 },
  { id: "hi-002", device_id: "http-dev-001", name: "CPU\u4F7F\u7528\u7387", category: "\u6027\u80FD\u76D1\u63A7", method: "GET", url_path: "/api/v1/monitor/cpu", request_body: "", content_type: "application/json", parser_type: "json_path", parser_expression: "$.data.usage_percent", threshold: { operator: "gt", critical: 90, warning: 70, unit: "%" }, is_read_only: true, weight: 20, order: 2 },
  { id: "hi-003", device_id: "http-dev-001", name: "\u5185\u5B58\u4F7F\u7528\u7387", category: "\u6027\u80FD\u76D1\u63A7", method: "GET", url_path: "/api/v1/monitor/memory", request_body: "", content_type: "application/json", parser_type: "json_path", parser_expression: "$.data.usage_percent", threshold: { operator: "gt", critical: 90, warning: 80, unit: "%" }, is_read_only: true, weight: 20, order: 3 },
  { id: "hi-004", device_id: "http-dev-001", name: "\u5B89\u5168\u7B56\u7565\u72B6\u6001", category: "\u5B89\u5168\u7B56\u7565", method: "GET", url_path: "/api/v1/security/policy/status", request_body: "", content_type: "application/json", parser_type: "json_path", parser_expression: "$.data.active_policies", threshold: null, is_read_only: true, weight: 15, order: 4 },
  { id: "hi-005", device_id: "http-dev-001", name: "\u8BC1\u4E66\u72B6\u6001", category: "\u8BC1\u4E66\u72B6\u6001", method: "GET", url_path: "/api/v1/sys/cert/status", request_body: "", content_type: "application/json", parser_type: "json_path", parser_expression: "$.data.cert_valid", threshold: null, is_read_only: true, weight: 10, order: 5 },
  { id: "hi-006", device_id: "http-dev-003", name: "\u7CFB\u7EDF\u72B6\u6001\u6458\u8981", category: "\u7CFB\u7EDF\u4FE1\u606F", method: "GET", url_path: "/api/system/status", request_body: "", content_type: "application/json", parser_type: "json_path", parser_expression: "$.result.status", threshold: null, is_read_only: true, weight: 10, order: 1 },
  { id: "hi-007", device_id: "http-dev-003", name: "\u5F53\u524D\u4F1A\u8BDD\u6570", category: "\u6027\u80FD\u76D1\u63A7", method: "GET", url_path: "/api/system/sessions", request_body: "", content_type: "application/json", parser_type: "json_path", parser_expression: "$.result.active_sessions", threshold: { operator: "gt", critical: 10000, warning: 5000, unit: "\u4F1A\u8BDD" }, is_read_only: true, weight: 15, order: 2 },
  { id: "hi-008", device_id: "http-dev-003", name: "\u5A01\u80C1\u65E5\u5FD7\u7EDF\u8BA1", category: "\u65E5\u5FD7\u5BA1\u8BA1", method: "POST", url_path: "/api/log/threat/query", request_body: '{"time_range":"24h","limit":10}', content_type: "application/json", parser_type: "json_path", parser_expression: "$.result.total_count", threshold: { operator: "gt", critical: 1000, warning: 100, unit: "\u6761" }, is_read_only: true, weight: 20, order: 3 },
  { id: "hi-ss-1", device_id: "http-dev-001", name: "\u7BA1\u7406\u754C\u9762\u603B\u89C8", category: "\u622A\u56FE\u5DE1\u68C0", method: "GET", url_path: "/", request_body: "", content_type: "", parser_type: "screenshot", parser_expression: "", threshold: null, is_read_only: true, weight: 5, order: 10, screenshot_config: { url_path: "/", navigation_mode: "url", menu_selectors: [], wait_condition: "networkidle", wait_timeout: 10, wait_selector: "", capture_area: "full_page", capture_selector: "", viewport_width: 1920, viewport_height: 1080, word_template_position: "3.1", word_section_title: "\u8BBE\u5907\u72B6\u6001\u603B\u89C8" } },
  { id: "hi-ss-2", device_id: "http-dev-001", name: "\u5B89\u5168\u7B56\u7565\u9875\u9762", category: "\u622A\u56FE\u5DE1\u68C0", method: "GET", url_path: "/security/policy", request_body: "", content_type: "", parser_type: "screenshot", parser_expression: "", threshold: null, is_read_only: true, weight: 5, order: 11, screenshot_config: { url_path: "/security/policy", navigation_mode: "menu", menu_selectors: ["a[href*='security']", "a[href*='policy']"], wait_condition: "selector", wait_timeout: 8, wait_selector: ".policy-table", capture_area: "selector", capture_selector: ".policy-table", viewport_width: 1920, viewport_height: 1080, word_template_position: "3.2", word_section_title: "\u5B89\u5168\u7B56\u7565\u72B6\u6001" } },
  { id: "hi-ss-3", device_id: "http-dev-001", name: "\u7CFB\u7EDF\u65E5\u5FD7\u9875\u9762", category: "\u622A\u56FE\u5DE1\u68C0", method: "GET", url_path: "/log/system", request_body: "", content_type: "", parser_type: "screenshot", parser_expression: "", threshold: null, is_read_only: true, weight: 5, order: 12, screenshot_config: { url_path: "/log/system", navigation_mode: "menu", menu_selectors: ["a[href*='log']", "a[href*='system']"], wait_condition: "networkidle", wait_timeout: 10, wait_selector: "", capture_area: "viewport", capture_selector: "", viewport_width: 1920, viewport_height: 1080, word_template_position: "3.3", word_section_title: "\u7CFB\u7EDF\u65E5\u5FD7" } },
];

const httpLogs: HTTPExecLog[] = [
  { id: "log-001", device_id: "http-dev-001", device_name: "\u603B\u90E8\u9632\u706B\u5899-USG6625", started_at: ago(2), completed_at: ago(1.9), status: "completed", total_items: 5, completed_items: 5, ok_count: 4, warning_count: 1, critical_count: 0, error_count: 0, cert_warning: null },
  { id: "log-002", device_id: "http-dev-001", device_name: "\u603B\u90E8\u9632\u706B\u5899-USG6625", started_at: ago(26), completed_at: ago(25.9), status: "completed", total_items: 5, completed_items: 5, ok_count: 5, warning_count: 0, critical_count: 0, error_count: 0, cert_warning: null },
  { id: "log-003", device_id: "http-dev-003", device_name: "\u8001\u65E7\u9632\u706B\u5899-TopSec", started_at: ago(3), completed_at: ago(2.8), status: "partial", total_items: 3, completed_items: 2, ok_count: 1, warning_count: 1, critical_count: 0, error_count: 1, cert_warning: "\u8BC1\u4E66\u5373\u5C06\u8FC7\u671F\uFF0C\u5EFA\u8BAE\u5C3D\u5FEB\u66F4\u65B0" },
  { id: "log-004", device_id: "http-dev-005", device_name: "\u542F\u660E\u661F\u8FB9\u754C\u9632\u706B\u5899", started_at: ago(48), completed_at: ago(47.9), status: "failed", total_items: 0, completed_items: 0, ok_count: 0, warning_count: 0, critical_count: 0, error_count: 1, cert_warning: "SSL\u8BC1\u4E66\u5DF2\u8FC7\u671F\uFF0C\u65E0\u6CD5\u5EFA\u7ACB\u5B89\u5168\u8FDE\u63A5" },
];

const httpScreenshots: Array<Record<string, unknown>> = [
  { id: "ss-001", device_id: "http-dev-001", device_name: "\u603B\u90E8\u9632\u706B\u5899-USG6625", item_id: "hi-ss-1", item_name: "\u7BA1\u7406\u754C\u9762\u603B\u89C8", url: "https://10.0.1.254:443/", captured_at: ago(2), width: 1920, height: 1080, file_size: 245760, thumbnail_url: "", status: "success", error_message: null, login_page: false, full_page: true },
  { id: "ss-002", device_id: "http-dev-001", device_name: "\u603B\u90E8\u9632\u706B\u5899-USG6625", item_id: "hi-ss-2", item_name: "\u767B\u5F55\u9875\u9762", url: "https://10.0.1.254:443/api/v1/sys/user/login", captured_at: ago(2), width: 1920, height: 1080, file_size: 189440, thumbnail_url: "", status: "success", error_message: null, login_page: true, full_page: false },
  { id: "ss-003", device_id: "http-dev-001", device_name: "\u603B\u90E8\u9632\u706B\u5899-USG6625", item_id: "hi-ss-3", item_name: "\u5B89\u5168\u7B56\u7565\u6982\u89C8", url: "https://10.0.1.254:443/policy/overview", captured_at: ago(2), width: 1920, height: 2400, file_size: 512000, thumbnail_url: "", status: "success", error_message: null, login_page: false, full_page: true },
  { id: "ss-004", device_id: "http-dev-002", device_name: "\u8FB9\u754C\u5B89\u5168\u7F51\u5173-Sangfor", item_id: "hi-ss-4", item_name: "\u5B89\u5168\u6001\u52BF\u4EEA\u8868\u76D8", url: "https://10.0.2.10:443/", captured_at: ago(5), width: 1920, height: 1080, file_size: 312320, thumbnail_url: "", status: "success", error_message: null, login_page: false, full_page: false },
  { id: "ss-005", device_id: "http-dev-002", device_name: "\u8FB9\u754C\u5B89\u5168\u7F51\u5173-Sangfor", item_id: "hi-ss-5", item_name: "\u5A01\u80C1\u65E5\u5FD7\u9875\u9762", url: "https://10.0.2.10:443/log/threat", captured_at: ago(5), width: 1920, height: 1080, file_size: 278400, thumbnail_url: "", status: "success", error_message: null, login_page: false, full_page: false },
  { id: "ss-006", device_id: "http-dev-003", device_name: "\u8001\u65E7\u9632\u706B\u5899-TopSec", item_id: "hi-ss-6", item_name: "\u7CFB\u7EDF\u72B6\u6001\u9875\u9762", url: "https://topsec.local:443/status.html", captured_at: ago(3), width: 1024, height: 768, file_size: 156672, thumbnail_url: "", status: "success", error_message: null, login_page: false, full_page: false },
  { id: "ss-007", device_id: "http-dev-003", device_name: "\u8001\u65E7\u9632\u706B\u5899-TopSec", item_id: "hi-ss-7", item_name: "\u8BBF\u95EE\u63A7\u5236\u7B56\u7565", url: "https://topsec.local:443/acl.html", captured_at: ago(3), width: 0, height: 0, file_size: 0, thumbnail_url: "", status: "failed", error_message: "\u9875\u9762\u52A0\u8F7D\u8D85\u65F6\uFF0C\u8BBE\u5907\u54CD\u5E94\u8FC7\u6162", login_page: false, full_page: false },
  { id: "ss-008", device_id: "http-dev-005", device_name: "\u542F\u660E\u661F\u8FB9\u754C\u9632\u706B\u5899", item_id: "hi-ss-8", item_name: "\u7CFB\u7EDF\u4EEA\u8868\u76D8", url: "https://10.0.5.10:443/", captured_at: ago(26), width: 1920, height: 1080, file_size: 298880, thumbnail_url: "", status: "success", error_message: null, login_page: false, full_page: true },
];

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

  // ============================================================
  // HTTP Integration Routes
  // ============================================================
  if (path.startsWith('http-integration/')) {
    const sub = path.replace('http-integration/', '');

    // GET /api/v1/http-integration/devices
    if (sub === 'devices' && method === 'GET') {
      return NextResponse.json(httpDevices);
    }

    // POST /api/v1/http-integration/devices
    if (sub === 'devices' && method === 'POST') {
      const body = await request.json();
      const newDev: HTTPDeviceData = {
        id: `http-dev-${String(httpDevices.length + 1).padStart(3, '0')}`,
        name: body.name || '', brand: body.brand || 'generic', model: body.model || '',
        base_url: body.base_url || '', port: body.port || 443,
        use_https: body.use_https !== false, auth_type: body.auth_type || 'form',
        username: body.username || '', password_enc: body.password_enc || '',
        login_url: body.login_url || '', username_field: body.username_field || '',
        password_field: body.password_field || '', submit_selector: body.submit_selector || '',
        tls_min_version: body.tls_min_version || 'TLSv1.2', tls_max_version: body.tls_max_version || 'TLSv1.3',
        verify_cert: body.verify_cert !== false, accept_self_signed: body.accept_self_signed || false,
        custom_headers: body.custom_headers || {}, cipher_suites: body.cipher_suites || [],
        timeout: body.timeout || 30, status: 'disconnected', cert_status: 'unknown',
        cert_expiry: null, last_check: null, compat_mode: body.compat_mode || false,
        tags: body.tags || [], created_at: new Date().toISOString(),
      };
      httpDevices.push(newDev);
      return NextResponse.json(newDev);
    }

    // DELETE /api/v1/http-integration/devices/:id
    if (sub.startsWith('devices/') && method === 'DELETE') {
      const id = sub.replace('devices/', '').split('/')[0];
      const idx = httpDevices.findIndex(d => d.id === id);
      if (idx >= 0) httpDevices.splice(idx, 1);
      return NextResponse.json({ success: true });
    }

    // POST /api/v1/http-integration/devices/:id/test
    if (sub.includes('/test') && method === 'POST') {
      const id = sub.split('/')[1];
      const dev = httpDevices.find(d => d.id === id);
      if (!dev) return NextResponse.json({ error: '设备不存在' }, { status: 404 });
      const statuses: Array<'connected' | 'error'> = ['connected', 'connected', 'connected', 'error'];
      const certStatuses: Array<'valid' | 'expiring' | 'expired' | 'self_signed'> = ['valid', 'self_signed', 'expiring', 'expired'];
      dev.status = statuses[Math.floor(Math.random() * statuses.length)];
      dev.cert_status = certStatuses[Math.floor(Math.random() * certStatuses.length)];
      dev.last_check = new Date().toISOString();
      return NextResponse.json({ success: true, status: dev.status, cert_status: dev.cert_status, latency_ms: Math.floor(Math.random() * 200) + 50, tls_version: dev.tls_min_version, cert_info: { subject: dev.base_url, issuer: dev.accept_self_signed ? 'Self-signed' : 'CA', valid: dev.cert_status !== 'expired' } });
    }

    // POST /api/v1/http-integration/devices/:id/run
    if (sub.includes('/run') && method === 'POST') {
      const id = sub.split('/')[1];
      const dev = httpDevices.find(d => d.id === id);
      if (!dev) return NextResponse.json({ error: '设备不存在' }, { status: 404 });
      const devItems = httpItems.filter(i => i.device_id === id);
      const log: HTTPExecLog = {
        id: `log-${String(httpLogs.length + 1).padStart(3, '0')}`, device_id: id, device_name: dev.name,
        started_at: new Date().toISOString(), completed_at: new Date(Date.now() + 5000).toISOString(),
        status: 'completed', total_items: devItems.length, completed_items: devItems.length,
        ok_count: Math.floor(devItems.length * 0.8), warning_count: Math.floor(devItems.length * 0.15),
        critical_count: Math.floor(devItems.length * 0.05), error_count: 0,
        cert_warning: dev.cert_status === 'expired' ? 'SSL证书已过期' : dev.cert_status === 'expiring' ? '证书即将过期，建议尽快更新' : null,
      };
      httpLogs.unshift(log);
      return NextResponse.json({ success: true, log_id: log.id });
    }

    // GET /api/v1/http-integration/certs
    if (sub === 'certs' && method === 'GET') {
      return NextResponse.json(httpCerts);
    }

    // POST /api/v1/http-integration/certs
    if (sub === 'certs' && method === 'POST') {
      const body = await request.json();
      const newCert: SSLCertData = {
        id: `cert-${String(httpCerts.length + 1).padStart(3, '0')}`,
        device_id: body.device_id, device_name: body.device_name || '',
        subject: `CN=${body.device_id}, O=Imported`, issuer: 'Imported CA',
        serial: Array.from({ length: 6 }, () => Math.floor(Math.random() * 256).toString(16).toUpperCase().padStart(2, '0')).join(':'),
        valid_from: new Date().toISOString(), valid_to: new Date(Date.now() + 365 * 86400000).toISOString(),
        status: 'valid', is_self_signed: false, key_size: 2048, signature_algorithm: 'SHA256withRSA',
        san: [], imported: true, trusted: body.trusted !== false,
      };
      httpCerts.push(newCert);
      return NextResponse.json(newCert);
    }

    // GET /api/v1/http-integration/items
    if (sub === 'items' && method === 'GET') {
      return NextResponse.json(httpItems);
    }

    // POST /api/v1/http-integration/items
    if (sub === 'items' && method === 'POST') {
      const body = await request.json();
      const newItem: HTTPInspItem = {
        id: `hi-${String(httpItems.length + 1).padStart(3, '0')}`,
        device_id: body.device_id, name: body.name || '', category: body.category || '\u7CFB\u7EDF\u4FE1\u606F',
        method: body.method || 'GET', url_path: body.url_path || '',
        request_body: body.request_body || '', content_type: body.content_type || 'application/json',
        parser_type: body.parser_type || 'json_path', parser_expression: body.parser_expression || '',
        threshold: body.threshold || null, is_read_only: body.is_read_only !== false,
        weight: body.weight || 10, order: body.order || httpItems.length + 1,
      };
      httpItems.push(newItem);
      return NextResponse.json(newItem);
    }

    // GET /api/v1/http-integration/logs
    if (sub === 'logs' && method === 'GET') {
      return NextResponse.json(httpLogs);
    }

    // GET /api/v1/http-integration/screenshots
    if (sub === 'screenshots' && method === 'GET') {
      return NextResponse.json(httpScreenshots);
    }

    // POST /api/v1/http-integration/devices/:id/capture
    const captureMatch = sub.match(/^devices\/([^/]+)\/capture$/);
    if (captureMatch && method === 'POST') {
      const dev = httpDevices.find(d => d.id === captureMatch[1]);
      if (!dev) return NextResponse.json({ error: 'Device not found' }, { status: 404 });
      const newScreenshots = [
        { id: `ss-${Date.now()}-1`, device_id: dev.id, device_name: dev.name, item_id: 'hi-ss-1', item_name: '\u7BA1\u7406\u754C\u9762\u603B\u89C8', url: `${dev.use_https ? 'https' : 'http'}://${dev.base_url}:${dev.port}/`, captured_at: new Date().toISOString(), width: 1920, height: 1080, file_size: 245760, thumbnail_url: '', status: 'success' as const, error_message: null, login_page: false, full_page: true },
        { id: `ss-${Date.now()}-2`, device_id: dev.id, device_name: dev.name, item_id: 'hi-ss-2', item_name: '\u767B\u5F55\u9875\u9762', url: `${dev.use_https ? 'https' : 'http'}://${dev.base_url}:${dev.port}${dev.login_url || '/login'}`, captured_at: new Date().toISOString(), width: 1920, height: 1080, file_size: 189440, thumbnail_url: '', status: 'success' as const, error_message: null, login_page: true, full_page: false },
      ];
      httpScreenshots.unshift(...newScreenshots);
      return NextResponse.json({ success: true, captured: newScreenshots.length });
    }
  }

  return NextResponse.json({ error: `Not found: ${method} ${path}` }, { status: 404 });
}

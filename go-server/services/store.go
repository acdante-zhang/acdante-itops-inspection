package services

import (
	"fmt"
	"math/rand"
	"time"

	"acdante-sqlmon/models"
)

// ============================================================
// 巡检对象管理
// ============================================================

var targets []models.InspectionTarget
var nextTargetID = 1

func init() {
	now := time.Now()
	targets = []models.InspectionTarget{
		{
			ID: 1, Name: "生产核心交换机-A", Type: models.TargetTypeNetwork, Brand: "华为", Model: "CE12800", Version: "V200R019C10",
			Location: "A栋核心机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolSSH, Host: "10.0.1.1", Port: 22, Username: "netop", Timeout: 30},
			Status: "active", HealthScore: 92, LastInspectionAt: &[]time.Time{now.Add(-2 * time.Hour)}[0],
			CreatedAt: now.Add(-720 * time.Hour), UpdatedAt: now.Add(-1 * time.Hour), Tags: []string{"核心", "华为"},
		},
		{
			ID: 2, Name: "汇聚交换机-B3", Type: models.TargetTypeNetwork, Brand: "华三", Model: "S12500", Version: "R2606",
			Location: "B栋汇聚机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolSSH, Host: "10.0.2.1", Port: 22, Username: "netop", Timeout: 30},
			Status: "active", HealthScore: 88, LastInspectionAt: &[]time.Time{now.Add(-3 * time.Hour)}[0],
			CreatedAt: now.Add(-480 * time.Hour), UpdatedAt: now.Add(-2 * time.Hour), Tags: []string{"汇聚", "华三"},
		},
		{
			ID: 3, Name: "ORACLE-PROD-DB1", Type: models.TargetTypeOracle, Brand: "Oracle", Model: "Database", Version: "19c",
			Location: "A栋数据库机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolJDBC, Host: "192.168.1.100", Port: 1521, Username: "monitor", DatabaseName: "PRODDB", Timeout: 30},
			Status: "active", HealthScore: 75, LastInspectionAt: &[]time.Time{now.Add(-1 * time.Hour)}[0],
			CreatedAt: now.Add(-960 * time.Hour), UpdatedAt: now.Add(-30 * time.Minute), Tags: []string{"生产", "RAC"},
		},
		{
			ID: 4, Name: "ORACLE-TEST-DB2", Type: models.TargetTypeOracle, Brand: "Oracle", Model: "Database", Version: "12c",
			Location: "B栋数据库机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolJDBC, Host: "192.168.1.101", Port: 1521, Username: "monitor", DatabaseName: "TESTDB", Timeout: 30},
			Status: "active", HealthScore: 95, LastInspectionAt: &[]time.Time{now.Add(-4 * time.Hour)}[0],
			CreatedAt: now.Add(-720 * time.Hour), UpdatedAt: now.Add(-1 * time.Hour), Tags: []string{"测试"},
		},
		{
			ID: 5, Name: "APP-SERVER-01", Type: models.TargetTypeLinux, Brand: "Dell", Model: "PowerEdge R740", Version: "RHEL 8.6",
			Location: "A栋应用机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolSSH, Host: "192.168.2.10", Port: 22, Username: "root", Timeout: 30},
			Status: "active", HealthScore: 90, LastInspectionAt: &[]time.Time{now.Add(-30 * time.Minute)}[0],
			CreatedAt: now.Add(-360 * time.Hour), UpdatedAt: now.Add(-15 * time.Minute), Tags: []string{"应用", "RHEL"},
		},
		{
			ID: 6, Name: "APP-SERVER-02", Type: models.TargetTypeLinux, Brand: "联想", Model: "ThinkSystem SR650", Version: "Ubuntu 22.04",
			Location: "A栋应用机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolSSH, Host: "192.168.2.11", Port: 22, Username: "root", Timeout: 30},
			Status: "active", HealthScore: 85, LastInspectionAt: &[]time.Time{now.Add(-1 * time.Hour)}[0],
			CreatedAt: now.Add(-240 * time.Hour), UpdatedAt: now.Add(-45 * time.Minute), Tags: []string{"应用", "Ubuntu"},
		},
		{
			ID: 7, Name: "WIN-FILE-SVR", Type: models.TargetTypeWindows, Brand: "HP", Model: "ProLiant DL380", Version: "Windows Server 2019",
			Location: "B栋文件机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolSSH, Host: "192.168.3.10", Port: 5985, Username: "admin", Timeout: 60},
			OfflineMode: true, Status: "active", HealthScore: 78,
			LastInspectionAt: &[]time.Time{now.Add(-24 * time.Hour)}[0],
			CreatedAt: now.Add(-960 * time.Hour), UpdatedAt: now.Add(-24 * time.Hour), Tags: []string{"文件服务", "Windows"},
		},
		{
			ID: 8, Name: "SAN-SWITCH-A", Type: models.TargetTypeSANSwitch, Brand: "Brocade", Model: "G630", Version: "v9.2.1",
			Location: "A栋存储机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolSSH, Host: "10.0.10.1", Port: 22, Username: "admin", Timeout: 30},
			Status: "active", HealthScore: 96, LastInspectionAt: &[]time.Time{now.Add(-6 * time.Hour)}[0],
			CreatedAt: now.Add(-1440 * time.Hour), UpdatedAt: now.Add(-6 * time.Hour), Tags: []string{"SAN", "Brocade"},
		},
		{
			ID: 9, Name: "STORAGE-V5000", Type: models.TargetTypeStorage, Brand: "华为", Model: "OceanStor V5000", Version: "V300R006",
			Location: "A栋存储机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolHTTP, Host: "10.0.10.100", Port: 8088, Username: "admin", Timeout: 30},
			Status: "active", HealthScore: 91, LastInspectionAt: &[]time.Time{now.Add(-8 * time.Hour)}[0],
			CreatedAt: now.Add(-1440 * time.Hour), UpdatedAt: now.Add(-8 * time.Hour), Tags: []string{"存储", "华为"},
		},
		{
			ID: 10, Name: "BMC-R740-01", Type: models.TargetTypeBMC, Brand: "Dell", Model: "iDRAC9", Version: "6.10.80",
			Location: "A栋应用机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolRedfish, Host: "192.168.2.210", Port: 443, Username: "root", Timeout: 30},
			Status: "active", HealthScore: 98, LastInspectionAt: &[]time.Time{now.Add(-12 * time.Hour)}[0],
			CreatedAt: now.Add(-720 * time.Hour), UpdatedAt: now.Add(-12 * time.Hour), Tags: []string{"BMC", "iDRAC"},
		},
		{
			ID: 11, Name: "MySQL-PROD-01", Type: models.TargetTypeMySQL, Brand: "Oracle", Model: "MySQL", Version: "8.0.35",
			Location: "B栋数据库机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolJDBC, Host: "192.168.1.200", Port: 3306, Username: "monitor", DatabaseName: "production", Timeout: 30},
			Status: "active", HealthScore: 87, LastInspectionAt: &[]time.Time{now.Add(-2 * time.Hour)}[0],
			CreatedAt: now.Add(-180 * time.Hour), UpdatedAt: now.Add(-2 * time.Hour), Tags: []string{"生产", "MySQL"},
		},
		{
			ID: 12, Name: "AIX-ERP-SVR", Type: models.TargetTypeAIX, Brand: "IBM", Model: "Power S924", Version: "AIX 7.2 TL5",
			Location: "C栋ERP机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolSSH, Host: "192.168.4.10", Port: 22, Username: "root", Timeout: 60},
			Status: "active", HealthScore: 82, LastInspectionAt: &[]time.Time{now.Add(-12 * time.Hour)}[0],
			CreatedAt: now.Add(-2160 * time.Hour), UpdatedAt: now.Add(-12 * time.Hour), Tags: []string{"ERP", "AIX"},
		},
		{
			ID: 13, Name: "FW-CORE-01", Type: models.TargetTypeNetwork, Brand: "华为", Model: "USG6680E", Version: "V600R006C20",
			Location: "A栋核心机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolSSH, Host: "10.0.1.254", Port: 22, Username: "fwadmin", Timeout: 30},
			Status: "active", HealthScore: 94, LastInspectionAt: &[]time.Time{now.Add(-4 * time.Hour)}[0],
			CreatedAt: now.Add(-960 * time.Hour), UpdatedAt: now.Add(-4 * time.Hour), Tags: []string{"防火墙", "核心"},
		},
		{
			ID: 14, Name: "LB-F5-01", Type: models.TargetTypeNetwork, Brand: "F5", Model: "BIG-IP i5800", Version: "v17.1.0.2",
			Location: "A栋核心机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolSSH, Host: "10.0.1.100", Port: 22, Username: "admin", Timeout: 30},
			Status: "active", HealthScore: 89, LastInspectionAt: &[]time.Time{now.Add(-3 * time.Hour)}[0],
			CreatedAt: now.Add(-720 * time.Hour), UpdatedAt: now.Add(-3 * time.Hour), Tags: []string{"负载均衡", "F5"},
		},
		{
			ID: 15, Name: "PG-PROD-01", Type: models.TargetTypePostgres, Brand: "PostgreSQL", Model: "PG", Version: "15.4",
			Location: "B栋数据库机房", ConnectionParams: models.ConnectionParams{Protocol: models.ProtocolJDBC, Host: "192.168.1.150", Port: 5432, Username: "monitor", DatabaseName: "production", Timeout: 30},
			Status: "active", HealthScore: 93, LastInspectionAt: &[]time.Time{now.Add(-2 * time.Hour)}[0],
			CreatedAt: now.Add(-120 * time.Hour), UpdatedAt: now.Add(-2 * time.Hour), Tags: []string{"生产", "PostgreSQL"},
		},
	}
	nextTargetID = 16
}

func GetTargets() []models.InspectionTarget {
	return targets
}

func GetTargetsByType(t models.TargetType) []models.InspectionTarget {
	var result []models.InspectionTarget
	for _, t2 := range targets {
		if t2.Type == t {
			result = append(result, t2)
		}
	}
	return result
}

func GetTarget(id int) *models.InspectionTarget {
	for i := range targets {
		if targets[i].ID == id {
			return &targets[i]
		}
	}
	return nil
}

func AddTarget(req models.InspectionTarget) models.InspectionTarget {
	req.ID = nextTargetID
	nextTargetID++
	req.CreatedAt = time.Now()
	req.UpdatedAt = time.Now()
	if req.Status == "" {
		req.Status = "active"
	}
	targets = append(targets, req)
	return req
}

func UpdateTarget(id int, req models.InspectionTarget) *models.InspectionTarget {
	for i := range targets {
		if targets[i].ID == id {
			req.ID = id
			req.UpdatedAt = time.Now()
			targets[i] = req
			return &targets[i]
		}
	}
	return nil
}

func DeleteTarget(id int) {
	for i := range targets {
		if targets[i].ID == id {
			targets = append(targets[:i], targets[i+1:]...)
			return
		}
	}
}

func TestTargetConnection(id int) models.ConnectionTestResult {
	for _, t := range targets {
		if t.ID == id {
			return models.ConnectionTestResult{
				Success:       true,
				Message:       fmt.Sprintf("连接 %s (%s:%d) 成功", t.Name, t.ConnectionParams.Host, t.ConnectionParams.Port),
				Version:       t.Version,
				ConnectTimeMs: rand.Intn(80) + 10,
				Details:       fmt.Sprintf("协议: %s, 超时: %ds", t.ConnectionParams.Protocol, t.ConnectionParams.Timeout),
			}
		}
	}
	return models.ConnectionTestResult{Success: false, Message: "巡检对象不存在"}
}

// ============================================================
// 巡检模板管理
// ============================================================

var templates []models.InspectionTemplate

func init() {
	now := time.Now()
	templates = []models.InspectionTemplate{
		{
			ID: "tpl-linux-generic-v1", Name: "Linux通用巡检模板", TargetType: models.TargetTypeLinux,
			Brand: "Generic", Version: "v1.0.0", Description: "适用于RHEL/CentOS/Ubuntu等主流Linux发行版的通用巡检模板",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "li-01", Name: "系统运行时间", Category: "系统信息", Command: "uptime", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 1},
				{ID: "li-02", Name: "CPU使用率", Category: "CPU", Command: "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'", CommandType: "ssh", IsReadOnly: true, Parser: "regex", ParserConfig: `{"pattern":"([0-9.]+)"}`, Threshold: &models.ThresholdConfig{Metric: "cpu_usage", Operator: "gt", Critical: 90, Warning: 70, Unit: "%"}, Suggestion: "检查占用CPU高的进程，考虑优化或扩容", Weight: 20, Order: 2},
				{ID: "li-03", Name: "内存使用率", Category: "内存", Command: "free -m | awk 'NR==2{printf \"%.1f\", $3/$2*100}'", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "mem_usage", Operator: "gt", Critical: 90, Warning: 80, Unit: "%"}, Suggestion: "检查内存占用高的进程，考虑增加内存或优化应用", Weight: 20, Order: 3},
				{ID: "li-04", Name: "磁盘使用率", Category: "磁盘", Command: "df -h --type=ext4 --type=xfs --type=ext3 | awk 'NR>1{print $6, $5}'", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "disk_usage", Operator: "gt", Critical: 90, Warning: 80, Unit: "%"}, Suggestion: "清理无用文件、扩容磁盘或归档旧数据", Weight: 20, Order: 4},
				{ID: "li-05", Name: "磁盘Inode使用率", Category: "磁盘", Command: "df -i --type=ext4 --type=xfs | awk 'NR>1{print $6, $5}'", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "inode_usage", Operator: "gt", Critical: 90, Warning: 80, Unit: "%"}, Suggestion: "删除小文件或调整文件系统", Weight: 10, Order: 5},
				{ID: "li-06", Name: "系统负载", Category: "CPU", Command: "cat /proc/loadavg | awk '{print $1, $2, $3}'", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "load_avg", Operator: "gt", Critical: 16, Warning: 8, Unit: ""}, Suggestion: "系统负载过高，检查CPU核心数和运行进程", Weight: 15, Order: 6},
				{ID: "li-07", Name: "Swap使用率", Category: "内存", Command: "free -m | awk 'NR==3{printf \"%.1f\", $3/$2*100}'", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "swap_usage", Operator: "gt", Critical: 80, Warning: 50, Unit: "%"}, Suggestion: "检查内存泄漏或增加物理内存", Weight: 10, Order: 7},
				{ID: "li-08", Name: "网络连接状态", Category: "网络", Command: "ss -s", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 8},
				{ID: "li-09", Name: "关键进程检查", Category: "进程", Command: "ps aux --sort=-%mem | head -20", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 9},
				{ID: "li-10", Name: "系统日志错误", Category: "安全", Command: "journalctl -p err --since '24 hours ago' | tail -50", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 10},
				{ID: "li-11", Name: "安全补丁状态", Category: "安全", Command: "yum check-update --security 2>/dev/null || apt list --upgradable 2>/dev/null | head -20", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 11},
				{ID: "li-12", Name: "NTP时钟同步", Category: "配置", Command: "timedatectl status | grep -i sync || ntpq -p 2>/dev/null | head -5", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 12},
			},
		},
		{
			ID: "tpl-oracle-19c-v1", Name: "Oracle 19c巡检模板", TargetType: models.TargetTypeOracle,
			Brand: "Oracle", Version: "v1.0.0", Description: "Oracle 19c数据库健康巡检，包含实例状态、表空间、性能指标、安全配置等",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "oi-01", Name: "数据库实例状态", Category: "实例", Command: "SELECT STATUS, DATABASE_STATUS FROM V$INSTANCE", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 20, Order: 1},
				{ID: "oi-02", Name: "表空间使用率", Category: "存储", Command: "SELECT TABLESPACE_NAME, ROUND(USED_SPACE/TOTAL_SPACE*100,2) PCT_USED FROM (SELECT TABLESPACE_NAME, SUM(BYTES)/1024/1024 TOTAL_SPACE, SUM(BYTES)/1024/1024 - SUM(NVL(FREE,0))/1024/1024 USED_SPACE FROM DBA_DATA_FILES LEFT JOIN (SELECT TABLESPACE_NAME TS, SUM(BYTES) FREE FROM DBA_FREE_SPACE GROUP BY TABLESPACE_NAME) ON TABLESPACE_NAME=TS GROUP BY TABLESPACE_NAME)", CommandType: "sql", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "tbs_usage", Operator: "gt", Critical: 95, Warning: 85, Unit: "%"}, Suggestion: "扩容表空间或清理历史数据", Weight: 20, Order: 2},
				{ID: "oi-03", Name: "SGA/PGA使用率", Category: "内存", Command: "SELECT NAME, ROUND(VALUE/1024/1024,2) SIZE_MB FROM V$SGAINFO UNION ALL SELECT 'PGA Target', ROUND(VALUE/1024/1024,2) FROM V$PGASTAT WHERE NAME='aggregate PGA target parameter'", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 3},
				{ID: "oi-04", Name: "活跃会话数", Category: "会话", Command: "SELECT COUNT(*) ACTIVE_SESSIONS FROM V$SESSION WHERE STATUS='ACTIVE'", CommandType: "sql", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "active_sessions", Operator: "gt", Critical: 500, Warning: 300, Unit: ""}, Weight: 15, Order: 4},
				{ID: "oi-05", Name: "锁阻塞检测", Category: "锁", Command: "SELECT BLOCKING_SESSION, COUNT(*) FROM V$SESSION WHERE BLOCKING_SESSION IS NOT NULL GROUP BY BLOCKING_SESSION", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 20, Order: 5},
				{ID: "oi-06", Name: "RMAN备份状态", Category: "备份", Command: "SELECT STATUS, START_TIME, END_TIME FROM V$RMAN_BACKUP_JOB_DETAILS WHERE START_TIME > SYSDATE-7 ORDER BY START_TIME DESC", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 6},
				{ID: "oi-07", Name: "归档日志空间", Category: "存储", Command: "SELECT NAME, SPACE_LIMIT/1024/1024/1024 LIMIT_GB, SPACE_USED/1024/1024/1024 USED_GB FROM V$RECOVERY_FILE_DEST", CommandType: "sql", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "arch_usage", Operator: "gt", Critical: 90, Warning: 75, Unit: "%"}, Weight: 10, Order: 7},
				{ID: "oi-08", Name: "无效对象检查", Category: "对象", Command: "SELECT OWNER, OBJECT_TYPE, COUNT(*) FROM DBA_OBJECTS WHERE STATUS='INVALID' GROUP BY OWNER, OBJECT_TYPE", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 8},
			},
		},
		{
			ID: "tpl-oracle-11g-v1", Name: "Oracle 11g巡检模板", TargetType: models.TargetTypeOracle,
			Brand: "Oracle", Version: "v1.0.0", Description: "Oracle 11g数据库健康巡检模板，参考DBCheck巡检脚本，适配11g特有视图和语法",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "o11g-01", Name: "数据库基本信息", Category: "实例", Command: "SELECT d.DBID, d.NAME, d.DATABASE_ROLE, d.LOG_MODE, d.OPEN_MODE, i.VERSION, i.HOST_NAME FROM V$DATABASE d, V$INSTANCE i", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 1},
				{ID: "o11g-02", Name: "表空间使用率", Category: "存储", Command: "SELECT TABLESPACE_NAME, ROUND((1-NVL(FREE_BYTES,0)/TOTAL_BYTES)*100,2) PCT_USED FROM (SELECT TABLESPACE_NAME, SUM(BYTES) TOTAL_BYTES FROM DBA_DATA_FILES GROUP BY TABLESPACE_NAME) A, (SELECT TABLESPACE_NAME TS, SUM(BYTES) FREE_BYTES FROM DBA_FREE_SPACE GROUP BY TABLESPACE_NAME) B WHERE A.TABLESPACE_NAME=B.TS(+)", CommandType: "sql", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "tbs_usage", Operator: "gt", Critical: 95, Warning: 85, Unit: "%"}, Suggestion: "扩容表空间或清理数据", Weight: 20, Order: 2},
				{ID: "o11g-03", Name: "SGA统计", Category: "内存", Command: "SELECT NAME, VALUE/1024/1024 SIZE_MB FROM V$SGA", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 3},
				{ID: "o11g-04", Name: "TOP 10 SQL", Category: "性能", Command: "SELECT SQL_ID, EXECUTIONS, ELAPSED_TIME/1000000 ELAPSED_SEC, CPU_TIME/1000000 CPU_SEC FROM (SELECT * FROM V$SQLAREA ORDER BY ELAPSED_TIME DESC) WHERE ROWNUM<=10", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 4},
				{ID: "o11g-05", Name: "备份状态", Category: "备份", Command: "SELECT * FROM (SELECT INPUT_TYPE, STATUS, START_TIME, END_TIME FROM V$RMAN_BACKUP_JOB_DETAILS ORDER BY START_TIME DESC) WHERE ROWNUM<=5", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 5},
			},
		},
		{
			ID: "tpl-oracle-12c-v1", Name: "Oracle 12c巡检模板", TargetType: models.TargetTypeOracle,
			Brand: "Oracle", Version: "v1.0.0", Description: "Oracle 12c/12cR2数据库健康巡检模板，支持CDB/PDB架构",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "o12c-01", Name: "CDB/PDB状态", Category: "实例", Command: "SELECT CON_ID, NAME, OPEN_MODE FROM V$PDBS", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 20, Order: 1},
				{ID: "o12c-02", Name: "表空间使用率", Category: "存储", Command: "SELECT CON_ID, TABLESPACE_NAME, ROUND(USED_PCT,2) PCT_USED FROM CDB_TABLESPACE_USAGE_METRICS", CommandType: "sql", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "tbs_usage", Operator: "gt", Critical: 95, Warning: 85, Unit: "%"}, Weight: 20, Order: 2},
				{ID: "o12c-03", Name: "AWR性能概览", Category: "性能", Command: "SELECT SNAP_ID, BEGIN_INTERVAL_TIME, END_INTERVAL_TIME FROM DBA_HIST_SNAPSHOT ORDER BY SNAP_ID DESC FETCH FIRST 5 ROWS ONLY", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 3},
			},
		},
		{
			ID: "tpl-network-huawei-v1", Name: "华为网络设备巡检模板", TargetType: models.TargetTypeNetwork,
			Brand: "华为", Version: "v1.0.0", Description: "华为交换机/路由器/防火墙通用巡检模板，支持CE/USG/S系列",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "hw-01", Name: "设备版本信息", Category: "系统", Command: "display version", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 1},
				{ID: "hw-02", Name: "CPU使用率", Category: "CPU", Command: "display cpu-usage", CommandType: "ssh", IsReadOnly: true, Parser: "regex", ParserConfig: `{"pattern":"([0-9]+)%"}`, Threshold: &models.ThresholdConfig{Metric: "cpu_usage", Operator: "gt", Critical: 90, Warning: 70, Unit: "%"}, Suggestion: "检查异常进程或流量，考虑设备扩容", Weight: 20, Order: 2},
				{ID: "hw-03", Name: "内存使用率", Category: "内存", Command: "display memory-usage", CommandType: "ssh", IsReadOnly: true, Parser: "regex", ParserConfig: `{"pattern":"([0-9]+)%"}`, Threshold: &models.ThresholdConfig{Metric: "mem_usage", Operator: "gt", Critical: 85, Warning: 70, Unit: "%"}, Weight: 20, Order: 3},
				{ID: "hw-04", Name: "接口状态", Category: "接口", Command: "display interface brief", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 4},
				{ID: "hw-05", Name: "告警信息", Category: "告警", Command: "display alarm active all", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 5},
				{ID: "hw-06", Name: "日志缓冲", Category: "日志", Command: "display logbuffer reverse", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 6},
				{ID: "hw-07", Name: "路由表摘要", Category: "路由", Command: "display ip routing-table statistics", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 7},
				{ID: "hw-08", Name: "风扇状态", Category: "硬件", Command: "display device fan", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 8},
				{ID: "hw-09", Name: "电源状态", Category: "硬件", Command: "display device power", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 9},
				{ID: "hw-10", Name: "温度信息", Category: "硬件", Command: "display device temperature", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "temperature", Operator: "gt", Critical: 70, Warning: 60, Unit: "°C"}, Weight: 5, Order: 10},
			},
		},
		{
			ID: "tpl-network-h3c-v1", Name: "华三网络设备巡检模板", TargetType: models.TargetTypeNetwork,
			Brand: "华三", Version: "v1.0.0", Description: "华三交换机/路由器通用巡检模板，支持S/MSR系列",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "h3c-01", Name: "设备版本", Category: "系统", Command: "display version", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 1},
				{ID: "h3c-02", Name: "CPU使用率", Category: "CPU", Command: "display cpu-usage", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "cpu_usage", Operator: "gt", Critical: 90, Warning: 70, Unit: "%"}, Weight: 20, Order: 2},
				{ID: "h3c-03", Name: "内存使用率", Category: "内存", Command: "display memory", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "mem_usage", Operator: "gt", Critical: 85, Warning: 70, Unit: "%"}, Weight: 20, Order: 3},
				{ID: "h3c-04", Name: "接口状态", Category: "接口", Command: "display interface brief", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 4},
				{ID: "h3c-05", Name: "告警信息", Category: "告警", Command: "display alarm", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 5},
			},
		},
		{
			ID: "tpl-san-brocade-v1", Name: "Brocade SAN交换机巡检模板", TargetType: models.TargetTypeSANSwitch,
			Brand: "Brocade", Version: "v1.0.0", Description: "Brocade光纤交换机健康巡检模板",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "br-01", Name: "交换机状态", Category: "系统", Command: "switchshow", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 1},
				{ID: "br-02", Name: "端口状态", Category: "端口", Command: "portshow", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 2},
				{ID: "br-03", Name: "SFP信息", Category: "硬件", Command: "sfpshow all", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 3},
				{ID: "br-04", Name: "错误统计", Category: "错误", Command: "porterrshow", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 20, Order: 4},
				{ID: "br-05", Name: "固件版本", Category: "系统", Command: "firmwaredownload --show", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 5},
			},
		},
		{
			ID: "tpl-storage-huawei-v1", Name: "华为存储巡检模板", TargetType: models.TargetTypeStorage,
			Brand: "华为", Version: "v1.0.0", Description: "华为OceanStor系列存储巡检模板",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "st-hw-01", Name: "存储系统状态", Category: "系统", Command: "show system general", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 1},
				{ID: "st-hw-02", Name: "存储池使用率", Category: "存储", Command: "show storage_pool general", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "pool_usage", Operator: "gt", Critical: 90, Warning: 80, Unit: "%"}, Weight: 20, Order: 2},
				{ID: "st-hw-03", Name: "LUN状态", Category: "存储", Command: "show lun general", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 3},
				{ID: "st-hw-04", Name: "硬盘状态", Category: "硬件", Command: "show disk general", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 4},
				{ID: "st-hw-05", Name: "控制器状态", Category: "硬件", Command: "show controller general", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 5},
			},
		},
		{
			ID: "tpl-windows-generic-v1", Name: "Windows通用巡检模板", TargetType: models.TargetTypeWindows,
			Brand: "Microsoft", Version: "v1.0.0", Description: "Windows Server通用巡检模板，支持离线采集模式",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "win-01", Name: "系统信息", Category: "系统", Command: "Get-ComputerInfo | Select-Object CsName, WindowsVersion, OsArchitecture", CommandType: "script", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 1},
				{ID: "win-02", Name: "CPU使用率", Category: "CPU", Command: "Get-Counter '\\Processor(_Total)\\% Processor Time' | Select-Object -ExpandProperty CounterSamples | Select-Object CookedValue", CommandType: "script", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "cpu_usage", Operator: "gt", Critical: 90, Warning: 70, Unit: "%"}, Weight: 20, Order: 2},
				{ID: "win-03", Name: "内存使用率", Category: "内存", Command: "$os = Get-CimInstance Win32_OperatingSystem; [math]::Round(($os.TotalVisibleMemorySize - $os.FreePhysicalMemory)/$os.TotalVisibleMemorySize*100,2)", CommandType: "script", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "mem_usage", Operator: "gt", Critical: 90, Warning: 80, Unit: "%"}, Weight: 20, Order: 3},
				{ID: "win-04", Name: "磁盘使用率", Category: "磁盘", Command: "Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select-Object DeviceID, @{N='Size_GB';E={[math]::Round($_.Size/1GB,2)}}, @{N='Free_GB';E={[math]::Round($_.FreeSpace/1GB,2)}}", CommandType: "script", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "disk_usage", Operator: "gt", Critical: 90, Warning: 80, Unit: "%"}, Weight: 20, Order: 4},
				{ID: "win-05", Name: "事件日志错误", Category: "安全", Command: "Get-EventLog -LogName System -EntryType Error -Newest 20 | Format-Table TimeGenerated, Source, Message -Wrap", CommandType: "script", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 5},
				{ID: "win-06", Name: "服务状态", Category: "服务", Command: "Get-Service | Where-Object {$_.StartType -eq 'Automatic' -and $_.Status -ne 'Running'} | Format-Table Name, DisplayName, Status", CommandType: "script", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 6},
			},
		},
		{
			ID: "tpl-bmc-dell-idrac-v1", Name: "Dell iDRAC巡检模板", TargetType: models.TargetTypeBMC,
			Brand: "Dell", Version: "v1.0.0", Description: "Dell iDRAC BMC巡检模板（Redfish API）",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "idrac-01", Name: "系统信息", Category: "系统", Command: "/redfish/v1/Systems/System.Embedded.1", CommandType: "http", IsReadOnly: true, Parser: "jsonpath", ParserConfig: `{"paths":["$.Model","$.SerialNumber","$.PowerState"]}`, Weight: 5, Order: 1},
				{ID: "idrac-02", Name: "硬盘状态", Category: "存储", Command: "/redfish/v1/Systems/System.Embedded.1/Storage", CommandType: "http", IsReadOnly: true, Parser: "jsonpath", Weight: 15, Order: 2},
				{ID: "idrac-03", Name: "风扇状态", Category: "硬件", Command: "/redfish/v1/Chassis/System.Embedded.1/Thermal", CommandType: "http", IsReadOnly: true, Parser: "jsonpath", Weight: 10, Order: 3},
				{ID: "idrac-04", Name: "电源状态", Category: "硬件", Command: "/redfish/v1/Chassis/System.Embedded.1/Power", CommandType: "http", IsReadOnly: true, Parser: "jsonpath", Weight: 10, Order: 4},
				{ID: "idrac-05", Name: "SEL日志", Category: "日志", Command: "/redfish/v1/Managers/iDRAC.Embedded.1/LogServices/Sel/Entries", CommandType: "http", IsReadOnly: true, Parser: "jsonpath", Weight: 10, Order: 5},
			},
		},
		{
			ID: "tpl-aix-generic-v1", Name: "AIX通用巡检模板", TargetType: models.TargetTypeAIX,
			Brand: "IBM", Version: "v1.0.0", Description: "IBM AIX操作系统巡检模板，适用于Power Systems",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "aix-01", Name: "系统版本", Category: "系统", Command: "oslevel -s", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 5, Order: 1},
				{ID: "aix-02", Name: "CPU使用率", Category: "CPU", Command: "vmstat 1 3 | tail -1 | awk '{print 100-$16}'", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "cpu_usage", Operator: "gt", Critical: 90, Warning: 70, Unit: "%"}, Weight: 20, Order: 2},
				{ID: "aix-03", Name: "内存使用率", Category: "内存", Command: "svmon -G | head -2 | tail -1 | awk '{printf \"%.1f\", $3/$2*100}'", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 20, Order: 3},
				{ID: "aix-04", Name: "文件系统使用率", Category: "磁盘", Command: "df -g | awk 'NR>1{print $7, $4}'", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "fs_usage", Operator: "gt", Critical: 90, Warning: 80, Unit: "%"}, Weight: 15, Order: 4},
				{ID: "aix-05", Name: "VG状态", Category: "存储", Command: "lsvg -o | xargs -I{} lsvg {}", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 5},
				{ID: "aix-06", Name: "HACMP状态", Category: "集群", Command: "clstat 2>/dev/null || echo 'HACMP not configured'", CommandType: "ssh", IsReadOnly: true, Parser: "raw", Weight: 10, Order: 6},
			},
		},
		{
			ID: "tpl-mysql-8-v1", Name: "MySQL 8.0巡检模板", TargetType: models.TargetTypeMySQL,
			Brand: "Oracle", Version: "v1.0.0", Description: "MySQL 8.0数据库巡检模板",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "my8-01", Name: "实例状态", Category: "实例", Command: "SHOW GLOBAL STATUS LIKE 'Threads_connected'; SHOW GLOBAL STATUS LIKE 'Threads_running'", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 1},
				{ID: "my8-02", Name: "InnoDB缓冲池", Category: "内存", Command: "SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool%'", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 2},
				{ID: "my8-03", Name: "慢查询统计", Category: "性能", Command: "SHOW GLOBAL STATUS LIKE 'Slow_queries'; SHOW VARIABLES LIKE 'long_query_time'", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 3},
				{ID: "my8-04", Name: "主从复制状态", Category: "复制", Command: "SHOW SLAVE STATUS\\G", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 20, Order: 4},
				{ID: "my8-05", Name: "连接数", Category: "连接", Command: "SHOW VARIABLES LIKE 'max_connections'; SHOW GLOBAL STATUS LIKE 'Max_used_connections'", CommandType: "sql", IsReadOnly: true, Parser: "raw", Threshold: &models.ThresholdConfig{Metric: "conn_usage", Operator: "gt", Critical: 90, Warning: 75, Unit: "%"}, Weight: 15, Order: 5},
			},
		},
		{
			ID: "tpl-pg-15-v1", Name: "PostgreSQL 15巡检模板", TargetType: models.TargetTypePostgres,
			Brand: "PostgreSQL", Version: "v1.0.0", Description: "PostgreSQL 15数据库巡检模板",
			IsBuiltIn: true, CreatedBy: "system", CreatedAt: now, UpdatedAt: now,
			Items: []models.InspectionItem{
				{ID: "pg-01", Name: "连接数", Category: "连接", Command: "SELECT count(*) FROM pg_stat_activity; SHOW max_connections", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 1},
				{ID: "pg-02", Name: "数据库大小", Category: "存储", Command: "SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database WHERE datistemplate = false", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 2},
				{ID: "pg-03", Name: "复制状态", Category: "复制", Command: "SELECT * FROM pg_stat_replication", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 15, Order: 3},
				{ID: "pg-04", Name: "死锁检查", Category: "锁", Command: "SELECT * FROM pg_locks WHERE NOT granted", CommandType: "sql", IsReadOnly: true, Parser: "raw", Weight: 20, Order: 4},
			},
		},
	}
}

func GetTemplates() []models.InspectionTemplate {
	return templates
}

func GetTemplatesByType(t models.TargetType) []models.InspectionTemplate {
	var result []models.InspectionTemplate
	for _, tpl := range templates {
		if tpl.TargetType == t {
			result = append(result, tpl)
		}
	}
	return result
}

func GetTemplate(id string) *models.InspectionTemplate {
	for i := range templates {
		if templates[i].ID == id {
			return &templates[i]
		}
	}
	return nil
}

func AddTemplate(req models.InspectionTemplate) models.InspectionTemplate {
	req.ID = fmt.Sprintf("tpl-custom-%d", time.Now().UnixNano())
	req.CreatedAt = time.Now()
	req.UpdatedAt = time.Now()
	req.IsBuiltIn = false
	templates = append(templates, req)
	return req
}

func UpdateTemplate(id string, req models.InspectionTemplate) *models.InspectionTemplate {
	for i := range templates {
		if templates[i].ID == id {
			req.ID = id
			req.UpdatedAt = time.Now()
			templates[i] = req
			return &templates[i]
		}
	}
	return nil
}

func DeleteTemplate(id string) {
	for i := range templates {
		if templates[i].ID == id {
			templates = append(templates[:i], templates[i+1:]...)
			return
		}
	}
}

// ============================================================
// 巡检任务管理
// ============================================================

var tasks []models.InspectionTask
var nextTaskNum = 1

func init() {
	now := time.Now()
	tasks = []models.InspectionTask{
		{ID: "task-001", Name: "每日核心网络巡检", TemplateID: "tpl-network-huawei-v1", TargetIDs: []int{1, 13, 14}, ScheduleType: models.ScheduleDaily, Status: models.TaskStatusCompleted, LastRunAt: &[]time.Time{now.Add(-2 * time.Hour)}[0], NextRunAt: &[]time.Time{now.Add(22 * time.Hour)}[0], NotifyEmail: []string{"ops@company.com"}, CreatedBy: "admin", CreatedAt: now.Add(-720 * time.Hour), UpdatedAt: now.Add(-2 * time.Hour)},
		{ID: "task-002", Name: "Oracle生产库巡检", TemplateID: "tpl-oracle-19c-v1", TargetIDs: []int{3}, ScheduleType: models.ScheduleHourly, Status: models.TaskStatusCompleted, LastRunAt: &[]time.Time{now.Add(-1 * time.Hour)}[0], NextRunAt: &[]time.Time{now.Add(0 * time.Minute)}[0], NotifyEmail: []string{"dba@company.com"}, CreatedBy: "admin", CreatedAt: now.Add(-480 * time.Hour), UpdatedAt: now.Add(-1 * time.Hour)},
		{ID: "task-003", Name: "Linux服务器周巡检", TemplateID: "tpl-linux-generic-v1", TargetIDs: []int{5, 6}, ScheduleType: models.ScheduleWeekly, Status: models.TaskStatusCompleted, LastRunAt: &[]time.Time{now.Add(-48 * time.Hour)}[0], NextRunAt: &[]time.Time{now.Add(120 * time.Hour)}[0], CreatedBy: "engineer", CreatedAt: now.Add(-240 * time.Hour), UpdatedAt: now.Add(-48 * time.Hour)},
		{ID: "task-004", Name: "存储设备月巡检", TemplateID: "tpl-storage-huawei-v1", TargetIDs: []int{9}, ScheduleType: models.ScheduleMonthly, Status: models.TaskStatusPending, NextRunAt: &[]time.Time{now.Add(168 * time.Hour)}[0], CreatedBy: "admin", CreatedAt: now.Add(-720 * time.Hour), UpdatedAt: now.Add(-720 * time.Hour)},
		{ID: "task-005", Name: "SAN交换机巡检", TemplateID: "tpl-san-brocade-v1", TargetIDs: []int{8}, ScheduleType: models.ScheduleDaily, Status: models.TaskStatusRunning, LastRunAt: &[]time.Time{now.Add(-5 * time.Minute)}[0], CreatedBy: "engineer", CreatedAt: now.Add(-360 * time.Hour), UpdatedAt: now.Add(-5 * time.Minute)},
		{ID: "task-006", Name: "MySQL数据库巡检", TemplateID: "tpl-mysql-8-v1", TargetIDs: []int{11}, ScheduleType: models.ScheduleDaily, Status: models.TaskStatusCompleted, LastRunAt: &[]time.Time{now.Add(-3 * time.Hour)}[0], NextRunAt: &[]time.Time{now.Add(21 * time.Hour)}[0], CreatedBy: "admin", CreatedAt: now.Add(-180 * time.Hour), UpdatedAt: now.Add(-3 * time.Hour)},
	}
	nextTaskNum = 7
}

func GetTasks() []models.InspectionTask {
	return tasks
}

func GetTask(id string) *models.InspectionTask {
	for i := range tasks {
		if tasks[i].ID == id {
			return &tasks[i]
		}
	}
	return nil
}

func AddTask(req models.InspectionTask) models.InspectionTask {
	req.ID = fmt.Sprintf("task-%03d", nextTaskNum)
	nextTaskNum++
	req.CreatedAt = time.Now()
	req.UpdatedAt = time.Now()
	if req.Status == "" {
		req.Status = models.TaskStatusPending
	}
	tasks = append(tasks, req)
	return req
}

func UpdateTask(id string, req models.InspectionTask) *models.InspectionTask {
	for i := range tasks {
		if tasks[i].ID == id {
			req.ID = id
			req.UpdatedAt = time.Now()
			tasks[i] = req
			return &tasks[i]
		}
	}
	return nil
}

func DeleteTask(id string) {
	for i := range tasks {
		if tasks[i].ID == id {
			tasks = append(tasks[:i], tasks[i+1:]...)
			return
		}
	}
}

func RunTask(id string) *models.InspectionTask {
	for i := range tasks {
		if tasks[i].ID == id {
			now := time.Now()
			tasks[i].Status = models.TaskStatusRunning
			tasks[i].LastRunAt = &now
			// Simulate completion
			go func(idx int) {
				time.Sleep(2 * time.Second)
				tasks[idx].Status = models.TaskStatusCompleted
			}(i)
			return &tasks[i]
		}
	}
	return nil
}

// ============================================================
// 巡检结果管理
// ============================================================

var results []models.InspectionResult
var nextResultID = 1

func init() {
	now := time.Now()
	results = []models.InspectionResult{
		{ID: 1, TaskID: "task-001", TargetID: 1, TargetName: "生产核心交换机-A", ItemID: "hw-01", ItemName: "设备版本信息", Category: "系统", RawValue: "Huawei Versatile Routing Platform Software VRP (R) software, Version 5.170 (CE12800 V200R019C10)", ParsedValue: "CE12800 V200R019C10", Status: models.ResultOK, ExecutedAt: now.Add(-2 * time.Hour), DurationMs: 230},
		{ID: 2, TaskID: "task-001", TargetID: 1, TargetName: "生产核心交换机-A", ItemID: "hw-02", ItemName: "CPU使用率", Category: "CPU", RawValue: "15%", ParsedValue: 15.0, Status: models.ResultOK, Threshold: "警告>70% 严重>90%", ExecutedAt: now.Add(-2 * time.Hour), DurationMs: 180},
		{ID: 3, TaskID: "task-001", TargetID: 1, TargetName: "生产核心交换机-A", ItemID: "hw-03", ItemName: "内存使用率", Category: "内存", RawValue: "62%", ParsedValue: 62.0, Status: models.ResultOK, Threshold: "警告>70% 严重>85%", ExecutedAt: now.Add(-2 * time.Hour), DurationMs: 190},
		{ID: 4, TaskID: "task-002", TargetID: 3, TargetName: "ORACLE-PROD-DB1", ItemID: "oi-01", ItemName: "数据库实例状态", Category: "实例", RawValue: "STATUS=OPEN, DATABASE_STATUS=ACTIVE", ParsedValue: "OPEN/ACTIVE", Status: models.ResultOK, ExecutedAt: now.Add(-1 * time.Hour), DurationMs: 450},
		{ID: 5, TaskID: "task-002", TargetID: 3, TargetName: "ORACLE-PROD-DB1", ItemID: "oi-02", ItemName: "表空间使用率", Category: "存储", RawValue: "USERS: 92.5%, SYSAUX: 78.3%, SYSTEM: 65.1%, UNDOTBS: 45.2%", ParsedValue: "USERS=92.5%", Status: models.ResultWarning, Threshold: "警告>85% 严重>95%", Suggestion: "USERS表空间使用率偏高，建议扩容或清理数据", ExecutedAt: now.Add(-1 * time.Hour), DurationMs: 680},
		{ID: 6, TaskID: "task-002", TargetID: 3, TargetName: "ORACLE-PROD-DB1", ItemID: "oi-05", ItemName: "锁阻塞检测", Category: "锁", RawValue: "SID 156 阻塞 3 个会话，持锁时间 600s", ParsedValue: "1个阻塞源", Status: models.ResultCritical, Threshold: ">0 即告警", Suggestion: "检查SID 156会话是否正常，必要时Kill该会话", ExecutedAt: now.Add(-1 * time.Hour), DurationMs: 520},
		{ID: 7, TaskID: "task-003", TargetID: 5, TargetName: "APP-SERVER-01", ItemID: "li-02", ItemName: "CPU使用率", Category: "CPU", RawValue: "45.2%", ParsedValue: 45.2, Status: models.ResultOK, Threshold: "警告>70% 严重>90%", ExecutedAt: now.Add(-48 * time.Hour), DurationMs: 310},
		{ID: 8, TaskID: "task-003", TargetID: 5, TargetName: "APP-SERVER-01", ItemID: "li-04", ItemName: "磁盘使用率", Category: "磁盘", RawValue: "/ 85%, /data 91%, /log 72%", ParsedValue: "/data=91%", Status: models.ResultWarning, Threshold: "警告>80% 严重>90%", Suggestion: "/data分区使用率91%，建议清理或扩容", ExecutedAt: now.Add(-48 * time.Hour), DurationMs: 290},
		{ID: 9, TaskID: "task-003", TargetID: 6, TargetName: "APP-SERVER-02", ItemID: "li-03", ItemName: "内存使用率", Category: "内存", RawValue: "87.3%", ParsedValue: 87.3, Status: models.ResultWarning, Threshold: "警告>80% 严重>90%", Suggestion: "内存使用率偏高，检查内存泄漏", ExecutedAt: now.Add(-48 * time.Hour), DurationMs: 280},
		{ID: 10, TaskID: "task-006", TargetID: 11, TargetName: "MySQL-PROD-01", ItemID: "my8-04", ItemName: "主从复制状态", Category: "复制", RawValue: "Slave_IO_Running=Yes, Slave_SQL_Running=Yes, Seconds_Behind_Master=0", ParsedValue: "正常,延迟0s", Status: models.ResultOK, ExecutedAt: now.Add(-3 * time.Hour), DurationMs: 420},
	}
	nextResultID = 11
}

func GetResults(taskID string, targetID int) []models.InspectionResult {
	var filtered []models.InspectionResult
	for _, r := range results {
		if taskID != "" && r.TaskID != taskID {
			continue
		}
		if targetID > 0 && r.TargetID != targetID {
			continue
		}
		filtered = append(filtered, r)
	}
	return filtered
}

func GenerateMockResults(taskID string, targetID int, templateID string) []models.InspectionResult {
	tpl := GetTemplate(templateID)
	if tpl == nil {
		return nil
	}

	var t *models.InspectionTarget
	for _, tgt := range targets {
		if tgt.ID == targetID {
			t = &tgt
			break
		}
	}
	if t == nil {
		return nil
	}

	var newResults []models.InspectionResult
	now := time.Now()
	for _, item := range tpl.Items {
		status := models.ResultOK
		rawValue := "正常"
		parsedValue := "OK"
		var thresholdDesc string
		var suggestion string

		// Simulate some warnings and criticals
		r := rand.Float64()
		if r < 0.1 {
			status = models.ResultCritical
			rawValue = fmt.Sprintf("%s异常 - 值超出阈值范围", item.Name)
			parsedValue = "CRITICAL"
			if item.Threshold != nil {
				thresholdDesc = fmt.Sprintf("严重>%.0f%s 警告>%.0f%s", item.Threshold.Critical, item.Threshold.Unit, item.Threshold.Warning, item.Threshold.Unit)
			}
			suggestion = item.Suggestion
		} else if r < 0.25 {
			status = models.ResultWarning
			rawValue = fmt.Sprintf("%s偏高 - 接近阈值", item.Name)
			parsedValue = "WARNING"
			if item.Threshold != nil {
				thresholdDesc = fmt.Sprintf("警告>%.0f%s", item.Threshold.Warning, item.Threshold.Unit)
			}
			suggestion = item.Suggestion
		}

		nextResultID++
		newResults = append(newResults, models.InspectionResult{
			ID: nextResultID, TaskID: taskID, TargetID: targetID, TargetName: t.Name,
			ItemID: item.ID, ItemName: item.Name, Category: item.Category,
			RawValue: rawValue, ParsedValue: parsedValue, Status: status,
			Threshold: thresholdDesc, Suggestion: suggestion,
			ExecutedAt: now, DurationMs: rand.Intn(500) + 50,
		})
	}
	results = append(results, newResults...)
	return newResults
}

// ============================================================
// 巡检报告管理
// ============================================================

var reports []models.InspectionReport
var nextReportNum = 1

func init() {
	now := time.Now()
	reports = []models.InspectionReport{
		{
			ID: "rpt-001", TaskID: "task-001", TaskName: "每日核心网络巡检",
			TargetIDs: []int{1, 13, 14}, Format: models.ReportHTML,
			HealthScore: 92, TotalItems: 30, OKCount: 27, WarningCount: 2, CriticalCount: 1,
			Summary: "核心网络设备整体健康，防火墙CPU使用率偏高需关注",
			Issues: []models.IssueItem{
				{TargetName: "FW-CORE-01", ItemName: "CPU使用率", Category: "CPU", Status: models.ResultWarning, Value: "72%", Threshold: "警告>70%", Suggestion: "检查防火墙会话数和策略"},
			},
			GeneratedAt: now.Add(-2 * time.Hour), DownloadURL: "/api/v1/reports/rpt-001/download?format=html",
		},
		{
			ID: "rpt-002", TaskID: "task-002", TaskName: "Oracle生产库巡检",
			TargetIDs: []int{3}, Format: models.ReportHTML,
			HealthScore: 75, TotalItems: 8, OKCount: 5, WarningCount: 1, CriticalCount: 2,
			Summary: "ORACLE-PROD-DB1 存在锁阻塞和表空间使用率告警，需紧急处理",
			Issues: []models.IssueItem{
				{TargetName: "ORACLE-PROD-DB1", ItemName: "锁阻塞检测", Category: "锁", Status: models.ResultCritical, Value: "SID 156阻塞3个会话", Threshold: ">0即告警", Suggestion: "检查SID 156会话是否正常，必要时Kill该会话"},
				{TargetName: "ORACLE-PROD-DB1", ItemName: "表空间使用率", Category: "存储", Status: models.ResultWarning, Value: "USERS 92.5%", Threshold: "警告>85%", Suggestion: "USERS表空间使用率偏高，建议扩容"},
			},
			GeneratedAt: now.Add(-1 * time.Hour), DownloadURL: "/api/v1/reports/rpt-002/download?format=html",
		},
		{
			ID: "rpt-003", TaskID: "task-003", TaskName: "Linux服务器周巡检",
			TargetIDs: []int{5, 6}, Format: models.ReportHTML,
			HealthScore: 85, TotalItems: 24, OKCount: 20, WarningCount: 3, CriticalCount: 1,
			Summary: "服务器整体健康，APP-SERVER-01磁盘使用率需关注",
			GeneratedAt: now.Add(-48 * time.Hour), DownloadURL: "/api/v1/reports/rpt-003/download?format=html",
		},
		{
			ID: "rpt-004", TaskID: "task-006", TaskName: "MySQL数据库巡检",
			TargetIDs: []int{11}, Format: models.ReportHTML,
			HealthScore: 87, TotalItems: 5, OKCount: 4, WarningCount: 1, CriticalCount: 0,
			Summary: "MySQL主从复制正常，慢查询数略有上升",
			GeneratedAt: now.Add(-3 * time.Hour), DownloadURL: "/api/v1/reports/rpt-004/download?format=html",
		},
	}
	nextReportNum = 5
}

func GetReports() []models.InspectionReport {
	return reports
}

func GetReport(id string) *models.InspectionReport {
	for i := range reports {
		if reports[i].ID == id {
			return &reports[i]
		}
	}
	return nil
}

func GenerateReport(taskID string, format models.ReportFormat) *models.InspectionReport {
	task := GetTask(taskID)
	if task == nil {
		return nil
	}

	taskResults := GetResults(taskID, 0)
	tpl := GetTemplate(task.TemplateID)

	totalItems := len(taskResults)
	okCount := 0
	warningCount := 0
	criticalCount := 0
	var issues []models.IssueItem

	for _, r := range taskResults {
		switch r.Status {
		case models.ResultOK:
			okCount++
		case models.ResultWarning:
			warningCount++
			issues = append(issues, models.IssueItem{
				TargetName: r.TargetName, ItemName: r.ItemName, Category: r.Category,
				Status: r.Status, Value: r.RawValue, Threshold: r.Threshold, Suggestion: r.Suggestion,
			})
		case models.ResultCritical:
			criticalCount++
			issues = append(issues, models.IssueItem{
				TargetName: r.TargetName, ItemName: r.ItemName, Category: r.Category,
				Status: r.Status, Value: r.RawValue, Threshold: r.Threshold, Suggestion: r.Suggestion,
			})
		}
	}

	healthScore := 100
	if totalItems > 0 {
		healthScore = 100 - (criticalCount*15 + warningCount*5)
		if healthScore < 0 {
			healthScore = 0
		}
	}

	summary := "巡检完成"
	if criticalCount > 0 {
		summary = fmt.Sprintf("发现 %d 个严重问题，%d 个警告", criticalCount, warningCount)
	} else if warningCount > 0 {
		summary = fmt.Sprintf("发现 %d 个警告项，建议关注", warningCount)
	}

	templateName := ""
	if tpl != nil {
		templateName = tpl.Name
	}

	now := time.Now()
	report := models.InspectionReport{
		ID: fmt.Sprintf("rpt-%03d", nextReportNum), TaskID: taskID, TaskName: task.Name + " - " + templateName,
		TargetIDs: task.TargetIDs, Format: format,
		HealthScore: healthScore, TotalItems: totalItems,
		OKCount: okCount, WarningCount: warningCount, CriticalCount: criticalCount,
		Summary: summary, Issues: issues, Results: taskResults,
		GeneratedAt: now, DownloadURL: fmt.Sprintf("/api/v1/reports/rpt-%03d/download?format=%s", nextReportNum, format),
	}
	nextReportNum++
	reports = append(reports, report)
	return &report
}

// ============================================================
// 仪表盘统计
// ============================================================

func GetDashboardStats() models.DashboardStats {
	activeCount := 0
	typeCounts := make(map[models.TargetType]int)
	for _, t := range targets {
		if t.Status == "active" {
			activeCount++
		}
		typeCounts[t.Type]++
	}

	var targetsByType []models.TypeCount
	for t, c := range typeCounts {
		targetsByType = append(targetsByType, models.TypeCount{Type: t, Count: c})
	}

	runningCount := 0
	for _, t := range tasks {
		if t.Status == models.TaskStatusRunning {
			runningCount++
		}
	}

	now := time.Now()
	recentTasks := []models.RecentTask{
		{ID: "task-005", Name: "SAN交换机巡检", Status: models.TaskStatusRunning, StartedAt: now.Add(-5 * time.Minute), Progress: 60},
		{ID: "task-002", Name: "Oracle生产库巡检", Status: models.TaskStatusCompleted, StartedAt: now.Add(-1 * time.Hour), Progress: 100},
		{ID: "task-001", Name: "每日核心网络巡检", Status: models.TaskStatusCompleted, StartedAt: now.Add(-2 * time.Hour), Progress: 100},
		{ID: "task-006", Name: "MySQL数据库巡检", Status: models.TaskStatusCompleted, StartedAt: now.Add(-3 * time.Hour), Progress: 100},
	}

	criticalIssues := 0
	warningIssues := 0
	for _, r := range results {
		if r.Status == models.ResultCritical {
			criticalIssues++
		} else if r.Status == models.ResultWarning {
			warningIssues++
		}
	}

	alerts := []models.AlertItem{
		{ID: 1, Severity: "critical", Message: "ORACLE-PROD-DB1 检测到锁阻塞：SID 156阻塞3个会话", Target: "ORACLE-PROD-DB1", Time: now.Add(-30 * time.Minute)},
		{ID: 2, Severity: "warning", Message: "APP-SERVER-01 /data分区使用率91%，接近阈值", Target: "APP-SERVER-01", Time: now.Add(-1 * time.Hour)},
		{ID: 3, Severity: "warning", Message: "APP-SERVER-02 内存使用率87.3%，超过警告阈值", Target: "APP-SERVER-02", Time: now.Add(-48 * time.Hour)},
		{ID: 4, Severity: "info", Message: "SAN-SWITCH-A 巡检任务正在执行中", Target: "SAN-SWITCH-A", Time: now.Add(-5 * time.Minute)},
		{ID: 5, Severity: "info", Message: "MySQL-PROD-01 主从复制状态正常", Target: "MySQL-PROD-01", Time: now.Add(-3 * time.Hour)},
	}

	healthTrend := []models.HealthTrendItem{
		{Date: now.Add(-6 * 24 * time.Hour).Format("01-02"), HealthScore: 88, Critical: 1, Warning: 3},
		{Date: now.Add(-5 * 24 * time.Hour).Format("01-02"), HealthScore: 91, Critical: 0, Warning: 2},
		{Date: now.Add(-4 * 24 * time.Hour).Format("01-02"), HealthScore: 85, Critical: 2, Warning: 4},
		{Date: now.Add(-3 * 24 * time.Hour).Format("01-02"), HealthScore: 90, Critical: 1, Warning: 2},
		{Date: now.Add(-2 * 24 * time.Hour).Format("01-02"), HealthScore: 87, Critical: 1, Warning: 3},
		{Date: now.Add(-1 * 24 * time.Hour).Format("01-02"), HealthScore: 89, Critical: 1, Warning: 2},
		{Date: now.Format("01-02"), HealthScore: 86, Critical: 2, Warning: 3},
	}

	return models.DashboardStats{
		TotalTargets: len(targets), ActiveTargets: activeCount,
		TotalTemplates: len(templates), TotalTasks: len(tasks),
		RunningTasks: runningCount, TodayReports: len(reports),
		CriticalIssues: criticalIssues, WarningIssues: warningIssues,
		TargetsByType: targetsByType, RecentTasks: recentTasks,
		RecentAlerts: alerts, HealthTrend: healthTrend,
	}
}

// ============================================================
// 巡检知识库
// ============================================================

var knowledgeEntries []models.KnowledgeEntry

func init() {
	knowledgeEntries = []models.KnowledgeEntry{
		{ID: "kb-001", Title: "Oracle锁阻塞排查指南", Category: "数据库", TargetType: "oracle", Symptom: "会话等待enq: TX - row lock contention，业务响应缓慢", Cause: "一个会话持有行锁未释放，阻塞其他会话的DML操作", Solution: "1. 查询V$SESSION定位阻塞源会话\n2. 与业务确认是否可以Kill\n3. ALTER SYSTEM KILL SESSION 'sid,serial#' IMMEDIATE\n4. 优化应用逻辑，避免长事务", Reference: "https://docs.oracle.com/en/database/oracle/oracle-database/19/cncpt/locks.html", Severity: "critical", Tags: []string{"Oracle", "锁", "性能"}},
		{ID: "kb-002", Title: "Linux磁盘使用率告警处理", Category: "操作系统", TargetType: "linux", Symptom: "磁盘使用率超过80%告警阈值", Cause: "日志文件过大、临时文件未清理、数据增长过快", Solution: "1. du -sh /* | sort -rh 定位大目录\n2. 清理旧日志：find /var/log -mtime +30 -delete\n3. 清理临时文件：rm -rf /tmp/old_*\n4. 归档历史数据\n5. 必要时扩展磁盘容量", Reference: "", Severity: "warning", Tags: []string{"Linux", "磁盘", "容量"}},
		{ID: "kb-003", Title: "网络设备CPU使用率过高", Category: "网络设备", TargetType: "network", Symptom: "交换机/路由器CPU使用率持续超过70%", Cause: "路由表过大、ACL规则过多、广播风暴、硬件转发异常", Solution: "1. 检查CPU占用最高的进程\n2. 检查路由表规模\n3. 优化ACL规则\n4. 检查是否有环路\n5. 确认硬件转发是否正常", Reference: "", Severity: "warning", Tags: []string{"网络", "CPU", "华为"}},
		{ID: "kb-004", Title: "Oracle表空间不足处理", Category: "数据库", TargetType: "oracle", Symptom: "表空间使用率超过85%，DML操作可能失败", Cause: "数据增长过快、未设置自动扩展、碎片率高", Solution: "1. ALTER TABLESPACE xxx ADD DATAFILE\n2. 开启AUTOEXTEND\n3. 清理历史分区数据\n4. 重建高碎片率索引\n5. 归档旧数据到历史表", Reference: "", Severity: "warning", Tags: []string{"Oracle", "表空间", "存储"}},
		{ID: "kb-005", Title: "SAN交换机端口错误处理", Category: "存储", TargetType: "san_switch", Symptom: "porterrshow显示enc out/crc err等错误计数增长", Cause: "光模块故障、光纤线路衰减、SFP兼容性问题", Solution: "1. 检查SFP模块状态和型号兼容性\n2. 清洁光纤连接器\n3. 测量光功率是否在正常范围\n4. 更换故障SFP或光纤线\n5. 检查端口速率和填充字配置", Reference: "", Severity: "critical", Tags: []string{"SAN", "Brocade", "端口"}},
		{ID: "kb-006", Title: "MySQL主从延迟处理", Category: "数据库", TargetType: "mysql", Symptom: "Seconds_Behind_Master持续增长", Cause: "大事务、从库性能不足、网络延迟、单线程复制瓶颈", Solution: "1. 检查是否有大事务在主库执行\n2. 确认从库IO/CPU是否正常\n3. 开启多线程复制(slave_parallel_workers)\n4. 检查网络延迟\n5. 考虑使用GTID和半同步复制", Reference: "", Severity: "warning", Tags: []string{"MySQL", "复制", "延迟"}},
		{ID: "kb-007", Title: "AIX文件系统扩容", Category: "操作系统", TargetType: "aix", Symptom: "文件系统使用率超过80%", Cause: "数据增长、日志积累、应用输出文件过大", Solution: "1. chfs -a size=+10G /filesystem\n2. 确认VG中有足够空闲空间\n3. 如VG不足，先添加PV再扩展\n4. 清理无用文件", Reference: "", Severity: "warning", Tags: []string{"AIX", "文件系统", "扩容"}},
		{ID: "kb-008", Title: "BMC iDRAC无法访问处理", Category: "硬件管理", TargetType: "bmc", Symptom: "iDRAC Web界面无法访问或Redfish API超时", Cause: "iDRAC服务挂起、网络配置变更、固件Bug", Solution: "1. 尝试SSH登录iDRAC\n2. racadm racreset soft 重启iDRAC\n3. 检查iDRAC网络配置\n4. 升级iDRAC固件到最新版本", Reference: "", Severity: "warning", Tags: []string{"iDRAC", "BMC", "Dell"}},
	}
}

func GetKnowledgeEntries() []models.KnowledgeEntry {
	return knowledgeEntries
}

func GetKnowledgeEntry(id string) *models.KnowledgeEntry {
	for i := range knowledgeEntries {
		if knowledgeEntries[i].ID == id {
			return &knowledgeEntries[i]
		}
	}
	return nil
}

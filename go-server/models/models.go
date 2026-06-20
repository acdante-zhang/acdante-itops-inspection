package models

import "time"

// ============================================================
// 巡检对象 (InspectionTarget)
// ============================================================

type TargetType string

const (
	TargetTypeLinux     TargetType = "linux"
	TargetTypeWindows   TargetType = "windows"
	TargetTypeAIX       TargetType = "aix"
	TargetTypeSANSwitch TargetType = "san_switch"
	TargetTypeNetwork   TargetType = "network"
	TargetTypeBMC       TargetType = "bmc"
	TargetTypeStorage   TargetType = "storage"
	TargetTypeOracle    TargetType = "oracle"
	TargetTypeMySQL     TargetType = "mysql"
	TargetTypePostgres  TargetType = "postgres"
	TargetTypeMSSQL     TargetType = "mssql"
)

type ConnectionProtocol string

const (
	ProtocolSSH    ConnectionProtocol = "ssh"
	ProtocolSNMP   ConnectionProtocol = "snmp"
	ProtocolJDBC   ConnectionProtocol = "jdbc"
	ProtocolODBC   ConnectionProtocol = "odbc"
	ProtocolTelnet ConnectionProtocol = "telnet"
	ProtocolHTTP   ConnectionProtocol = "http"
	ProtocolIPMI   ConnectionProtocol = "ipmi"
	ProtocolRedfish ConnectionProtocol = "redfish"
)

// InspectionTarget 巡检对象
type InspectionTarget struct {
	ID               int                `json:"id"`
	Name             string             `json:"name" binding:"required"`
	Type             TargetType         `json:"type" binding:"required"`
	Brand            string             `json:"brand"`                // 品牌：华为/华三/Cisco/Brocade/EMC 等
	Model            string             `json:"model"`                // 型号
	Version          string             `json:"version"`              // 版本/固件版本
	Location         string             `json:"location"`             // 位置/机房
	ConnectionParams ConnectionParams   `json:"connection_params"`
	OfflineMode      bool               `json:"offline_mode"`         // 是否仅接受上传数据
	Status           string             `json:"status"`               // active/inactive/error
	HealthScore      int                `json:"health_score"`         // 0-100
	LastInspectionAt *time.Time         `json:"last_inspection_at"`
	CreatedAt        time.Time          `json:"created_at"`
	UpdatedAt        time.Time          `json:"updated_at"`
	Tags             []string           `json:"tags"`
}

// ConnectionParams 连接参数
type ConnectionParams struct {
	Protocol   ConnectionProtocol `json:"protocol"`
	Host       string             `json:"host"`
	Port       int                `json:"port"`
	Username   string             `json:"username"`
	PasswordEnc string            `json:"password_enc"` // AES加密存储
	AuthToken  string             `json:"auth_token"`
	SSHKey     string             `json:"ssh_key"`
	SNMPCommunity string          `json:"snmp_community"`
	SNMPVersion  string           `json:"snmp_version"` // v2c/v3
	DatabaseName string           `json:"database_name"`
	Timeout    int                `json:"timeout"` // 秒
}

// ============================================================
// 巡检模板 (InspectionTemplate)
// ============================================================

type InspectionTemplate struct {
	ID          string          `json:"id"`
	Name        string          `json:"name" binding:"required"`
	TargetType  TargetType      `json:"target_type" binding:"required"`
	Brand       string          `json:"brand"`          // 品牌标记
	Version     string          `json:"version"`        // 版本标记（如 v1.0, v2.1）
	Description string          `json:"description"`
	Items       []InspectionItem `json:"items"`
	IsBuiltIn   bool            `json:"is_builtin"`     // 是否内置模板
	CreatedBy   string          `json:"created_by"`
	CreatedAt   time.Time       `json:"created_at"`
	UpdatedAt   time.Time       `json:"updated_at"`
}

// InspectionItem 巡检项
type InspectionItem struct {
	ID           string            `json:"id"`
	Name         string            `json:"name"`           // 巡检项名称
	Category     string            `json:"category"`       // 分类：CPU/内存/磁盘/网络/安全/配置 等
	Command      string            `json:"command"`        // 执行命令/SQL/SNMP OID
	CommandType  string            `json:"command_type"`   // ssh/sql/snmp/http/script
	IsReadOnly   bool              `json:"is_read_only"`   // 是否只读命令
	WarningText  string            `json:"warning_text"`   // 非只读命令的警告提示
	Parser       string            `json:"parser"`         // 解析规则：regex/jsonpath/xpath/raw
	ParserConfig string            `json:"parser_config"`  // 解析配置
	Threshold    *ThresholdConfig  `json:"threshold"`      // 阈值配置
	Expected     string            `json:"expected"`       // 预期输出描述
	Suggestion   string            `json:"suggestion"`     // 建议修复步骤
	Weight       int               `json:"weight"`         // 权重（用于健康度评分）
	Order        int               `json:"order"`          // 排序
}

// ThresholdConfig 阈值配置
type ThresholdConfig struct {
	Metric    string  `json:"metric"`     // 指标名
	Operator  string  `json:"operator"`   // gt/gte/lt/lte/eq/neq/contains
	Critical  float64 `json:"critical"`   // 严重阈值
	Warning   float64 `json:"warning"`    // 警告阈值
	Unit      string  `json:"unit"`       // 单位
}

// ============================================================
// 巡检任务 (InspectionTask)
// ============================================================

type TaskStatus string

const (
	TaskStatusPending   TaskStatus = "pending"
	TaskStatusRunning   TaskStatus = "running"
	TaskStatusCompleted TaskStatus = "completed"
	TaskStatusFailed    TaskStatus = "failed"
)

type ScheduleType string

const (
	ScheduleOnce    ScheduleType = "once"
	ScheduleMinutely ScheduleType = "minutely"
	ScheduleHourly  ScheduleType = "hourly"
	ScheduleDaily   ScheduleType = "daily"
	ScheduleWeekly  ScheduleType = "weekly"
	ScheduleMonthly ScheduleType = "monthly"
)

// InspectionTask 巡检任务
type InspectionTask struct {
	ID            string        `json:"id"`
	Name          string        `json:"name" binding:"required"`
	TemplateID    string        `json:"template_id" binding:"required"`
	TargetIDs     []int         `json:"target_ids" binding:"required"`
	ScheduleType  ScheduleType  `json:"schedule_type"`
	CronExpr      string        `json:"cron_expr"`        // 自定义cron表达式
	Status        TaskStatus    `json:"status"`
	LastRunAt     *time.Time    `json:"last_run_at"`
	NextRunAt     *time.Time    `json:"next_run_at"`
	NotifyEmail   []string      `json:"notify_email"`
	NotifyWebhook string        `json:"notify_webhook"`
	CreatedBy     string        `json:"created_by"`
	CreatedAt     time.Time     `json:"created_at"`
	UpdatedAt     time.Time     `json:"updated_at"`
}

// ============================================================
// 巡检结果 (InspectionResult)
// ============================================================

type ResultStatus string

const (
	ResultOK       ResultStatus = "ok"
	ResultWarning  ResultStatus = "warning"
	ResultCritical ResultStatus = "critical"
	ResultError    ResultStatus = "error"
	ResultSkipped  ResultStatus = "skipped"
)

// InspectionResult 巡检结果
type InspectionResult struct {
	ID          int          `json:"id"`
	TaskID      string       `json:"task_id"`
	TargetID    int          `json:"target_id"`
	TargetName  string       `json:"target_name"`
	ItemID      string       `json:"item_id"`
	ItemName    string       `json:"item_name"`
	Category    string       `json:"category"`
	RawValue    string       `json:"raw_value"`
	ParsedValue interface{}  `json:"parsed_value"`
	Status      ResultStatus `json:"status"`
	Threshold   string       `json:"threshold_desc"`  // 阈值描述
	Suggestion  string       `json:"suggestion"`
	ExecutedAt  time.Time    `json:"executed_at"`
	DurationMs  int          `json:"duration_ms"`
}

// ============================================================
// 巡检报告 (InspectionReport)
// ============================================================

type ReportFormat string

const (
	ReportHTML ReportFormat = "html"
	ReportDOCX ReportFormat = "docx"
	ReportPDF  ReportFormat = "pdf"
)

// InspectionReport 巡检报告
type InspectionReport struct {
	ID            string        `json:"id"`
	TaskID        string        `json:"task_id"`
	TaskName      string        `json:"task_name"`
	TargetIDs     []int         `json:"target_ids"`
	Format        ReportFormat  `json:"format"`
	HealthScore   int           `json:"health_score"`     // 总体健康度
	TotalItems    int           `json:"total_items"`
	OKCount       int           `json:"ok_count"`
	WarningCount  int           `json:"warning_count"`
	CriticalCount int           `json:"critical_count"`
	Summary       string        `json:"summary"`
	Issues        []IssueItem   `json:"issues"`
	Results       []InspectionResult `json:"results"`
	GeneratedAt   time.Time     `json:"generated_at"`
	DownloadURL   string        `json:"download_url"`
}

// IssueItem 问题项
type IssueItem struct {
	TargetName string       `json:"target_name"`
	ItemName   string       `json:"item_name"`
	Category   string       `json:"category"`
	Status     ResultStatus `json:"status"`
	Value      string       `json:"value"`
	Threshold  string       `json:"threshold"`
	Suggestion string       `json:"suggestion"`
}

// ============================================================
// 仪表盘统计
// ============================================================

// DashboardStats 仪表盘统计数据
type DashboardStats struct {
	TotalTargets     int              `json:"total_targets"`
	ActiveTargets    int              `json:"active_targets"`
	TotalTemplates   int              `json:"total_templates"`
	TotalTasks       int              `json:"total_tasks"`
	RunningTasks     int              `json:"running_tasks"`
	TodayReports     int              `json:"today_reports"`
	CriticalIssues   int              `json:"critical_issues"`
	WarningIssues    int              `json:"warning_issues"`
	TargetsByType    []TypeCount      `json:"targets_by_type"`
	RecentTasks      []RecentTask     `json:"recent_tasks"`
	RecentAlerts     []AlertItem      `json:"recent_alerts"`
	HealthTrend      []HealthTrendItem `json:"health_trend"`
}

type TypeCount struct {
	Type  TargetType `json:"type"`
	Count int        `json:"count"`
}

type RecentTask struct {
	ID        string      `json:"id"`
	Name      string      `json:"name"`
	Status    TaskStatus  `json:"status"`
	StartedAt time.Time   `json:"started_at"`
	Progress  int         `json:"progress"` // 0-100
}

type AlertItem struct {
	ID       int          `json:"id"`
	Severity string       `json:"severity"` // critical/warning/info
	Message  string       `json:"message"`
	Target   string       `json:"target"`
	Time     time.Time    `json:"time"`
}

type HealthTrendItem struct {
	Date        string `json:"date"`
	HealthScore int    `json:"health_score"`
	Critical    int    `json:"critical"`
	Warning     int    `json:"warning"`
}

// ============================================================
// 连接测试结果
// ============================================================

type ConnectionTestResult struct {
	Success       bool   `json:"success"`
	Message       string `json:"message"`
	Version       string `json:"version,omitempty"`
	ConnectTimeMs int    `json:"connect_time_ms,omitempty"`
	Details       string `json:"details,omitempty"`
}

// ============================================================
// 巡检知识库
// ============================================================

type KnowledgeEntry struct {
	ID          string   `json:"id"`
	Title       string   `json:"title"`
	Category    string   `json:"category"`
	TargetType  string   `json:"target_type"`
	Symptom     string   `json:"symptom"`
	Cause       string   `json:"cause"`
	Solution    string   `json:"solution"`
	Reference   string   `json:"reference"`
	Severity    string   `json:"severity"`
	Tags        []string `json:"tags"`
}

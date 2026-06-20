/**
 * Acdante ITOps Inspection Platform
 * 统一 API 客户端
 */

const API_BASE = '/api/v1';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.error || error.detail || `API Error: ${res.status}`);
  }
  return res.json();
}

// ============================================================
// 类型定义
// ============================================================

export type TargetType = 'linux' | 'windows' | 'aix' | 'san_switch' | 'network' | 'bmc' | 'storage' | 'oracle' | 'mysql' | 'postgres' | 'mssql' | 'dm8' | 'tidb' | 'kingbase' | 'gbase' | 'ivorysql' | 'yashandb';
export type ConnectionProtocol = 'ssh' | 'snmp' | 'jdbc' | 'odbc' | 'telnet' | 'http' | 'ipmi' | 'redfish' | 'dbcheck';
export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed';
export type ScheduleType = 'once' | 'minutely' | 'hourly' | 'daily' | 'weekly' | 'monthly';
export type ResultStatus = 'ok' | 'warning' | 'critical' | 'error' | 'skipped';
export type ReportFormat = 'html' | 'docx' | 'pdf';

export interface ConnectionParams {
  protocol: ConnectionProtocol;
  host: string;
  port: number;
  username: string;
  password_enc?: string;
  auth_token?: string;
  ssh_key?: string;
  snmp_community?: string;
  snmp_version?: string;
  database_name?: string;
  timeout: number;
}

export interface InspectionTarget {
  id: number;
  name: string;
  type: TargetType;
  brand: string;
  model: string;
  version: string;
  location: string;
  connection_params: ConnectionParams;
  offline_mode: boolean;
  status: string;
  health_score: number;
  last_inspection_at: string | null;
  created_at: string;
  updated_at: string;
  tags: string[];
}

export interface ThresholdConfig {
  metric: string;
  operator: string;
  critical: number;
  warning: number;
  unit: string;
}

export interface InspectionItem {
  id: string;
  name: string;
  category: string;
  command: string;
  command_type: string;
  is_read_only: boolean;
  warning_text?: string;
  parser: string;
  parser_config?: string;
  threshold: ThresholdConfig | null;
  expected?: string;
  suggestion?: string;
  weight: number;
  order: number;
}

export interface InspectionTemplate {
  id: string;
  name: string;
  target_type: TargetType;
  brand: string;
  version: string;
  description: string;
  items: InspectionItem[];
  is_builtin: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface InspectionTask {
  id: string;
  name: string;
  template_id: string;
  target_ids: number[];
  schedule_type: ScheduleType;
  cron_expr?: string;
  status: TaskStatus;
  last_run_at: string | null;
  next_run_at: string | null;
  notify_email: string[];
  notify_webhook?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface InspectionResult {
  id: number;
  task_id: string;
  target_id: number;
  target_name: string;
  item_id: string;
  item_name: string;
  category: string;
  raw_value: string;
  parsed_value: unknown;
  status: ResultStatus;
  threshold: string;
  suggestion: string;
  executed_at: string;
  duration_ms: number;
}

export interface IssueItem {
  target_name: string;
  item_name: string;
  category: string;
  status: ResultStatus;
  value: string;
  threshold: string;
  suggestion: string;
}

export interface InspectionReport {
  id: string;
  task_id: string;
  task_name: string;
  target_ids: number[];
  format: ReportFormat;
  health_score: number;
  total_items: number;
  ok_count: number;
  warning_count: number;
  critical_count: number;
  summary: string;
  issues?: IssueItem[];
  results?: InspectionResult[];
  generated_at: string;
  download_url: string;
}

export interface DashboardStats {
  total_targets: number;
  active_targets: number;
  total_templates: number;
  total_tasks: number;
  running_tasks: number;
  today_reports: number;
  critical_issues: number;
  warning_issues: number;
  targets_by_type: { type: TargetType; count: number }[];
  recent_tasks: { id: string; name: string; status: TaskStatus; started_at: string; progress: number }[];
  recent_alerts: { id: number; severity: string; message: string; target: string; time: string }[];
  health_trend: { date: string; health_score: number; critical: number; warning: number }[];
}

export interface ConnectionTestResult {
  success: boolean;
  message: string;
  version?: string;
  connect_time_ms?: number;
}

export interface KnowledgeEntry {
  id: string;
  title: string;
  category: string;
  target_type: string;
  symptom: string;
  cause: string;
  solution: string;
  reference: string;
  severity: string;
  tags: string[];
}

// ============================================================
// API 函数
// ============================================================

export const api = {
  // Health
  health: () => fetchAPI<{ status: string; service: string }>(`/health`),

  // Dashboard
  dashboard: () => fetchAPI<DashboardStats>(`/dashboard/stats`),

  // Targets
  getTargets: (type?: string) => fetchAPI<{ targets: InspectionTarget[] }>(`/targets${type ? `?type=${type}` : ''}`),
  getTarget: (id: number) => fetchAPI<InspectionTarget>(`/targets/${id}`),
  createTarget: (data: Partial<InspectionTarget>) => fetchAPI<InspectionTarget>(`/targets`, { method: 'POST', body: JSON.stringify(data) }),
  updateTarget: (id: number, data: Partial<InspectionTarget>) => fetchAPI<InspectionTarget>(`/targets/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTarget: (id: number) => fetchAPI<{ message: string }>(`/targets/${id}`, { method: 'DELETE' }),
  testTarget: (id: number) => fetchAPI<ConnectionTestResult>(`/targets/${id}/test`, { method: 'POST' }),

  // Templates
  getTemplates: (type?: string) => fetchAPI<{ templates: InspectionTemplate[] }>(`/templates${type ? `?type=${type}` : ''}`),
  getTemplate: (id: string) => fetchAPI<InspectionTemplate>(`/templates/${id}`),
  createTemplate: (data: Partial<InspectionTemplate>) => fetchAPI<InspectionTemplate>(`/templates`, { method: 'POST', body: JSON.stringify(data) }),
  updateTemplate: (id: string, data: Partial<InspectionTemplate>) => fetchAPI<InspectionTemplate>(`/templates/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteTemplate: (id: string) => fetchAPI<{ message: string }>(`/templates/${id}`, { method: 'DELETE' }),

  // Tasks
  getTasks: () => fetchAPI<{ tasks: InspectionTask[] }>(`/tasks`),
  getTask: (id: string) => fetchAPI<InspectionTask>(`/tasks/${id}`),
  createTask: (data: Partial<InspectionTask>) => fetchAPI<InspectionTask>(`/tasks`, { method: 'POST', body: JSON.stringify(data) }),
  runTask: (id: string) => fetchAPI<{ task: InspectionTask; message: string }>(`/tasks/${id}/run`, { method: 'POST' }),
  deleteTask: (id: string) => fetchAPI<{ message: string }>(`/tasks/${id}`, { method: 'DELETE' }),

  // Results
  getResults: (taskId?: string, targetId?: number) => fetchAPI<{ results: InspectionResult[] }>(`/results${taskId ? `?task_id=${taskId}` : ''}${targetId ? `&target_id=${targetId}` : ''}`),

  // Reports
  getReports: () => fetchAPI<{ reports: InspectionReport[] }>(`/reports`),
  getReport: (id: string) => fetchAPI<InspectionReport>(`/reports/${id}`),
  generateReport: (taskId: string, format: ReportFormat = 'html') => fetchAPI<InspectionReport>(`/reports/generate`, { method: 'POST', body: JSON.stringify({ task_id: taskId, format }) }),

  // Knowledge
  getKnowledge: () => fetchAPI<{ entries: KnowledgeEntry[] }>(`/knowledge`),
  getKnowledgeDetail: (id: string) => fetchAPI<KnowledgeEntry>(`/knowledge/${id}`),
};

// ============================================================
// 工具函数
// ============================================================

export const TARGET_TYPE_LABELS: Record<TargetType, string> = {
  linux: 'Linux',
  windows: 'Windows',
  aix: 'AIX',
  san_switch: 'SAN交换机',
  network: '网络设备',
  bmc: 'BMC',
  storage: '存储设备',
  oracle: 'Oracle',
  mysql: 'MySQL',
  postgres: 'PostgreSQL',
  mssql: 'SQL Server',
  dm8: '达梦 DM8',
  tidb: 'TiDB',
  kingbase: 'KingbaseES',
  gbase: 'GBase 8s',
  ivorysql: 'IvorySQL',
  yashandb: 'YashanDB',
};

export const TARGET_TYPE_ICONS: Record<TargetType, string> = {
  linux: '🐧',
  windows: '🪟',
  aix: '🔷',
  san_switch: '🔌',
  network: '🌐',
  bmc: '🔧',
  storage: '💾',
  oracle: '🔶',
  mysql: '🐬',
  postgres: '🐘',
  mssql: '📊',
  dm8: '🗄️',
  tidb: '⚡',
  kingbase: '👑',
  gbase: '🔷',
  ivorysql: '🦣',
  yashandb: '🏔️',
};

export const STATUS_COLORS: Record<string, string> = {
  ok: 'text-green-400',
  warning: 'text-amber-400',
  critical: 'text-red-400',
  error: 'text-red-500',
  skipped: 'text-slate-400',
  active: 'text-green-400',
  inactive: 'text-slate-400',
  pending: 'text-blue-400',
  running: 'text-cyan-400',
  completed: 'text-green-400',
  failed: 'text-red-400',
};

export const STATUS_BG: Record<string, string> = {
  ok: 'bg-green-500/20 text-green-400',
  warning: 'bg-amber-500/20 text-amber-400',
  critical: 'bg-red-500/20 text-red-400',
  pending: 'bg-blue-500/20 text-blue-400',
  running: 'bg-cyan-500/20 text-cyan-400',
  completed: 'bg-green-500/20 text-green-400',
  failed: 'bg-red-500/20 text-red-400',
};

export const PROTOCOL_LABELS: Record<ConnectionProtocol, string> = {
  ssh: 'SSH',
  snmp: 'SNMP',
  jdbc: 'JDBC',
  odbc: 'ODBC',
  telnet: 'Telnet',
  http: 'HTTP(S)',
  ipmi: 'IPMI',
  redfish: 'Redfish',
  dbcheck: 'DBCheck引擎',
};

export const SCHEDULE_LABELS: Record<ScheduleType, string> = {
  once: '一次性',
  minutely: '每分钟',
  hourly: '每小时',
  daily: '每天',
  weekly: '每周',
  monthly: '每月',
};

export function getHealthColor(score: number): string {
  if (score >= 90) return 'text-green-400';
  if (score >= 70) return 'text-amber-400';
  return 'text-red-400';
}

export function getHealthBg(score: number): string {
  if (score >= 90) return 'bg-green-500/20';
  if (score >= 70) return 'bg-amber-500/20';
  return 'bg-red-500/20';
}

export function formatTime(isoStr: string | null): string {
  if (!isoStr) return '-';
  const d = new Date(isoStr);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return '刚刚';
  if (diffMin < 60) return `${diffMin}分钟前`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}小时前`;
  const diffDay = Math.floor(diffHr / 24);
  if (diffDay < 30) return `${diffDay}天前`;
  return d.toLocaleDateString('zh-CN');
}

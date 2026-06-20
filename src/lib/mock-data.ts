/**
 * Oracle 容灾平台 - 模拟数据层
 * 包含所有页面使用的模拟数据，与后端API一一对应
 */

// ========== 类型定义 ==========
export interface OracleInstance {
  id: string;
  name: string;
  version: '10g' | '11g' | '19c' | '23c' | '26ai';
  role: 'PRIMARY' | 'PHYSICAL_STANDBY' | 'LOGICAL_STANDBY' | 'SNAPSHOT_STANDBY';
  status: 'OPEN' | 'MOUNTED' | 'READ ONLY WITH APPLY' | 'MOUNTED (SRL)';
  host: string;
  port: number;
  dbUniqueName: string;
  dbid: number;
  openMode: string;
  logMode: string;
  protectionMode: string;
  dgConfigId: string;
  syncLagSeconds: number;
  lastSyncTime: string;
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  sessions: number;
  uptime: string;
}

export interface DGConfig {
  id: string;
  name: string;
  type: 'DG' | 'ADG' | 'FSFO';
  primaryId: string;
  standbyIds: string[];
  fsfoEnabled: boolean;
  fsfoTarget: string | null;
  observerRunning: boolean;
  protectionMode: 'MaxProtection' | 'MaxAvailability' | 'MaxPerformance';
  transportMode: 'SYNC' | 'ASYNC' | 'FASTSYNC';
  delayMins: number;
  status: 'HEALTHY' | 'WARNING' | 'ERROR' | 'CREATING';
  created: string;
  lastSwitchover: string | null;
  lastFailover: string | null;
}

export interface SyncLog {
  id: string;
  timestamp: string;
  sequence: number;
  thread: number;
  source: string;
  destination: string;
  status: 'VALID' | 'GAP' | 'ERROR' | 'APPLYING';
  size: string;
  applied: boolean;
  applyTime: string | null;
}

export interface AlertLog {
  id: string;
  timestamp: string;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  source: string;
  message: string;
  acknowledged: boolean;
}

export interface PerformanceMetric {
  timestamp: string;
  tps: number;
  qps: number;
  redoRate: number;
  applyRate: number;
  lagSeconds: number;
  cpuPercent: number;
  memoryPercent: number;
  diskIOPS: number;
  networkMBps: number;
}

export interface ZFSDataset {
  name: string;
  used: string;
  avail: string;
  refer: string;
  mountpoint: string;
  snapshots: number;
  latestSnapshot: string | null;
  compression: string;
  dedup: string;
}

export interface K8sResource {
  name: string;
  namespace: string;
  kind: 'Pod' | 'Deployment' | 'StatefulSet' | 'Service' | 'PVC';
  status: string;
  replicas: string;
  age: string;
  cpu: string;
  memory: string;
}

// ========== 模拟数据 ==========

export const mockInstances: OracleInstance[] = [
  {
    id: 'inst-001', name: 'PROD-DB01', version: '19c', role: 'PRIMARY',
    status: 'OPEN', host: '10.0.1.10', port: 1521, dbUniqueName: 'PROD_db1',
    dbid: 1234567890, openMode: 'READ WRITE', logMode: 'ARCHIVELOG',
    protectionMode: 'Maximum Availability', dgConfigId: 'dg-001',
    syncLagSeconds: 0, lastSyncTime: '2026-06-02T10:30:00Z',
    cpuUsage: 67, memoryUsage: 72, diskUsage: 58, sessions: 245, uptime: '45d 12h'
  },
  {
    id: 'inst-002', name: 'PROD-DB02', version: '19c', role: 'PHYSICAL_STANDBY',
    status: 'READ ONLY WITH APPLY', host: '10.0.2.10', port: 1521, dbUniqueName: 'PROD_db2',
    dbid: 1234567891, openMode: 'READ ONLY WITH APPLY', logMode: 'ARCHIVELOG',
    protectionMode: 'Maximum Availability', dgConfigId: 'dg-001',
    syncLagSeconds: 3, lastSyncTime: '2026-06-02T10:29:57Z',
    cpuUsage: 23, memoryUsage: 45, diskUsage: 56, sessions: 12, uptime: '45d 12h'
  },
  {
    id: 'inst-003', name: 'PROD-DB03', version: '19c', role: 'PHYSICAL_STANDBY',
    status: 'MOUNTED (SRL)', host: '10.0.3.10', port: 1521, dbUniqueName: 'PROD_db3',
    dbid: 1234567892, openMode: 'MOUNTED', logMode: 'ARCHIVELOG',
    protectionMode: 'Maximum Availability', dgConfigId: 'dg-001',
    syncLagSeconds: 8, lastSyncTime: '2026-06-02T10:29:52Z',
    cpuUsage: 15, memoryUsage: 38, diskUsage: 54, sessions: 3, uptime: '30d 8h'
  },
  {
    id: 'inst-004', name: 'FIN-DB01', version: '23c', role: 'PRIMARY',
    status: 'OPEN', host: '10.0.1.20', port: 1521, dbUniqueName: 'FIN_db1',
    dbid: 2345678901, openMode: 'READ WRITE', logMode: 'ARCHIVELOG',
    protectionMode: 'Maximum Performance', dgConfigId: 'dg-002',
    syncLagSeconds: 0, lastSyncTime: '2026-06-02T10:30:00Z',
    cpuUsage: 82, memoryUsage: 85, diskUsage: 72, sessions: 189, uptime: '120d 5h'
  },
  {
    id: 'inst-005', name: 'FIN-DB02', version: '23c', role: 'PHYSICAL_STANDBY',
    status: 'READ ONLY WITH APPLY', host: '10.0.2.20', port: 1521, dbUniqueName: 'FIN_db2',
    dbid: 2345678902, openMode: 'READ ONLY WITH APPLY', logMode: 'ARCHIVELOG',
    protectionMode: 'Maximum Performance', dgConfigId: 'dg-002',
    syncLagSeconds: 12, lastSyncTime: '2026-06-02T10:29:48Z',
    cpuUsage: 35, memoryUsage: 52, diskUsage: 70, sessions: 8, uptime: '120d 5h'
  },
  {
    id: 'inst-006', name: 'HR-DB01', version: '11g', role: 'PRIMARY',
    status: 'OPEN', host: '10.0.1.30', port: 1521, dbUniqueName: 'HR_db1',
    dbid: 3456789012, openMode: 'READ WRITE', logMode: 'ARCHIVELOG',
    protectionMode: 'Maximum Performance', dgConfigId: 'dg-003',
    syncLagSeconds: 0, lastSyncTime: '2026-06-02T10:30:00Z',
    cpuUsage: 45, memoryUsage: 55, diskUsage: 42, sessions: 67, uptime: '200d 15h'
  },
  {
    id: 'inst-007', name: 'HR-DB02', version: '11g', role: 'PHYSICAL_STANDBY',
    status: 'READ ONLY WITH APPLY', host: '10.0.2.30', port: 1521, dbUniqueName: 'HR_db2',
    dbid: 3456789013, openMode: 'READ ONLY WITH APPLY', logMode: 'ARCHIVELOG',
    protectionMode: 'Maximum Performance', dgConfigId: 'dg-003',
    syncLagSeconds: 5, lastSyncTime: '2026-06-02T10:29:55Z',
    cpuUsage: 18, memoryUsage: 40, diskUsage: 40, sessions: 5, uptime: '200d 15h'
  },
  {
    id: 'inst-008', name: 'AI-DB01', version: '26ai', role: 'PRIMARY',
    status: 'OPEN', host: '10.0.1.40', port: 1521, dbUniqueName: 'AI_db1',
    dbid: 4567890123, openMode: 'READ WRITE', logMode: 'ARCHIVELOG',
    protectionMode: 'Maximum Availability', dgConfigId: 'dg-004',
    syncLagSeconds: 0, lastSyncTime: '2026-06-02T10:30:00Z',
    cpuUsage: 91, memoryUsage: 88, diskUsage: 65, sessions: 312, uptime: '15d 3h'
  },
  {
    id: 'inst-009', name: 'AI-DB02', version: '26ai', role: 'PHYSICAL_STANDBY',
    status: 'READ ONLY WITH APPLY', host: '10.0.2.40', port: 1521, dbUniqueName: 'AI_db2',
    dbid: 4567890124, openMode: 'READ ONLY WITH APPLY', logMode: 'ARCHIVELOG',
    protectionMode: 'Maximum Availability', dgConfigId: 'dg-004',
    syncLagSeconds: 2, lastSyncTime: '2026-06-02T10:29:58Z',
    cpuUsage: 42, memoryUsage: 55, diskUsage: 63, sessions: 15, uptime: '15d 3h'
  },
  {
    id: 'inst-010', name: 'LEGACY-DB01', version: '10g', role: 'PRIMARY',
    status: 'OPEN', host: '10.0.1.50', port: 1521, dbUniqueName: 'LEGACY_db1',
    dbid: 5678901234, openMode: 'READ WRITE', logMode: 'ARCHIVELOG',
    protectionMode: 'Maximum Performance', dgConfigId: 'dg-005',
    syncLagSeconds: 0, lastSyncTime: '2026-06-02T10:30:00Z',
    cpuUsage: 33, memoryUsage: 48, diskUsage: 80, sessions: 23, uptime: '365d 1h'
  },
  {
    id: 'inst-011', name: 'LEGACY-DB02', version: '10g', role: 'PHYSICAL_STANDBY',
    status: 'MOUNTED (SRL)', host: '10.0.2.50', port: 1521, dbUniqueName: 'LEGACY_db2',
    dbid: 5678901235, openMode: 'MOUNTED', logMode: 'ARCHIVELOG',
    protectionMode: 'Maximum Performance', dgConfigId: 'dg-005',
    syncLagSeconds: 45, lastSyncTime: '2026-06-02T10:29:15Z',
    cpuUsage: 10, memoryUsage: 30, diskUsage: 78, sessions: 2, uptime: '365d 1h'
  },
];

export const mockDGConfigs: DGConfig[] = [
  {
    id: 'dg-001', name: 'PROD-DG', type: 'ADG', primaryId: 'inst-001',
    standbyIds: ['inst-002', 'inst-003'], fsfoEnabled: true, fsfoTarget: 'inst-002',
    observerRunning: true, protectionMode: 'MaxAvailability', transportMode: 'SYNC',
    delayMins: 0, status: 'HEALTHY', created: '2026-01-15',
    lastSwitchover: '2026-05-20', lastFailover: null
  },
  {
    id: 'dg-002', name: 'FIN-DG', type: 'ADG', primaryId: 'inst-004',
    standbyIds: ['inst-005'], fsfoEnabled: false, fsfoTarget: null,
    observerRunning: false, protectionMode: 'MaxPerformance', transportMode: 'ASYNC',
    delayMins: 15, status: 'WARNING', created: '2026-02-01',
    lastSwitchover: null, lastFailover: null
  },
  {
    id: 'dg-003', name: 'HR-DG', type: 'DG', primaryId: 'inst-006',
    standbyIds: ['inst-007'], fsfoEnabled: false, fsfoTarget: null,
    observerRunning: false, protectionMode: 'MaxPerformance', transportMode: 'ASYNC',
    delayMins: 30, status: 'HEALTHY', created: '2025-08-10',
    lastSwitchover: '2026-03-15', lastFailover: null
  },
  {
    id: 'dg-004', name: 'AI-DG', type: 'FSFO', primaryId: 'inst-008',
    standbyIds: ['inst-009'], fsfoEnabled: true, fsfoTarget: 'inst-009',
    observerRunning: true, protectionMode: 'MaxAvailability', transportMode: 'FASTSYNC',
    delayMins: 0, status: 'HEALTHY', created: '2026-05-18',
    lastSwitchover: null, lastFailover: null
  },
  {
    id: 'dg-005', name: 'LEGACY-DG', type: 'DG', primaryId: 'inst-010',
    standbyIds: ['inst-011'], fsfoEnabled: false, fsfoTarget: null,
    observerRunning: false, protectionMode: 'MaxPerformance', transportMode: 'ASYNC',
    delayMins: 60, status: 'ERROR', created: '2025-01-01',
    lastSwitchover: null, lastFailover: '2025-11-20'
  },
];

// 生成模拟同步日志
function generateSyncLogs(count: number): SyncLog[] {
  const logs: SyncLog[] = [];
  const sources = ['PROD-DB01', 'FIN-DB01', 'HR-DB01', 'AI-DB01', 'LEGACY-DB01'];
  const dests = ['PROD-DB02', 'FIN-DB02', 'HR-DB02', 'AI-DB02', 'LEGACY-DB02'];
  const statuses: SyncLog['status'][] = ['VALID', 'VALID', 'VALID', 'VALID', 'GAP', 'APPLYING'];
  const now = new Date('2026-06-02T10:30:00Z');

  for (let i = 0; i < count; i++) {
    const idx = i % 5;
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    logs.push({
      id: `sync-${String(i + 1).padStart(4, '0')}`,
      timestamp: new Date(now.getTime() - i * 30000).toISOString(),
      sequence: 1000 + count - i,
      thread: (idx % 2) + 1,
      source: sources[idx],
      destination: dests[idx],
      status,
      size: `${(Math.random() * 200 + 50).toFixed(0)}M`,
      applied: status === 'VALID',
      applyTime: status === 'VALID' ? new Date(now.getTime() - i * 30000 + Math.random() * 5000).toISOString() : null,
    });
  }
  return logs;
}

export const mockSyncLogs = generateSyncLogs(50);

// 生成告警日志
export const mockAlertLogs: AlertLog[] = [
  {
    id: 'alert-001', timestamp: '2026-06-02T10:28:00Z', level: 'CRITICAL',
    source: 'LEGACY-DB02', message: 'Redo transport gap detected - 45 seconds lag exceeds threshold', acknowledged: false
  },
  {
    id: 'alert-002', timestamp: '2026-06-02T10:25:00Z', level: 'WARNING',
    source: 'FIN-DB01', message: 'CPU usage 82% - approaching critical threshold', acknowledged: false
  },
  {
    id: 'alert-003', timestamp: '2026-06-02T10:20:00Z', level: 'WARNING',
    source: 'FIN-DB02', message: 'ADG sync lag 12 seconds - ASYNC mode degradation', acknowledged: true
  },
  {
    id: 'alert-004', timestamp: '2026-06-02T10:15:00Z', level: 'INFO',
    source: 'PROD-DG', message: 'FSFO Observer health check passed - target inst-002', acknowledged: true
  },
  {
    id: 'alert-005', timestamp: '2026-06-02T10:10:00Z', level: 'ERROR',
    source: 'LEGACY-DB02', message: 'ORA-12541: TNS:no listener - retrying connection', acknowledged: false
  },
  {
    id: 'alert-006', timestamp: '2026-06-02T10:05:00Z', level: 'INFO',
    source: 'AI-DG', message: 'ADG Real Apply running normally - lag 2s', acknowledged: true
  },
  {
    id: 'alert-007', timestamp: '2026-06-02T09:55:00Z', level: 'WARNING',
    source: 'PROD-DB03', message: 'Mounted standby - not in real apply mode', acknowledged: true
  },
  {
    id: 'alert-008', timestamp: '2026-06-02T09:45:00Z', level: 'CRITICAL',
    source: 'LEGACY-DB02', message: 'Disk usage 78% - approaching capacity on /u01', acknowledged: false
  },
  {
    id: 'alert-009', timestamp: '2026-06-02T09:30:00Z', level: 'INFO',
    source: 'AI-DB01', message: 'Oracle 26ai vector query performance within SLA', acknowledged: true
  },
  {
    id: 'alert-010', timestamp: '2026-06-02T09:15:00Z', level: 'ERROR',
    source: 'LEGACY-DG', message: 'Data Guard Broker configuration mismatch detected', acknowledged: false
  },
];

// 生成性能指标
function generatePerfMetrics(minutes: number): PerformanceMetric[] {
  const data: PerformanceMetric[] = [];
  const now = new Date('2026-06-02T10:30:00Z');
  for (let i = minutes; i >= 0; i--) {
    const t = new Date(now.getTime() - i * 60000);
    data.push({
      timestamp: t.toISOString(),
      tps: Math.floor(800 + Math.random() * 400 + Math.sin(i / 10) * 200),
      qps: Math.floor(5000 + Math.random() * 2000 + Math.sin(i / 8) * 1000),
      redoRate: Math.floor(15 + Math.random() * 10 + Math.sin(i / 12) * 5),
      applyRate: Math.floor(14 + Math.random() * 10 + Math.sin(i / 12) * 5),
      lagSeconds: Math.floor(Math.random() * 5 + Math.sin(i / 20) * 3 + Math.abs(Math.sin(i / 30)) * 2),
      cpuPercent: Math.floor(55 + Math.random() * 20 + Math.sin(i / 15) * 10),
      memoryPercent: Math.floor(65 + Math.random() * 10 + Math.sin(i / 20) * 5),
      diskIOPS: Math.floor(3000 + Math.random() * 2000 + Math.sin(i / 10) * 1000),
      networkMBps: Math.floor(50 + Math.random() * 30 + Math.sin(i / 8) * 15),
    });
  }
  return data;
}

export const mockPerfMetrics = generatePerfMetrics(60);

// ZFS 数据集
export const mockZFSDatasets: ZFSDataset[] = [
  { name: 'zp1/oradata/PROD', used: '2.1T', avail: '3.9T', refer: '2.1T', mountpoint: '/u02/oradata/PROD', snapshots: 48, latestSnapshot: 'zfs-auto-snap_hourly-2026-06-02-10', compression: 'lz4', dedup: 'off' },
  { name: 'zp1/oradata/FIN', used: '1.5T', avail: '4.5T', refer: '1.5T', mountpoint: '/u02/oradata/FIN', snapshots: 36, latestSnapshot: 'zfs-auto-snap_hourly-2026-06-02-10', compression: 'lz4', dedup: 'off' },
  { name: 'zp1/oradata/HR', used: '800G', avail: '5.2T', refer: '800G', mountpoint: '/u02/oradata/HR', snapshots: 24, latestSnapshot: 'zfs-auto-snap_daily-2026-06-02', compression: 'lz4', dedup: 'off' },
  { name: 'zp1/oradata/AI', used: '3.2T', avail: '2.8T', refer: '3.2T', mountpoint: '/u02/oradata/AI', snapshots: 72, latestSnapshot: 'zfs-auto-snap_frequent-2026-06-02-1025', compression: 'zstd', dedup: 'verify' },
  { name: 'zp1/oradata/LEGACY', used: '1.8T', avail: '4.2T', refer: '1.8T', mountpoint: '/u02/oradata/LEGACY', snapshots: 12, latestSnapshot: 'zfs-auto-snap_daily-2026-06-01', compression: 'lz4', dedup: 'off' },
  { name: 'zp1/fast_recovery_area', used: '900G', avail: '5.1T', refer: '900G', mountpoint: '/u03/fast_recovery_area', snapshots: 48, latestSnapshot: 'zfs-auto-snap_hourly-2026-06-02-10', compression: 'lz4', dedup: 'off' },
];

// K8s 资源
export const mockK8sResources: K8sResource[] = [
  { name: 'oracle-prod-primary', namespace: 'oracle-dr', kind: 'StatefulSet', status: 'Running', replicas: '1/1', age: '45d', cpu: '8', memory: '32Gi' },
  { name: 'oracle-prod-standby-0', namespace: 'oracle-dr', kind: 'Pod', status: 'Running', replicas: '1/1', age: '45d', cpu: '4', memory: '16Gi' },
  { name: 'oracle-prod-standby-1', namespace: 'oracle-dr', kind: 'Pod', status: 'Running', replicas: '1/1', age: '30d', cpu: '4', memory: '16Gi' },
  { name: 'oracle-fin-primary', namespace: 'oracle-dr', kind: 'StatefulSet', status: 'Running', replicas: '1/1', age: '120d', cpu: '16', memory: '64Gi' },
  { name: 'oracle-fin-standby', namespace: 'oracle-dr', kind: 'Pod', status: 'Running', replicas: '1/1', age: '120d', cpu: '8', memory: '32Gi' },
  { name: 'oracle-ai-primary', namespace: 'oracle-dr', kind: 'StatefulSet', status: 'Running', replicas: '1/1', age: '15d', cpu: '32', memory: '128Gi' },
  { name: 'oracle-ai-standby', namespace: 'oracle-dr', kind: 'Pod', status: 'Running', replicas: '1/1', age: '15d', cpu: '16', memory: '64Gi' },
  { name: 'dg-broker', namespace: 'oracle-dr', kind: 'Deployment', status: 'Running', replicas: '2/2', age: '45d', cpu: '2', memory: '4Gi' },
  { name: 'fsfo-observer', namespace: 'oracle-dr', kind: 'Deployment', status: 'Running', replicas: '1/1', age: '45d', cpu: '1', memory: '2Gi' },
  { name: 'zfs-snapshot-controller', namespace: 'oracle-dr', kind: 'Deployment', status: 'Running', replicas: '1/1', age: '45d', cpu: '500m', memory: '1Gi' },
  { name: 'oradb-monitor', namespace: 'oracle-dr', kind: 'Deployment', status: 'Running', replicas: '2/2', age: '45d', cpu: '2', memory: '4Gi' },
  { name: 'oracle-dr-service', namespace: 'oracle-dr', kind: 'Service', status: 'Active', replicas: '-', age: '45d', cpu: '-', memory: '-' },
  { name: 'pvc-oradata-prod', namespace: 'oracle-dr', kind: 'PVC', status: 'Bound', replicas: '-', age: '45d', cpu: '-', memory: '-' },
  { name: 'pvc-oradata-ai', namespace: 'oracle-dr', kind: 'PVC', status: 'Bound', replicas: '-', age: '15d', cpu: '-', memory: '-' },
];

// ========== 辅助函数 ==========

/** 获取实例对应的DG配置 */
export function getDGConfigForInstance(instanceId: string): DGConfig | undefined {
  const inst = mockInstances.find(i => i.id === instanceId);
  if (!inst) return undefined;
  return mockDGConfigs.find(dg => dg.id === inst.dgConfigId);
}

/** 获取DG配置的所有实例 */
export function getInstancesForDGConfig(dgConfigId: string): OracleInstance[] {
  return mockInstances.filter(i => i.dgConfigId === dgConfigId);
}

/** 版本颜色映射 */
export const versionColorMap: Record<string, string> = {
  '10g': '#e74c3c',
  '11g': '#e67e22',
  '19c': '#3498db',
  '23c': '#2ecc71',
  '26ai': '#9b59b6',
};

/** 状态颜色映射 */
export const statusColorMap: Record<string, string> = {
  'HEALTHY': '#22c55e',
  'WARNING': '#eab308',
  'ERROR': '#ef4444',
  'CREATING': '#3b82f6',
};

/** 角色标签 */
export const roleLabelMap: Record<string, string> = {
  'PRIMARY': '主库',
  'PHYSICAL_STANDBY': '物理备库',
  'LOGICAL_STANDBY': '逻辑备库',
  'SNAPSHOT_STANDBY': '快照备库',
};

/** 格式化同步延迟 */
export function formatLag(seconds: number): string {
  if (seconds === 0) return '实时同步';
  if (seconds < 60) return `${seconds}秒`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分${seconds % 60}秒`;
  return `${Math.floor(seconds / 3600)}时${Math.floor((seconds % 3600) / 60)}分`;
}

// Failover/Switchover 历史记录
export interface FailoverHistory {
  id: string;
  timestamp: string;
  dgName: string;
  type: 'SWITCHOVER' | 'FAILOVER';
  fromPrimary: string;
  toPrimary: string;
  durationSecs: number;
  dataLoss: number;
  status: 'COMPLETED' | 'FAILED' | 'IN_PROGRESS';
}

export const mockFailoverHistory: FailoverHistory[] = [
  {
    id: 'fh-001', timestamp: '2026-05-20T14:30:00Z', dgName: 'PROD-DG',
    type: 'SWITCHOVER', fromPrimary: 'PROD-DB01', toPrimary: 'PROD-DB02',
    durationSecs: 45, dataLoss: 0, status: 'COMPLETED'
  },
  {
    id: 'fh-002', timestamp: '2026-03-15T09:15:00Z', dgName: 'HR-DG',
    type: 'SWITCHOVER', fromPrimary: 'HR-DB01', toPrimary: 'HR-DB02',
    durationSecs: 38, dataLoss: 0, status: 'COMPLETED'
  },
  {
    id: 'fh-003', timestamp: '2025-11-20T03:22:00Z', dgName: 'LEGACY-DG',
    type: 'FAILOVER', fromPrimary: 'LEGACY-DB01', toPrimary: 'LEGACY-DB02',
    durationSecs: 120, dataLoss: 15, status: 'COMPLETED'
  },
  {
    id: 'fh-004', timestamp: '2026-04-10T22:05:00Z', dgName: 'FIN-DG',
    type: 'FAILOVER', fromPrimary: 'FIN-DB01', toPrimary: 'FIN-DB02',
    durationSecs: 90, dataLoss: 3, status: 'COMPLETED'
  },
  {
    id: 'fh-005', timestamp: '2026-05-20T15:10:00Z', dgName: 'PROD-DG',
    type: 'SWITCHOVER', fromPrimary: 'PROD-DB02', toPrimary: 'PROD-DB01',
    durationSecs: 42, dataLoss: 0, status: 'COMPLETED'
  },
];

// 性能指标（重命名导出，兼容页面引用）
export const mockPerformanceMetrics = mockPerfMetrics;

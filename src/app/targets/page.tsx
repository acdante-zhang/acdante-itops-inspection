'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  Monitor, Plus, Search, Filter, Wifi, WifiOff, Trash2,
  RefreshCw, Upload, MoreHorizontal, Shield, ChevronDown,
  Server, Database, Network, HardDrive, Cpu,
} from 'lucide-react';
import { api, TARGET_TYPE_LABELS, TARGET_TYPE_ICONS, PROTOCOL_LABELS, STATUS_BG, formatTime, getHealthColor } from '@/lib/api';
import type { InspectionTarget, TargetType, ConnectionProtocol, ConnectionParams } from '@/lib/api';

const TARGET_TYPES: TargetType[] = ['linux', 'windows', 'aix', 'san_switch', 'network', 'bmc', 'storage', 'oracle', 'mysql', 'postgres', 'mssql'];
const PROTOCOLS: ConnectionProtocol[] = ['ssh', 'snmp', 'jdbc', 'odbc', 'telnet', 'http', 'ipmi', 'redfish'];

export default function TargetsPage() {
  const [targets, setTargets] = useState<InspectionTarget[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [testing, setTesting] = useState<number | null>(null);
  const [testResult, setTestResult] = useState<{ id: number; success: boolean; message: string } | null>(null);

  const loadTargets = useCallback(() => {
    setLoading(true);
    api.getTargets(filterType === 'all' ? undefined : filterType)
      .then(data => setTargets(data.targets || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [filterType]);

  useEffect(() => { loadTargets(); }, [loadTargets]);

  const filtered = targets.filter(t =>
    !search || t.name.toLowerCase().includes(search.toLowerCase()) || t.connection_params?.host?.toLowerCase().includes(search.toLowerCase())
  );

  const handleTest = async (id: number) => {
    setTesting(id);
    setTestResult(null);
    try {
      const result = await api.testTarget(id);
      setTestResult({ id, success: result.success, message: result.message });
    } catch (err) {
      setTestResult({ id, success: false, message: '连接测试失败' });
    } finally {
      setTesting(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定删除该巡检对象？')) return;
    try {
      await api.deleteTarget(id);
      setTargets(prev => prev.filter(t => t.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Monitor size={20} className="text-cyan-400" /> 巡检对象管理
          </h1>
          <p className="text-sm text-slate-400 mt-1">管理巡检目标设备、数据库和基础设施</p>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-3 py-2 text-sm bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-md flex items-center gap-1.5 transition-colors">
            <Upload size={14} /> 批量导入
          </button>
          <button onClick={() => setShowAdd(true)} className="px-4 py-2 text-sm bg-cyan-600 hover:bg-cyan-500 text-white rounded-md flex items-center gap-1.5 transition-colors">
            <Plus size={14} /> 添加对象
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-xs">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="搜索对象名称或主机..."
            className="w-full pl-9 pr-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>
        <div className="flex items-center gap-1 flex-wrap">
          <button onClick={() => setFilterType('all')} className={`px-3 py-1.5 text-xs rounded-md transition-colors ${filterType === 'all' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400 hover:text-slate-200'}`}>
            全部
          </button>
          {TARGET_TYPES.map(t => (
            <button key={t} onClick={() => setFilterType(t)} className={`px-3 py-1.5 text-xs rounded-md transition-colors ${filterType === t ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400 hover:text-slate-200'}`}>
              {TARGET_TYPE_LABELS[t]}
            </button>
          ))}
        </div>
      </div>

      {/* Targets Table */}
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700 bg-slate-800/80">
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">对象名称</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">类型</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">品牌/型号</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">连接信息</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">健康度</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">状态</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-slate-400">最近巡检</th>
              <th className="text-right px-4 py-3 text-xs font-medium text-slate-400">操作</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={8} className="text-center py-12 text-slate-500">加载中...</td></tr>
            ) : filtered.length === 0 ? (
              <tr><td colSpan={8} className="text-center py-12 text-slate-500">
                <Monitor size={32} className="mx-auto mb-2 text-slate-600" />
                <p>暂无巡检对象</p>
                <p className="text-xs mt-1">点击"添加对象"开始配置</p>
              </td></tr>
            ) : (
              filtered.map(target => (
                <tr key={target.id} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="text-base">{TARGET_TYPE_ICONS[target.type] || '🖥'}</span>
                      <div>
                        <p className="text-slate-200 font-medium">{target.name}</p>
                        <p className="text-[10px] text-slate-500">{target.location || '-'}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-xs bg-slate-700 text-slate-300">
                      {TARGET_TYPE_LABELS[target.type] || target.type}
                    </span>
                    {target.version && <span className="ml-1 text-[10px] text-slate-500">{target.version}</span>}
                  </td>
                  <td className="px-4 py-3 text-slate-300">
                    <p>{target.brand || '-'}</p>
                    <p className="text-[10px] text-slate-500">{target.model || ''}</p>
                  </td>
                  <td className="px-4 py-3">
                    <p className="text-slate-300 font-mono text-xs">{target.connection_params?.host || '-'}</p>
                    <p className="text-[10px] text-slate-500">
                      {PROTOCOL_LABELS[target.connection_params?.protocol] || target.connection_params?.protocol} : {target.connection_params?.port || '-'}
                    </p>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`font-bold ${getHealthColor(target.health_score)}`}>
                      {target.health_score}%
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${target.status === 'active' ? STATUS_BG.ok : target.status === 'inactive' ? STATUS_BG.failed : 'bg-slate-700 text-slate-400'}`}>
                      {target.status === 'active' ? '在线' : target.status === 'inactive' ? '离线' : target.status}
                    </span>
                    {target.offline_mode && (
                      <span className="ml-1 px-1.5 py-0.5 rounded text-[9px] bg-amber-500/20 text-amber-400">离线</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">
                    {formatTime(target.last_inspection_at)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => handleTest(target.id)}
                        disabled={testing === target.id}
                        className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-cyan-400 transition-colors disabled:opacity-50"
                        title="连接测试"
                      >
                        <RefreshCw size={14} className={testing === target.id ? 'animate-spin' : ''} />
                      </button>
                      <button
                        onClick={() => handleDelete(target.id)}
                        className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-red-400 transition-colors"
                        title="删除"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                    {testResult && testResult.id === target.id && (
                      <div className={`mt-1 text-[10px] ${testResult.success ? 'text-green-400' : 'text-red-400'}`}>
                        {testResult.message}
                      </div>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Add Target Modal */}
      {showAdd && <AddTargetModal onClose={() => setShowAdd(false)} onCreated={() => { setShowAdd(false); loadTargets(); }} />}
    </div>
  );
}

function AddTargetModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [form, setForm] = useState({
    name: '', type: 'linux' as TargetType, brand: '', model: '', version: '',
    location: '', offline_mode: false, tags: '',
    protocol: 'ssh' as ConnectionProtocol, host: '', port: 22,
    username: '', password: '', database_name: '',
    snmp_community: 'public', snmp_version: '2c', timeout: 30,
  });
  const [saving, setSaving] = useState(false);

  const defaultPorts: Record<string, number> = {
    ssh: 22, snmp: 161, jdbc: 1521, odbc: 1433, telnet: 23,
    http: 443, ipmi: 623, redfish: 443,
  };

  const handleProtocolChange = (p: ConnectionProtocol) => {
    setForm(prev => ({ ...prev, protocol: p, port: defaultPorts[p] || prev.port }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const connection_params: ConnectionParams = {
        protocol: form.protocol,
        host: form.host,
        port: form.port,
        username: form.username,
        password_enc: form.password,
        database_name: form.database_name || undefined,
        snmp_community: form.snmp_community || undefined,
        snmp_version: form.snmp_version || undefined,
        timeout: form.timeout,
      };
      await api.createTarget({
        name: form.name,
        type: form.type,
        brand: form.brand,
        model: form.model,
        version: form.version,
        location: form.location,
        offline_mode: form.offline_mode,
        connection_params,
        tags: form.tags ? form.tags.split(',').map(t => t.trim()) : [],
      });
      onCreated();
    } catch (err) {
      console.error(err);
      alert('创建失败，请重试');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-slate-800 border border-slate-700 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-100">添加巡检对象</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">对象名称 *</label>
              <input required value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="如: 生产数据库-主库" />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">对象类型 *</label>
              <select value={form.type} onChange={e => setForm(p => ({ ...p, type: e.target.value as TargetType }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500">
                {TARGET_TYPES.map(t => <option key={t} value={t}>{TARGET_TYPE_LABELS[t]}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">品牌</label>
              <input value={form.brand} onChange={e => setForm(p => ({ ...p, brand: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="如: 华为/Oracle/Red Hat" />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">型号</label>
              <input value={form.model} onChange={e => setForm(p => ({ ...p, model: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="如: OceanStor 5310" />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">版本</label>
              <input value={form.version} onChange={e => setForm(p => ({ ...p, version: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="如: 19c/RHEL 8.6" />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">位置/机房</label>
              <input value={form.location} onChange={e => setForm(p => ({ ...p, location: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="如: 北京IDC-A3" />
            </div>
          </div>

          <div className="border-t border-slate-700 pt-4">
            <h3 className="text-sm font-medium text-slate-300 mb-3">连接配置</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-slate-400 mb-1">连接协议 *</label>
                <select value={form.protocol} onChange={e => handleProtocolChange(e.target.value as ConnectionProtocol)} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500">
                  {PROTOCOLS.map(p => <option key={p} value={p}>{PROTOCOL_LABELS[p]}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">主机地址 *</label>
                <input required value={form.host} onChange={e => setForm(p => ({ ...p, host: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="IP 或域名" />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">端口</label>
                <input type="number" value={form.port} onChange={e => setForm(p => ({ ...p, port: Number(e.target.value) }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">用户名</label>
                <input value={form.username} onChange={e => setForm(p => ({ ...p, username: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">密码</label>
                <input type="password" value={form.password} onChange={e => setForm(p => ({ ...p, password: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
              </div>
              {(form.protocol === 'jdbc' || form.protocol === 'odbc') && (
                <div>
                  <label className="block text-xs text-slate-400 mb-1">数据库名</label>
                  <input value={form.database_name} onChange={e => setForm(p => ({ ...p, database_name: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
                </div>
              )}
              {form.protocol === 'snmp' && (
                <>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">SNMP Community</label>
                    <input value={form.snmp_community} onChange={e => setForm(p => ({ ...p, snmp_community: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">SNMP 版本</label>
                    <select value={form.snmp_version} onChange={e => setForm(p => ({ ...p, snmp_version: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500">
                      <option value="2c">v2c</option>
                      <option value="3">v3</option>
                    </select>
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input type="checkbox" id="offline" checked={form.offline_mode} onChange={e => setForm(p => ({ ...p, offline_mode: e.target.checked }))} className="rounded" />
            <label htmlFor="offline" className="text-xs text-slate-400">离线模式（仅接受上传的采集数据）</label>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm bg-slate-700 text-slate-300 rounded-md hover:bg-slate-600 transition-colors">取消</button>
            <button type="submit" disabled={saving} className="px-4 py-2 text-sm bg-cyan-600 text-white rounded-md hover:bg-cyan-500 transition-colors disabled:opacity-50">
              {saving ? '创建中...' : '创建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

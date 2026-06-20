'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  Radio, Search, Network, Cpu, Thermometer, HardDrive,
  Activity, Wifi, Shield, Server, Monitor, ChevronDown,
  ChevronRight, Zap, Plug, Cable, Globe, Eye, EyeOff,
  BarChart3, Download, FileText,
} from 'lucide-react';

// SNMP模板类型定义
interface SNMPTemplateItem {
  id: string;
  name: string;
  category: string;
  oid: string;
  oid_type: string;
  threshold?: { operator: string; critical: number; warning: number; unit: string } | null;
  is_table?: boolean;
  parser: string;
  suggestion?: string;
  weight: number;
  order: number;
}

interface SNMPTemplate {
  id: string;
  name: string;
  device_type: string;
  brand: string;
  model: string;
  description: string;
  vendor_mib: string;
  is_builtin: boolean;
  items: SNMPTemplateItem[];
}

// SNMP OID类型
interface SNMPOID {
  vendor: string;
  category: string;
  oid_name: string;
  oid: string;
  name: string;
  type: string;
  table?: boolean;
}

const DEVICE_TYPE_ICONS: Record<string, any> = {
  switch: Network,
  router: Globe,
  firewall: Shield,
  load_balancer: Activity,
  server: Server,
  storage: HardDrive,
  san_switch: Cable,
  security: Shield,
  network: Network,
};

const DEVICE_TYPE_LABELS: Record<string, string> = {
  switch: '交换机',
  router: '路由器',
  firewall: '防火墙',
  load_balancer: '负载均衡',
  server: '服务器',
  storage: '存储',
  san_switch: 'SAN交换机',
  security: '安全设备',
  network: '网络设备',
};

const CATEGORY_COLORS: Record<string, string> = {
  '系统': 'bg-blue-500/20 text-blue-400',
  'CPU': 'bg-cyan-500/20 text-cyan-400',
  '内存': 'bg-purple-500/20 text-purple-400',
  '硬件': 'bg-amber-500/20 text-amber-400',
  '接口': 'bg-green-500/20 text-green-400',
  '磁盘': 'bg-orange-500/20 text-orange-400',
  '连接': 'bg-indigo-500/20 text-indigo-400',
  '性能': 'bg-pink-500/20 text-pink-400',
  '端口': 'bg-teal-500/20 text-teal-400',
  '网络': 'bg-sky-500/20 text-sky-400',
  '池': 'bg-violet-500/20 text-violet-400',
  '虚拟服务': 'bg-rose-500/20 text-rose-400',
  '配置': 'bg-slate-500/20 text-slate-400',
  'SNMP': 'bg-lime-500/20 text-lime-400',
  '安全': 'bg-red-500/20 text-red-400',
  '散热': 'bg-yellow-500/20 text-yellow-400',
  '电源': 'bg-emerald-500/20 text-emerald-400',
  '存储': 'bg-orange-500/20 text-orange-400',
};

export default function SNMPPage() {
  const [templates, setTemplates] = useState<SNMPTemplate[]>([]);
  const [oids, setOids] = useState<SNMPOID[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'templates' | 'oids' | 'test'>('templates');
  const [filterBrand, setFilterBrand] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [searchOid, setSearchOid] = useState('');
  const [expandedTpl, setExpandedTpl] = useState<string | null>(null);
  const [selectedVendor, setSelectedVendor] = useState('all');

  // 连接测试
  const [testHost, setTestHost] = useState('');
  const [testCommunity, setTestCommunity] = useState('public');
  const [testVersion, setTestVersion] = useState('v2c');
  const [testResult, setTestResult] = useState<any>(null);
  const [testing, setTesting] = useState(false);

  const loadTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/snmp/templates');
      const data = await res.json();
      setTemplates(data.templates || []);
    } catch (err) {
      console.error('加载SNMP模板失败:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadOIDs = useCallback(async () => {
    try {
      const res = await fetch(`/api/v1/snmp/oids${selectedVendor !== 'all' ? `?vendor=${selectedVendor}` : ''}`);
      const data = await res.json();
      if (data.oids) {
        setOids(data.oids);
      }
    } catch (err) {
      console.error('加载OID失败:', err);
    }
  }, [selectedVendor]);

  useEffect(() => { loadTemplates(); }, [loadTemplates]);
  useEffect(() => { if (activeTab === 'oids') loadOIDs(); }, [activeTab, loadOIDs, selectedVendor]);

  const handleTestConnection = async () => {
    if (!testHost) return;
    setTesting(true);
    setTestResult(null);
    try {
      const res = await fetch('/api/v1/snmp/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          host: testHost,
          community: testCommunity,
          version: testVersion,
        }),
      });
      const data = await res.json();
      setTestResult(data);
    } catch (err: any) {
      setTestResult({ success: false, message: `测试失败: ${err.message}` });
    } finally {
      setTesting(false);
    }
  };

  const filteredTemplates = templates.filter(t => {
    if (filterBrand !== 'all' && t.brand !== filterBrand) return false;
    if (filterType !== 'all' && t.device_type !== filterType) return false;
    return true;
  });

  const filteredOids = searchOid
    ? oids.filter(o => o.name.toLowerCase().includes(searchOid.toLowerCase()) || o.oid.includes(searchOid))
    : oids;

  const brands = [...new Set(templates.map(t => t.brand))];
  const deviceTypes = [...new Set(templates.map(t => t.device_type))];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Radio size={20} className="text-cyan-400" /> SNMP 管理
          </h1>
          <p className="text-sm text-slate-400 mt-1">SNMP设备模板、OID浏览器、连接测试</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-700">
        {(['templates', 'oids', 'test'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-sm transition-colors ${
              activeTab === tab ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab === 'templates' ? `设备模板 (${templates.length})` : tab === 'oids' ? 'OID浏览器' : '连接测试'}
          </button>
        ))}
      </div>

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="space-y-3">
          {/* Filters */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-slate-500">品牌:</span>
            <button onClick={() => setFilterBrand('all')} className={`px-2 py-1 text-xs rounded ${filterBrand === 'all' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400'}`}>全部</button>
            {brands.map(b => (
              <button key={b} onClick={() => setFilterBrand(b)} className={`px-2 py-1 text-xs rounded ${filterBrand === b ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400'}`}>{b}</button>
            ))}
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-slate-500">类型:</span>
            <button onClick={() => setFilterType('all')} className={`px-2 py-1 text-xs rounded ${filterType === 'all' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400'}`}>全部</button>
            {deviceTypes.map(dt => (
              <button key={dt} onClick={() => setFilterType(dt)} className={`px-2 py-1 text-xs rounded ${filterType === dt ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400'}`}>{DEVICE_TYPE_LABELS[dt] || dt}</button>
            ))}
          </div>

          {loading ? (
            <div className="text-center py-12 text-slate-500">加载中...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {filteredTemplates.map(tmpl => {
                const IconComp = DEVICE_TYPE_ICONS[tmpl.device_type] || Monitor;
                return (
                  <div key={tmpl.id} className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden hover:border-slate-600 transition-colors">
                    <div
                      className="p-3 cursor-pointer"
                      onClick={() => setExpandedTpl(expandedTpl === tmpl.id ? null : tmpl.id)}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <IconComp size={16} className="text-cyan-400" />
                        <span className="text-sm text-slate-200 font-medium truncate">{tmpl.name}</span>
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="px-1.5 py-0.5 rounded text-[9px] bg-cyan-500/20 text-cyan-400">{tmpl.brand}</span>
                        <span className="px-1.5 py-0.5 rounded text-[9px] bg-slate-700 text-slate-400">{DEVICE_TYPE_LABELS[tmpl.device_type] || tmpl.device_type}</span>
                        <span className="text-[9px] text-slate-500 ml-auto">{tmpl.items.length} 个指标</span>
                        {expandedTpl === tmpl.id ? <ChevronDown size={12} className="text-slate-500" /> : <ChevronRight size={12} className="text-slate-500" />}
                      </div>
                    </div>

                    {expandedTpl === tmpl.id && (
                      <div className="border-t border-slate-700 p-3">
                        <p className="text-xs text-slate-400 mb-2">{tmpl.description}</p>
                        <div className="space-y-1 max-h-64 overflow-y-auto">
                          {tmpl.items.map(item => (
                            <div key={item.id} className="flex items-center gap-2 text-xs p-1.5 rounded hover:bg-slate-700/30">
                              <span className={`px-1 py-0.5 rounded text-[8px] ${CATEGORY_COLORS[item.category] || 'bg-slate-700 text-slate-400'}`}>{item.category}</span>
                              <span className="text-slate-300 flex-1">{item.name}</span>
                              <code className="text-[9px] text-slate-500 font-mono">{item.oid}</code>
                              {item.threshold && (
                                <span className="text-[8px] text-amber-400">⚠阈值</span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* OID Browser Tab */}
      {activeTab === 'oids' && (
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-md">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input value={searchOid} onChange={e => setSearchOid(e.target.value)} placeholder="搜索OID名称或编号..." className="w-full pl-9 pr-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500" />
            </div>
            <select value={selectedVendor} onChange={e => setSelectedVendor(e.target.value)} className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500">
              <option value="all">所有厂商</option>
              <option value="standard">标准MIB</option>
              <option value="huawei">华为</option>
              <option value="h3c">华三</option>
              <option value="cisco">思科</option>
              <option value="f5">F5</option>
              <option value="dell">Dell</option>
              <option value="sangfor">深信服</option>
              <option value="checkpoint">Checkpoint</option>
              <option value="brocade">Brocade</option>
              <option value="ucd_snmp">Net-SNMP</option>
              <option value="host_resources">主机资源</option>
            </select>
          </div>

          <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-2 px-3 text-slate-500 font-medium">厂商</th>
                  <th className="text-left py-2 px-3 text-slate-500 font-medium">分类</th>
                  <th className="text-left py-2 px-3 text-slate-500 font-medium">名称</th>
                  <th className="text-left py-2 px-3 text-slate-500 font-medium">OID</th>
                  <th className="text-left py-2 px-3 text-slate-500 font-medium">类型</th>
                  <th className="text-left py-2 px-3 text-slate-500 font-medium">表</th>
                </tr>
              </thead>
              <tbody>
                {filteredOids.slice(0, 100).map((oid, idx) => (
                  <tr key={idx} className="border-b border-slate-700/30 hover:bg-slate-700/20">
                    <td className="py-1.5 px-3 text-slate-400">{oid.vendor}</td>
                    <td className="py-1.5 px-3"><span className={`px-1.5 py-0.5 rounded text-[8px] ${CATEGORY_COLORS[oid.category] || 'bg-slate-700 text-slate-400'}`}>{oid.category}</span></td>
                    <td className="py-1.5 px-3 text-slate-200">{oid.name}</td>
                    <td className="py-1.5 px-3 font-mono text-slate-400">{oid.oid}</td>
                    <td className="py-1.5 px-3 text-slate-500">{oid.type}</td>
                    <td className="py-1.5 px-3 text-slate-500">{oid.table ? '✓' : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredOids.length > 100 && (
              <div className="p-3 text-center text-xs text-slate-500">显示前100条，共 {filteredOids.length} 条</div>
            )}
            {filteredOids.length === 0 && (
              <div className="p-8 text-center text-slate-500">
                <Search size={24} className="mx-auto mb-2 text-slate-600" />
                <p>未找到匹配的OID</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Connection Test Tab */}
      {activeTab === 'test' && (
        <div className="max-w-lg space-y-4">
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 space-y-3">
            <h3 className="text-sm font-medium text-slate-200">SNMP 连接测试</h3>
            <div>
              <label className="block text-xs text-slate-400 mb-1">目标主机 *</label>
              <input value={testHost} onChange={e => setTestHost(e.target.value)} placeholder="例如: 192.168.1.1" className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-slate-400 mb-1">SNMP版本</label>
                <select value={testVersion} onChange={e => setTestVersion(e.target.value)} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500">
                  <option value="v1">v1</option>
                  <option value="v2c">v2c</option>
                  <option value="v3">v3</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Community</label>
                <input value={testCommunity} onChange={e => setTestCommunity(e.target.value)} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
              </div>
            </div>
            <button
              onClick={handleTestConnection}
              disabled={testing || !testHost}
              className="w-full px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-md text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {testing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  测试中...
                </>
              ) : (
                <>
                  <Plug size={14} /> 测试连接
                </>
              )}
            </button>

            {testResult && (
              <div className={`p-3 rounded-md ${testResult.success ? 'bg-green-500/10 border border-green-500/20' : 'bg-red-500/10 border border-red-500/20'}`}>
                <div className={`text-sm font-medium ${testResult.success ? 'text-green-400' : 'text-red-400'}`}>
                  {testResult.success ? '✅ 连接成功' : '❌ 连接失败'}
                </div>
                <p className="text-xs text-slate-400 mt-1">{testResult.message}</p>
                {testResult.sys_descr && (
                  <p className="text-xs text-slate-500 mt-1 font-mono">{testResult.sys_descr}</p>
                )}
                {testResult.connect_time_ms && (
                  <p className="text-xs text-slate-500 mt-1">响应时间: {testResult.connect_time_ms.toFixed(1)}ms</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

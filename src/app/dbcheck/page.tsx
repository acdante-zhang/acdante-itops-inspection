'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  Database, RefreshCw, CheckCircle2, XCircle, AlertTriangle,
  Zap, Search, ChevronDown, ChevronRight, Shield, BookOpen,
  Download, Activity, Server, Terminal, GitBranch, ExternalLink,
} from 'lucide-react';

interface DBCheckDBType {
  target_type: string;
  dbcheck_type: string;
  label: string;
  icon: string;
  default_port: number;
  has_template: boolean;
}

interface DBCheckTemplate {
  id: string;
  name: string;
  target_type: string;
  db_type: string;
  description: string;
  item_count: number;
  is_dbcheck: boolean;
}

interface DBCheckRule {
  id: string;
  name: string;
  category: string;
  severity: string;
  enabled: boolean;
  db_types: string[];
  description?: string;
}

interface DBCheckVersion {
  version: string;
  commit: string;
  supported_types: number;
}

export default function DBCheckPage() {
  const [activeTab, setActiveTab] = useState<'overview' | 'templates' | 'rules' | 'update'>('overview');
  const [dbTypes, setDbTypes] = useState<DBCheckDBType[]>([]);
  const [templates, setTemplates] = useState<DBCheckTemplate[]>([]);
  const [rules, setRules] = useState<DBCheckRule[]>([]);
  const [version, setVersion] = useState<DBCheckVersion | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState('all');
  const [expandedTpl, setExpandedTpl] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [typesRes, versionRes] = await Promise.all([
        fetch('/api/v1/dbcheck/db-types').then(r => r.json()),
        fetch('/api/v1/dbcheck/version').then(r => r.json()),
      ]);
      setDbTypes(typesRes.db_types || []);
      setVersion(versionRes);
    } catch (err) {
      console.error('加载DBCheck数据失败:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadTemplates = useCallback(async () => {
    try {
      const res = await fetch(`/api/v1/dbcheck/templates${selectedType !== 'all' ? `?db_type=${selectedType}` : ''}`);
      const data = await res.json();
      setTemplates(data.templates || []);
    } catch (err) {
      console.error('加载模板失败:', err);
    }
  }, [selectedType]);

  const loadRules = useCallback(async () => {
    try {
      const res = await fetch(`/api/v1/dbcheck/rules${selectedType !== 'all' ? `?db_type=${selectedType}` : ''}`);
      const data = await res.json();
      setRules(data.rules || []);
    } catch (err) {
      console.error('加载规则失败:', err);
    }
  }, [selectedType]);

  useEffect(() => { loadData(); }, [loadData]);
  useEffect(() => { if (activeTab === 'templates') loadTemplates(); if (activeTab === 'rules') loadRules(); }, [activeTab, loadTemplates, loadRules]);

  const SEVERITY_COLORS: Record<string, string> = {
    high: 'bg-red-500/20 text-red-400',
    medium: 'bg-amber-500/20 text-amber-400',
    low: 'bg-blue-500/20 text-blue-400',
    info: 'bg-slate-500/20 text-slate-400',
    critical: 'bg-red-500/20 text-red-400',
    warning: 'bg-amber-500/20 text-amber-400',
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Database size={20} className="text-cyan-400" /> 数据库巡检引擎
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            DBCheck v{version?.version || '...'} — 10种数据库 · 130+规则 · AI诊断 · 专业报告
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-1 rounded text-xs bg-cyan-500/20 text-cyan-400 flex items-center gap-1">
            <GitBranch size={12} /> v{version?.version || 'loading'}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-700">
        {(['overview', 'templates', 'rules', 'update'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-sm transition-colors ${
              activeTab === tab ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab === 'overview' ? '引擎概览' : tab === 'templates' ? '巡检模板' : tab === 'rules' ? '规则管理' : '版本更新'}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-cyan-400">{dbTypes.length}</p>
              <p className="text-xs text-slate-400 mt-1">支持的数据库类型</p>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-green-400">{templates.length || 7}</p>
              <p className="text-xs text-slate-400 mt-1">内置巡检模板</p>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-amber-400">130+</p>
              <p className="text-xs text-slate-400 mt-1">YAML规则引擎</p>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 text-center">
              <p className="text-2xl font-bold text-purple-400">Ollama</p>
              <p className="text-xs text-slate-400 mt-1">本地AI诊断</p>
            </div>
          </div>

          {/* DB Types */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <h3 className="text-sm font-medium text-slate-200 mb-3">支持的数据库类型</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
              {dbTypes.map(t => (
                <div key={t.target_type} className="p-2 bg-slate-700/30 rounded text-center">
                  <span className="text-lg">{t.icon}</span>
                  <p className="text-xs text-slate-300 mt-1">{t.label}</p>
                  <p className="text-[9px] text-slate-500">端口 {t.default_port}</p>
                  {t.has_template && (
                    <span className="px-1 py-0.5 rounded text-[8px] bg-green-500/20 text-green-400 mt-1 inline-block">模板</span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Engine Info */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <h3 className="text-sm font-medium text-slate-200 mb-2">引擎信息</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-slate-400 text-xs">引擎版本</p>
                <p className="text-slate-200">{version?.version || 'unknown'}</p>
              </div>
              <div>
                <p className="text-slate-400 text-xs">Git Commit</p>
                <p className="text-slate-200 font-mono text-xs">{version?.commit || 'unknown'}</p>
              </div>
              <div>
                <p className="text-slate-400 text-xs">引擎来源</p>
                <p className="text-slate-200">
                  <a href="https://github.com/fiyo/DBCheck" target="_blank" className="text-cyan-400 hover:underline flex items-center gap-1">
                    github.com/fiyo/DBCheck <ExternalLink size={10} />
                  </a>
                </p>
              </div>
              <div>
                <p className="text-slate-400 text-xs">安装路径</p>
                <p className="text-slate-200 font-mono text-xs">vendor/dbcheck/</p>
              </div>
            </div>
          </div>

          {/* Capabilities */}
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <h3 className="text-sm font-medium text-slate-200 mb-2">核心能力</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {[
                { icon: Activity, title: '配置驱动巡检', desc: 'SQL模板存SQLite，Web UI动态管理，新增DB无需改代码' },
                { icon: Shield, title: 'YAML规则引擎', desc: '130+内置规则，安全沙箱eval，用户可自定义规则' },
                { icon: Zap, title: '智能诊断', desc: '本地Ollama AI诊断，慢查询深度分析，索引健康检查' },
                { icon: Server, title: '全版本适配', desc: 'Oracle 10g-21c自适应，MySQL 5.7/8.0/8.4，PG 12-16' },
                { icon: Download, title: '专业报告', desc: 'Word+PDF双格式，配置驱动章节，5类加权健康评分' },
                { icon: Terminal, title: '远程采集', desc: 'SSH隧道支持，远程系统资源采集(CPU/内存/磁盘)' },
              ].map((item, idx) => (
                <div key={idx} className="p-3 bg-slate-700/30 rounded">
                  <div className="flex items-center gap-2 mb-1">
                    <item.icon size={14} className="text-cyan-400" />
                    <span className="text-xs font-medium text-slate-200">{item.title}</span>
                  </div>
                  <p className="text-xs text-slate-400">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">数据库类型:</span>
            <button onClick={() => setSelectedType('all')} className={`px-2 py-1 text-xs rounded ${selectedType === 'all' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400'}`}>全部</button>
            {dbTypes.filter(t => t.has_template).map(t => (
              <button key={t.target_type} onClick={() => setSelectedType(t.target_type)} className={`px-2 py-1 text-xs rounded ${selectedType === t.target_type ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400'}`}>
                {t.icon} {t.label}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {templates.map(tmpl => (
              <div key={tmpl.id} className="bg-slate-800/50 border border-slate-700 rounded-lg p-3 hover:border-slate-600 transition-colors">
                <div className="flex items-center gap-2 mb-2">
                  <Database size={14} className="text-cyan-400" />
                  <span className="text-sm text-slate-200 font-medium">{tmpl.name}</span>
                </div>
                <p className="text-xs text-slate-400 mb-2">{tmpl.description?.slice(0, 80)}...</p>
                <div className="flex items-center gap-2">
                  <span className="px-1.5 py-0.5 rounded text-[9px] bg-cyan-500/20 text-cyan-400">DBCheck</span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] bg-purple-500/20 text-purple-400">{tmpl.item_count}+ 项</span>
                  <span className="text-[9px] text-slate-500 ml-auto">{tmpl.target_type}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Rules Tab */}
      {activeTab === 'rules' && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">过滤:</span>
            <button onClick={() => setSelectedType('all')} className={`px-2 py-1 text-xs rounded ${selectedType === 'all' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400'}`}>全部</button>
            {dbTypes.map(t => (
              <button key={t.target_type} onClick={() => setSelectedType(t.dbcheck_type)} className={`px-2 py-1 text-xs rounded ${selectedType === t.dbcheck_type ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400'}`}>
                {t.label}
              </button>
            ))}
          </div>

          {rules.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <Shield size={32} className="mx-auto mb-2 text-slate-600" />
              <p>暂无规则数据（规则引擎需真实DBCheck数据目录初始化）</p>
              <p className="text-xs mt-1">首次运行DBCheck巡检后，规则将自动加载</p>
            </div>
          ) : (
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-2 px-3 text-slate-500">ID</th>
                    <th className="text-left py-2 px-3 text-slate-500">名称</th>
                    <th className="text-left py-2 px-3 text-slate-500">分类</th>
                    <th className="text-left py-2 px-3 text-slate-500">级别</th>
                    <th className="text-left py-2 px-3 text-slate-500">状态</th>
                  </tr>
                </thead>
                <tbody>
                  {rules.map(rule => (
                    <tr key={rule.id} className="border-b border-slate-700/30 hover:bg-slate-700/20">
                      <td className="py-1.5 px-3 text-slate-400 font-mono">{rule.id}</td>
                      <td className="py-1.5 px-3 text-slate-200">{rule.name}</td>
                      <td className="py-1.5 px-3"><span className="px-1.5 py-0.5 rounded text-[8px] bg-slate-700 text-slate-400">{rule.category}</span></td>
                      <td className="py-1.5 px-3"><span className={`px-1.5 py-0.5 rounded text-[8px] ${SEVERITY_COLORS[rule.severity] || 'bg-slate-700 text-slate-400'}`}>{rule.severity}</span></td>
                      <td className="py-1.5 px-3">
                        {rule.enabled ? (
                          <span className="text-green-400 flex items-center gap-1"><CheckCircle2 size={10} /> 启用</span>
                        ) : (
                          <span className="text-slate-500 flex items-center gap-1"><XCircle size={10} /> 禁用</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Update Tab */}
      {activeTab === 'update' && (
        <div className="max-w-2xl space-y-4">
          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <h3 className="text-sm font-medium text-slate-200 mb-3">版本信息</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-xs text-slate-400">当前版本</span>
                <span className="text-xs text-cyan-400 font-mono">{version?.version || 'unknown'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-slate-400">Git Commit</span>
                <span className="text-xs text-slate-400 font-mono">{version?.commit || 'unknown'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-slate-400">支持的数据库</span>
                <span className="text-xs text-slate-400">{version?.supported_types || 0} 种</span>
              </div>
              <div className="flex justify-between">
                <span className="text-xs text-slate-400">安装方式</span>
                <span className="text-xs text-slate-400">vendor/dbcheck (内置)</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
            <h3 className="text-sm font-medium text-slate-200 mb-3">更新说明</h3>
            <div className="text-xs text-slate-400 space-y-2">
              <p>DBCheck作为独立项目维护，通过以下方式更新：</p>
              <div className="bg-slate-900 rounded p-3 font-mono text-slate-300">
                <p># 方式1: Git更新（推荐）</p>
                <p className="text-cyan-400">cd vendor/dbcheck</p>
                <p className="text-cyan-400">git pull origin main</p>
                <p className="mt-2"># 方式2: 手动下载替换</p>
                <p className="text-cyan-400"># 从 https://github.com/fiyo/DBCheck 下载最新版</p>
                <p className="text-cyan-400"># 替换 vendor/dbcheck/ 目录</p>
                <p className="mt-2"># 方式3: 版本锁定</p>
                <p className="text-cyan-400">git checkout v2.5.0  # 锁定到特定版本</p>
              </div>
              <p className="text-amber-400">⚠ 更新后请重启ITOps平台服务以重载模板库</p>
            </div>
          </div>

          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
            <h3 className="text-sm font-medium text-green-400 mb-2">✅ 集成优势</h3>
            <ul className="text-xs text-slate-400 space-y-1">
              <li>• DBCheck独立升级，不影响ITOps主平台</li>
              <li>• 新增数据库类型自动出现在ITOps中</li>
              <li>• 版本可锁定、可回退，生产环境安全可控</li>
              <li>• 桥接层隔离变更，API接口保持稳定</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

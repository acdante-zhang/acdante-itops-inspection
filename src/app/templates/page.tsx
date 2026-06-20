'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  FileText, Plus, Search, Shield, Lock, Eye, Edit3, Trash2,
  ChevronDown, ChevronRight, AlertTriangle, Copy, BookOpen,
} from 'lucide-react';
import { api, TARGET_TYPE_LABELS, TARGET_TYPE_ICONS } from '@/lib/api';
import type { InspectionTemplate, InspectionItem, TargetType } from '@/lib/api';

const TARGET_TYPES: TargetType[] = ['linux', 'windows', 'aix', 'san_switch', 'network', 'bmc', 'storage', 'oracle', 'mysql', 'postgres', 'mssql'];

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<InspectionTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<InspectionTemplate | null>(null);

  const loadTemplates = useCallback(() => {
    setLoading(true);
    api.getTemplates(filterType === 'all' ? undefined : filterType)
      .then(data => setTemplates(data.templates || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [filterType]);

  useEffect(() => { loadTemplates(); }, [loadTemplates]);

  const filtered = templates.filter(t =>
    !search || t.name.toLowerCase().includes(search.toLowerCase()) || t.brand?.toLowerCase().includes(search.toLowerCase())
  );

  const handleDelete = async (id: string) => {
    if (!confirm('确定删除该巡检模板？')) return;
    try {
      await api.deleteTemplate(id);
      setTemplates(prev => prev.filter(t => t.id !== id));
    } catch (err) { console.error(err); }
  };

  const handleDuplicate = async (tmpl: InspectionTemplate) => {
    try {
      const newTmpl = await api.createTemplate({
        ...tmpl,
        id: undefined,
        name: `${tmpl.name} (副本)`,
        is_builtin: false,
      });
      setTemplates(prev => [...prev, newTmpl]);
    } catch (err) { console.error(err); }
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileText size={20} className="text-cyan-400" /> 巡检模板管理
          </h1>
          <p className="text-sm text-slate-400 mt-1">定义巡检项、命令、解析规则与阈值判断</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="px-4 py-2 text-sm bg-cyan-600 hover:bg-cyan-500 text-white rounded-md flex items-center gap-1.5 transition-colors">
          <Plus size={14} /> 新建模板
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-xs">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="搜索模板名称或品牌..." className="w-full pl-9 pr-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500" />
        </div>
        <div className="flex items-center gap-1 flex-wrap">
          <button onClick={() => setFilterType('all')} className={`px-3 py-1.5 text-xs rounded-md transition-colors ${filterType === 'all' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400 hover:text-slate-200'}`}>全部</button>
          {TARGET_TYPES.map(t => (
            <button key={t} onClick={() => setFilterType(t)} className={`px-3 py-1.5 text-xs rounded-md transition-colors ${filterType === t ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400 hover:text-slate-200'}`}>
              {TARGET_TYPE_LABELS[t]}
            </button>
          ))}
        </div>
      </div>

      {/* Template List */}
      <div className="space-y-3">
        {loading ? (
          <div className="text-center py-12 text-slate-500">加载中...</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            <FileText size={32} className="mx-auto mb-2 text-slate-600" />
            <p>暂无巡检模板</p>
          </div>
        ) : (
          filtered.map(tmpl => (
            <div key={tmpl.id} className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
              <div
                className="flex items-center gap-4 p-4 cursor-pointer hover:bg-slate-700/30 transition-colors"
                onClick={() => setExpandedId(expandedId === tmpl.id ? null : tmpl.id)}
              >
                <span className="text-base">{TARGET_TYPE_ICONS[tmpl.target_type] || '📄'}</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-200 font-medium">{tmpl.name}</span>
                    {tmpl.is_builtin && (
                      <span className="px-1.5 py-0.5 rounded text-[9px] bg-blue-500/20 text-blue-400">内置</span>
                    )}
                    <span className="px-1.5 py-0.5 rounded text-[9px] bg-slate-700 text-slate-400">
                      {TARGET_TYPE_LABELS[tmpl.target_type] || tmpl.target_type}
                    </span>
                    {tmpl.brand && <span className="text-[10px] text-slate-500">{tmpl.brand}</span>}
                    {tmpl.version && <span className="px-1.5 py-0.5 rounded text-[9px] bg-amber-500/20 text-amber-400">v{tmpl.version}</span>}
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{tmpl.description || `${tmpl.items?.length || 0} 个巡检项`}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-400">{tmpl.items?.length || 0} 项</span>
                  {expandedId === tmpl.id ? <ChevronDown size={16} className="text-slate-400" /> : <ChevronRight size={16} className="text-slate-400" />}
                </div>
              </div>

              {expandedId === tmpl.id && (
                <div className="border-t border-slate-700 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-xs font-semibold text-slate-300">巡检项列表</h3>
                    <div className="flex items-center gap-1">
                      <button onClick={() => setEditingTemplate(tmpl)} className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-cyan-400 transition-colors" title="编辑模板">
                        <Edit3 size={14} />
                      </button>
                      <button onClick={() => handleDuplicate(tmpl)} className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-blue-400 transition-colors" title="复制模板">
                        <Copy size={14} />
                      </button>
                      {!tmpl.is_builtin && (
                        <button onClick={() => handleDelete(tmpl.id)} className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-red-400 transition-colors" title="删除">
                          <Trash2 size={14} />
                        </button>
                      )}
                    </div>
                  </div>
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left py-2 px-2 text-slate-500 font-medium">序号</th>
                        <th className="text-left py-2 px-2 text-slate-500 font-medium">名称</th>
                        <th className="text-left py-2 px-2 text-slate-500 font-medium">分类</th>
                        <th className="text-left py-2 px-2 text-slate-500 font-medium">命令/查询</th>
                        <th className="text-left py-2 px-2 text-slate-500 font-medium">类型</th>
                        <th className="text-left py-2 px-2 text-slate-500 font-medium">只读</th>
                        <th className="text-left py-2 px-2 text-slate-500 font-medium">权重</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tmpl.items?.map((item, idx) => (
                        <tr key={item.id || idx} className="border-b border-slate-700/30 hover:bg-slate-700/20">
                          <td className="py-2 px-2 text-slate-500">{item.order || idx + 1}</td>
                          <td className="py-2 px-2 text-slate-200">{item.name}</td>
                          <td className="py-2 px-2"><span className="px-1.5 py-0.5 rounded bg-slate-700 text-slate-400">{item.category}</span></td>
                          <td className="py-2 px-2 font-mono text-slate-400 max-w-xs truncate" title={item.command}>{item.command}</td>
                          <td className="py-2 px-2 text-slate-400">{item.command_type}</td>
                          <td className="py-2 px-2">
                            {item.is_read_only ? (
                              <span className="flex items-center gap-1 text-green-400"><Lock size={10} /> 是</span>
                            ) : (
                              <span className="flex items-center gap-1 text-amber-400"><AlertTriangle size={10} /> 否</span>
                            )}
                            {item.warning_text && !item.is_read_only && (
                              <p className="text-[9px] text-amber-500 mt-0.5">{item.warning_text}</p>
                            )}
                          </td>
                          <td className="py-2 px-2 text-slate-400">{item.weight}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Add/Edit Template Modal */}
      {(showAdd || editingTemplate) && (
        <TemplateFormModal
          template={editingTemplate}
          onClose={() => { setShowAdd(false); setEditingTemplate(null); }}
          onSaved={() => { setShowAdd(false); setEditingTemplate(null); loadTemplates(); }}
        />
      )}
    </div>
  );
}

function TemplateFormModal({ template, onClose, onSaved }: { template: InspectionTemplate | null; onClose: () => void; onSaved: () => void }) {
  const isEdit = !!template;
  const [form, setForm] = useState({
    name: template?.name || '',
    target_type: template?.target_type || 'linux' as TargetType,
    brand: template?.brand || '',
    version: template?.version || '',
    description: template?.description || '',
    items: template?.items || [] as InspectionItem[],
  });
  const [saving, setSaving] = useState(false);

  const addItem = () => {
    setForm(prev => ({
      ...prev,
      items: [...prev.items, {
        id: `item_${Date.now()}`,
        name: '', category: '基础信息', command: '', command_type: 'shell',
        is_read_only: true, parser: 'regex', threshold: null, weight: 1,
        order: prev.items.length + 1,
      }],
    }));
  };

  const updateItem = (idx: number, field: string, value: unknown) => {
    setForm(prev => {
      const items = [...prev.items];
      items[idx] = { ...items[idx], [field]: value };
      return { ...prev, items };
    });
  };

  const removeItem = (idx: number) => {
    setForm(prev => ({ ...prev, items: prev.items.filter((_, i) => i !== idx) }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (isEdit && template) {
        await api.updateTemplate(template.id, form);
      } else {
        await api.createTemplate(form);
      }
      onSaved();
    } catch (err) {
      console.error(err);
      alert('保存失败');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-slate-800 border border-slate-700 rounded-lg w-full max-w-3xl max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-100">{isEdit ? '编辑模板' : '新建巡检模板'}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">模板名称 *</label>
              <input required value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">目标类型 *</label>
              <select value={form.target_type} onChange={e => setForm(p => ({ ...p, target_type: e.target.value as TargetType }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500">
                {TARGET_TYPES.map(t => <option key={t} value={t}>{TARGET_TYPE_LABELS[t]}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">品牌标记</label>
              <input value={form.brand} onChange={e => setForm(p => ({ ...p, brand: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="不同品牌命令可能有差异" />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">版本标记</label>
              <input value={form.version} onChange={e => setForm(p => ({ ...p, version: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="如: 11g/12c/19c" />
            </div>
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">描述</label>
            <textarea value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} rows={2} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
          </div>

          {/* Items */}
          <div className="border-t border-slate-700 pt-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-slate-300">巡检项 ({form.items.length})</h3>
              <button type="button" onClick={addItem} className="px-3 py-1.5 text-xs bg-slate-700 text-slate-300 rounded hover:bg-slate-600 transition-colors flex items-center gap-1">
                <Plus size={12} /> 添加巡检项
              </button>
            </div>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {form.items.map((item, idx) => (
                <div key={item.id || idx} className="p-3 bg-slate-700/50 rounded-lg space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-slate-400">#{idx + 1}</span>
                    <button type="button" onClick={() => removeItem(idx)} className="text-slate-500 hover:text-red-400"><Trash2 size={12} /></button>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <input value={item.name} onChange={e => updateItem(idx, 'name', e.target.value)} placeholder="名称" className="px-2 py-1.5 bg-slate-700 border border-slate-600 rounded text-xs text-slate-200 focus:outline-none focus:border-cyan-500" />
                    <input value={item.category} onChange={e => updateItem(idx, 'category', e.target.value)} placeholder="分类" className="px-2 py-1.5 bg-slate-700 border border-slate-600 rounded text-xs text-slate-200 focus:outline-none focus:border-cyan-500" />
                    <select value={item.command_type} onChange={e => updateItem(idx, 'command_type', e.target.value)} className="px-2 py-1.5 bg-slate-700 border border-slate-600 rounded text-xs text-slate-200 focus:outline-none focus:border-cyan-500">
                      <option value="shell">Shell</option>
                      <option value="sql">SQL</option>
                      <option value="snmp">SNMP OID</option>
                      <option value="http">HTTP API</option>
                      <option value="ps1">PowerShell</option>
                    </select>
                  </div>
                  <textarea value={item.command} onChange={e => updateItem(idx, 'command', e.target.value)} placeholder="命令/查询语句" rows={2} className="w-full px-2 py-1.5 bg-slate-700 border border-slate-600 rounded text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500" />
                  <div className="flex items-center gap-3">
                    <label className="flex items-center gap-1 text-xs text-slate-400">
                      <input type="checkbox" checked={item.is_read_only} onChange={e => updateItem(idx, 'is_read_only', e.target.checked)} className="rounded" />
                      <Lock size={10} /> 只读命令
                    </label>
                    {!item.is_read_only && (
                      <input value={item.warning_text || ''} onChange={e => updateItem(idx, 'warning_text', e.target.value)} placeholder="非只读命令警告说明" className="flex-1 px-2 py-1 bg-amber-900/20 border border-amber-700/30 rounded text-xs text-amber-300 placeholder-amber-600 focus:outline-none" />
                    )}
                    <input type="number" value={item.weight} onChange={e => updateItem(idx, 'weight', Number(e.target.value))} placeholder="权重" className="w-16 px-2 py-1 bg-slate-700 border border-slate-600 rounded text-xs text-slate-200 focus:outline-none" min={1} max={10} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm bg-slate-700 text-slate-300 rounded-md hover:bg-slate-600 transition-colors">取消</button>
            <button type="submit" disabled={saving} className="px-4 py-2 text-sm bg-cyan-600 text-white rounded-md hover:bg-cyan-500 transition-colors disabled:opacity-50">
              {saving ? '保存中...' : '保存'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  BookOpen, Search, Filter, ExternalLink, ChevronDown,
  ChevronRight, AlertTriangle, Lightbulb, Bug, Shield,
} from 'lucide-react';
import { api, TARGET_TYPE_LABELS, STATUS_BG } from '@/lib/api';
import type { KnowledgeEntry, TargetType } from '@/lib/api';

const CATEGORIES = ['操作系统', '数据库', '网络设备', '存储设备', 'SAN交换机', 'BMC', '安全', '性能', '高可用'];

export default function KnowledgePage() {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const loadEntries = useCallback(() => {
    setLoading(true);
    api.getKnowledge()
      .then(data => setEntries(data.entries || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadEntries(); }, [loadEntries]);

  const filtered = entries.filter(e => {
    const matchSearch = !search || e.title.toLowerCase().includes(search.toLowerCase()) || e.symptom?.toLowerCase().includes(search.toLowerCase());
    const matchCategory = filterCategory === 'all' || e.category === filterCategory;
    return matchSearch && matchCategory;
  });

  const severityIcon = (severity: string) => {
    if (severity === 'critical') return <AlertTriangle size={14} className="text-red-400" />;
    if (severity === 'warning') return <AlertTriangle size={14} className="text-amber-400" />;
    return <Lightbulb size={14} className="text-blue-400" />;
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <BookOpen size={20} className="text-cyan-400" /> 巡检知识库
          </h1>
          <p className="text-sm text-slate-400 mt-1">常见问题解析、排查方法与最佳实践</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 max-w-xs">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="搜索问题、症状..." className="w-full pl-9 pr-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500" />
        </div>
        <div className="flex items-center gap-1 flex-wrap">
          <button onClick={() => setFilterCategory('all')} className={`px-3 py-1.5 text-xs rounded-md transition-colors ${filterCategory === 'all' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400 hover:text-slate-200'}`}>全部</button>
          {CATEGORIES.map(c => (
            <button key={c} onClick={() => setFilterCategory(c)} className={`px-3 py-1.5 text-xs rounded-md transition-colors ${filterCategory === c ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-400 hover:text-slate-200'}`}>{c}</button>
          ))}
        </div>
      </div>

      {/* Knowledge Cards */}
      <div className="space-y-3">
        {loading ? (
          <div className="text-center py-12 text-slate-500">加载中...</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            <BookOpen size={32} className="mx-auto mb-2 text-slate-600" />
            <p>暂无匹配的知识条目</p>
          </div>
        ) : (
          filtered.map(entry => (
            <div key={entry.id} className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
              <div
                className="flex items-center gap-3 p-4 cursor-pointer hover:bg-slate-700/30 transition-colors"
                onClick={() => setExpandedId(expandedId === entry.id ? null : entry.id)}
              >
                {severityIcon(entry.severity)}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-200 font-medium text-sm">{entry.title}</span>
                    <span className="px-1.5 py-0.5 rounded text-[9px] bg-slate-700 text-slate-400">{entry.category}</span>
                    {entry.target_type && <span className="px-1.5 py-0.5 rounded text-[9px] bg-blue-500/20 text-blue-400">{TARGET_TYPE_LABELS[entry.target_type as TargetType] || entry.target_type}</span>}
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-medium ${STATUS_BG[entry.severity] || 'bg-slate-700 text-slate-400'}`}>{entry.severity}</span>
                  </div>
                  {entry.symptom && <p className="text-xs text-slate-500 mt-0.5 truncate">{entry.symptom}</p>}
                </div>
                {expandedId === entry.id ? <ChevronDown size={16} className="text-slate-400" /> : <ChevronRight size={16} className="text-slate-400" />}
              </div>

              {expandedId === entry.id && (
                <div className="border-t border-slate-700 p-4 space-y-3">
                  {entry.symptom && (
                    <div>
                      <h4 className="text-xs font-medium text-amber-400 mb-1 flex items-center gap-1"><Bug size={12} /> 症状表现</h4>
                      <p className="text-sm text-slate-300 whitespace-pre-wrap">{entry.symptom}</p>
                    </div>
                  )}
                  {entry.cause && (
                    <div>
                      <h4 className="text-xs font-medium text-red-400 mb-1 flex items-center gap-1"><AlertTriangle size={12} /> 可能原因</h4>
                      <p className="text-sm text-slate-300 whitespace-pre-wrap">{entry.cause}</p>
                    </div>
                  )}
                  {entry.solution && (
                    <div>
                      <h4 className="text-xs font-medium text-green-400 mb-1 flex items-center gap-1"><Lightbulb size={12} /> 解决方案</h4>
                      <p className="text-sm text-slate-300 whitespace-pre-wrap">{entry.solution}</p>
                    </div>
                  )}
                  {entry.reference && (
                    <div className="pt-2 border-t border-slate-700/50">
                      <a href={entry.reference} target="_blank" rel="noopener noreferrer" className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
                        <ExternalLink size={10} /> 参考文档
                      </a>
                    </div>
                  )}
                  {entry.tags && entry.tags.length > 0 && (
                    <div className="flex items-center gap-1 flex-wrap">
                      {entry.tags.map(tag => (
                        <span key={tag} className="px-1.5 py-0.5 rounded text-[9px] bg-slate-700 text-slate-400">{tag}</span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

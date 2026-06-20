'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  FileBarChart, Download, Eye, CheckCircle2, XCircle,
  AlertTriangle, Search, BarChart3, TrendingUp,
  ArrowUpDown,
} from 'lucide-react';
import { api, STATUS_BG, formatTime, getHealthColor } from '@/lib/api';
import type { InspectionReport, IssueItem, ReportFormat } from '@/lib/api';

export default function ReportsPage() {
  const [reports, setReports] = useState<InspectionReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedReport, setSelectedReport] = useState<InspectionReport | null>(null);

  const loadReports = useCallback(() => {
    setLoading(true);
    api.getReports()
      .then(data => setReports(data.reports || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadReports(); }, [loadReports]);

  const filtered = reports.filter(r =>
    !search || r.task_name?.toLowerCase().includes(search.toLowerCase())
  );

  const handleDownload = async (report: InspectionReport, format: ReportFormat) => {
    try {
      if (format === 'html') {
        // HTML下载使用原有方式
        const newReport = await api.generateReport(report.task_id, format);
        if (newReport.download_url) {
          window.open(newReport.download_url, '_blank');
        }
      } else {
        // DOCX/PDF 使用新的后端API生成
        const taskId = report.task_id || 'task-unknown';
        const res = await fetch('/api/v1/reports/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            task_name: report.task_name || '巡检报告',
            task_id: taskId,
            format: format,
            targets: [],
            results: report.results || [],
            config: {
              title: `${report.task_name || '巡检报告'}`,
              platform_name: 'Acdante ITOps Inspection Platform',
            }
          }),
        });
        const data = await res.json();
        if (data.paths && data.paths[format]) {
          // 触发下载
          window.open(`/api/v1/reports/download/${data.report_id}?format=${format}`, '_blank');
        } else {
          alert(`${format.toUpperCase()} 报告生成中，请稍后下载。报告ID: ${data.report_id}`);
        }
      }
    } catch (err) {
      console.error(err);
      alert('下载失败，请确保Python后端服务正在运行');
    }
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileBarChart size={20} className="text-cyan-400" /> 巡检报告
          </h1>
          <p className="text-sm text-slate-400 mt-1">查看、预览和下载巡检报告</p>
        </div>
      </div>

      <div className="relative max-w-xs">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="搜索报告..." className="w-full pl-9 pr-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Report List */}
        <div className="lg:col-span-1 space-y-2">
          {loading ? (
            <div className="text-center py-12 text-slate-500">加载中...</div>
          ) : filtered.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <FileBarChart size={32} className="mx-auto mb-2 text-slate-600" />
              <p>暂无巡检报告</p>
            </div>
          ) : (
            filtered.map(report => (
              <div
                key={report.id}
                onClick={() => setSelectedReport(report)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedReport?.id === report.id ? 'bg-cyan-500/10 border border-cyan-500/30' : 'bg-slate-800/50 border border-slate-700 hover:border-slate-600'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-200 font-medium truncate">{report.task_name || `报告 ${report.id.slice(0, 8)}`}</span>
                  <span className={`font-bold text-sm ${getHealthColor(report.health_score)}`}>{report.health_score}%</span>
                </div>
                <div className="flex items-center gap-3 mt-1 text-[10px] text-slate-500">
                  <span>{formatTime(report.generated_at)}</span>
                  <span className="text-green-400">{report.ok_count} OK</span>
                  {report.warning_count > 0 && <span className="text-amber-400">{report.warning_count} WARN</span>}
                  {report.critical_count > 0 && <span className="text-red-400">{report.critical_count} CRIT</span>}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Report Detail */}
        <div className="lg:col-span-2">
          {selectedReport ? (
            <ReportDetail report={selectedReport} onDownload={handleDownload} />
          ) : (
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-12 text-center text-slate-500">
              <Eye size={32} className="mx-auto mb-2" />
              <p>选择左侧报告查看详情</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ReportDetail({ report, onDownload }: { report: InspectionReport; onDownload: (r: InspectionReport, f: ReportFormat) => void }) {
  const [activeTab, setActiveTab] = useState<'summary' | 'issues' | 'detail'>('summary');

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-100">{report.task_name || `报告 ${report.id.slice(0, 8)}`}</h2>
            <p className="text-xs text-slate-500 mt-0.5">生成于 {formatTime(report.generated_at)}</p>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => onDownload(report, 'html')} className="px-3 py-1.5 text-xs bg-slate-700 text-slate-300 rounded hover:bg-slate-600 transition-colors flex items-center gap-1">
              <Download size={12} /> HTML
            </button>
            <button onClick={() => onDownload(report, 'docx')} className="px-3 py-1.5 text-xs bg-slate-700 text-slate-300 rounded hover:bg-slate-600 transition-colors flex items-center gap-1">
              <Download size={12} /> DOCX
            </button>
            <button onClick={() => onDownload(report, 'pdf')} className="px-3 py-1.5 text-xs bg-slate-700 text-slate-300 rounded hover:bg-slate-600 transition-colors flex items-center gap-1">
              <Download size={12} /> PDF
            </button>
          </div>
        </div>

        {/* Health Score Bar */}
        <div className="mt-4 flex items-center gap-4">
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-400">健康度</span>
              <span className={`text-sm font-bold ${getHealthColor(report.health_score)}`}>{report.health_score}%</span>
            </div>
            <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${report.health_score >= 90 ? 'bg-green-500' : report.health_score >= 70 ? 'bg-amber-500' : 'bg-red-500'}`}
                style={{ width: `${report.health_score}%` }}
              />
            </div>
          </div>
          <div className="flex items-center gap-4 text-center">
            <div>
              <p className="text-lg font-bold text-green-400">{report.ok_count}</p>
              <p className="text-[10px] text-slate-500">正常</p>
            </div>
            <div>
              <p className="text-lg font-bold text-amber-400">{report.warning_count}</p>
              <p className="text-[10px] text-slate-500">告警</p>
            </div>
            <div>
              <p className="text-lg font-bold text-red-400">{report.critical_count}</p>
              <p className="text-[10px] text-slate-500">严重</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-700">
        {(['summary', 'issues', 'detail'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 text-sm transition-colors ${
              activeTab === tab ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab === 'summary' ? '概览' : tab === 'issues' ? `问题 (${report.critical_count + report.warning_count})` : '详情'}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-4">
        {activeTab === 'summary' && (
          <div className="space-y-4">
            <div className="p-4 bg-slate-700/30 rounded-lg">
              <h3 className="text-sm font-medium text-slate-200 mb-2">巡检摘要</h3>
              <p className="text-sm text-slate-400">{report.summary || '暂无摘要信息'}</p>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="p-3 bg-green-500/10 rounded-lg text-center">
                <CheckCircle2 size={24} className="mx-auto text-green-400 mb-1" />
                <p className="text-2xl font-bold text-green-400">{report.ok_count}</p>
                <p className="text-xs text-slate-500">正常项目</p>
              </div>
              <div className="p-3 bg-amber-500/10 rounded-lg text-center">
                <AlertTriangle size={24} className="mx-auto text-amber-400 mb-1" />
                <p className="text-2xl font-bold text-amber-400">{report.warning_count}</p>
                <p className="text-xs text-slate-500">告警项目</p>
              </div>
              <div className="p-3 bg-red-500/10 rounded-lg text-center">
                <XCircle size={24} className="mx-auto text-red-400 mb-1" />
                <p className="text-2xl font-bold text-red-400">{report.critical_count}</p>
                <p className="text-xs text-slate-500">严重问题</p>
              </div>
            </div>
            <div className="p-4 bg-slate-700/30 rounded-lg">
              <h3 className="text-sm font-medium text-slate-200 mb-2">巡检统计</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-400 w-20">总检查项</span>
                  <div className="flex-1 h-3 bg-slate-700 rounded-full overflow-hidden flex">
                    {report.total_items > 0 && (
                      <>
                        <div className="h-full bg-green-500" style={{ width: `${(report.ok_count / report.total_items) * 100}%` }} />
                        <div className="h-full bg-amber-500" style={{ width: `${(report.warning_count / report.total_items) * 100}%` }} />
                        <div className="h-full bg-red-500" style={{ width: `${(report.critical_count / report.total_items) * 100}%` }} />
                      </>
                    )}
                  </div>
                  <span className="text-xs text-slate-300">{report.total_items}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'issues' && (
          <div className="space-y-2">
            {(!report.issues || report.issues.length === 0) ? (
              <div className="text-center py-8 text-slate-500">
                <CheckCircle2 size={24} className="mx-auto mb-2 text-green-400" />
                <p>未发现问题</p>
              </div>
            ) : (
              report.issues.map((issue, idx) => (
                <div key={idx} className={`p-3 rounded-lg border ${issue.status === 'critical' ? 'bg-red-500/5 border-red-500/20' : 'bg-amber-500/5 border-amber-500/20'}`}>
                  <div className="flex items-center gap-2">
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-medium ${STATUS_BG[issue.status]}`}>
                      {issue.status.toUpperCase()}
                    </span>
                    <span className="text-sm text-slate-200 font-medium">{issue.item_name}</span>
                    <span className="text-xs text-slate-500 ml-auto">{issue.target_name}</span>
                  </div>
                  <div className="mt-2 text-xs text-slate-400 space-y-1">
                    <p>当前值: <span className="text-slate-200 font-mono">{issue.value}</span> | 阈值: <span className="text-slate-200 font-mono">{issue.threshold}</span></p>
                    {issue.suggestion && <p className="text-cyan-400/80">建议: {issue.suggestion}</p>}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'detail' && (
          <div className="space-y-2">
            {(!report.results || report.results.length === 0) ? (
              <div className="text-center py-8 text-slate-500">
                <BarChart3 size={24} className="mx-auto mb-2" />
                <p>暂无详细结果</p>
              </div>
            ) : (
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-2 px-2 text-slate-500 font-medium">对象</th>
                    <th className="text-left py-2 px-2 text-slate-500 font-medium">检查项</th>
                    <th className="text-left py-2 px-2 text-slate-500 font-medium">分类</th>
                    <th className="text-left py-2 px-2 text-slate-500 font-medium">原始值</th>
                    <th className="text-left py-2 px-2 text-slate-500 font-medium">状态</th>
                    <th className="text-left py-2 px-2 text-slate-500 font-medium">建议</th>
                  </tr>
                </thead>
                <tbody>
                  {report.results.map((r, idx) => (
                    <tr key={idx} className="border-b border-slate-700/30 hover:bg-slate-700/20">
                      <td className="py-2 px-2 text-slate-300">{r.target_name}</td>
                      <td className="py-2 px-2 text-slate-200">{r.item_name}</td>
                      <td className="py-2 px-2"><span className="px-1.5 py-0.5 rounded bg-slate-700 text-slate-400">{r.category}</span></td>
                      <td className="py-2 px-2 font-mono text-slate-400 max-w-xs truncate" title={String(r.raw_value)}>{String(r.raw_value).slice(0, 60)}</td>
                      <td className="py-2 px-2"><span className={`px-1.5 py-0.5 rounded text-[9px] font-medium ${STATUS_BG[r.status]}`}>{r.status.toUpperCase()}</span></td>
                      <td className="py-2 px-2 text-slate-400 max-w-xs truncate">{r.suggestion || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

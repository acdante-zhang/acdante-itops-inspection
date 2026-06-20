'use client';

import { useEffect, useState } from 'react';
import {
  Monitor, FileText, ListChecks, FileBarChart,
  AlertTriangle, CheckCircle2, XCircle, Clock,
  Server, Activity, TrendingUp, Shield,
} from 'lucide-react';
import { api, TARGET_TYPE_LABELS, STATUS_BG, formatTime } from '@/lib/api';
import type { DashboardStats } from '@/lib/api';
import Link from 'next/link';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.dashboard()
      .then(data => setStats(data))
      .catch(err => console.error('Failed to load dashboard:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-28 bg-slate-800/50 rounded-lg animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-64 bg-slate-800/50 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (!stats) return <div className="p-6 text-slate-400">加载失败，请刷新页面</div>;

  const statCards = [
    { label: '巡检对象', value: stats.total_targets, icon: <Monitor size={20} />, sub: `${stats.active_targets} 在线`, color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
    { label: '巡检模板', value: stats.total_templates, icon: <FileText size={20} />, sub: `${stats.total_tasks} 任务`, color: 'text-blue-400', bg: 'bg-blue-500/10' },
    { label: '严重问题', value: stats.critical_issues, icon: <XCircle size={20} />, sub: `${stats.warning_issues} 告警`, color: 'text-red-400', bg: 'bg-red-500/10' },
    { label: '今日报告', value: stats.today_reports, icon: <FileBarChart size={20} />, sub: `${stats.running_tasks} 执行中`, color: 'text-amber-400', bg: 'bg-amber-500/10' },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Shield size={24} className="text-cyan-400" />
            Acdante ITOps Inspection Platform
          </h1>
          <p className="text-sm text-slate-400 mt-1">多协议、多对象自动化巡检系统</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500">最后刷新: {new Date().toLocaleTimeString('zh-CN')}</span>
          <Link href="/tasks" className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-md text-sm font-medium transition-colors">
            创建巡检任务
          </Link>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map(card => (
          <div key={card.label} className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition-colors">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">{card.label}</span>
              <div className={`p-2 rounded-md ${card.bg}`}>
                <span className={card.color}>{card.icon}</span>
              </div>
            </div>
            <div className="mt-2">
              <span className="text-3xl font-bold text-slate-100">{card.value}</span>
            </div>
            <div className="mt-1 text-xs text-slate-500">{card.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Targets by Type */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <Server size={16} className="text-cyan-400" /> 巡检对象分布
          </h2>
          <div className="space-y-2">
            {stats.targets_by_type.map(item => {
              const maxCount = Math.max(...stats.targets_by_type.map(t => t.count), 1);
              return (
                <div key={item.type} className="flex items-center gap-3">
                  <span className="text-xs text-slate-400 w-20 text-right">{TARGET_TYPE_LABELS[item.type as keyof typeof TARGET_TYPE_LABELS] || item.type}</span>
                  <div className="flex-1 h-5 bg-slate-700/50 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-cyan-500/60 rounded-full transition-all"
                      style={{ width: `${(item.count / maxCount) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-slate-300 w-8 text-right">{item.count}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <AlertTriangle size={16} className="text-amber-400" /> 最近告警
          </h2>
          {stats.recent_alerts.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <CheckCircle2 size={32} className="mx-auto mb-2 text-green-400" />
              <p>暂无告警</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {stats.recent_alerts.map(alert => (
                <div key={alert.id} className="flex items-start gap-3 p-2 rounded bg-slate-700/30">
                  <span className={`mt-0.5 px-1.5 py-0.5 rounded text-[10px] font-medium ${STATUS_BG[alert.severity] || 'bg-slate-700 text-slate-400'}`}>
                    {alert.severity.toUpperCase()}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-slate-200 truncate">{alert.message}</p>
                    <p className="text-[10px] text-slate-500">{alert.target} · {formatTime(alert.time)}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Recent Tasks */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <Activity size={16} className="text-cyan-400" /> 近期任务
          </h2>
          {stats.recent_tasks.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              <ListChecks size={32} className="mx-auto mb-2" />
              <p>暂无巡检任务</p>
            </div>
          ) : (
            <div className="space-y-2">
              {stats.recent_tasks.map(task => (
                <div key={task.id} className="flex items-center gap-3 p-2 rounded bg-slate-700/30">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${STATUS_BG[task.status] || 'bg-slate-700 text-slate-400'}`}>
                    {task.status.toUpperCase()}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-slate-200 truncate">{task.name}</p>
                    <p className="text-[10px] text-slate-500">{formatTime(task.started_at)}</p>
                  </div>
                  {task.status === 'running' && (
                    <div className="w-16 bg-slate-700 rounded-full h-1.5">
                      <div className="bg-cyan-400 h-1.5 rounded-full transition-all" style={{ width: `${task.progress}%` }} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Health Trend */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <TrendingUp size={16} className="text-green-400" /> 健康趋势（近7天）
          </h2>
          <div className="flex items-end gap-1 h-32">
            {stats.health_trend.map((item, idx) => {
              const maxH = 100;
              return (
                <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                  <div className="w-full flex flex-col items-center gap-0.5" style={{ height: '100px' }}>
                    <div className="flex-1 w-full flex flex-col justify-end gap-px">
                      <div
                        className="w-full bg-red-500/40 rounded-sm"
                        style={{ height: `${(item.critical / maxH) * 60}px` }}
                        title={`严重: ${item.critical}`}
                      />
                      <div
                        className="w-full bg-amber-500/40 rounded-sm"
                        style={{ height: `${(item.warning / maxH) * 30}px` }}
                        title={`告警: ${item.warning}`}
                      />
                    </div>
                  </div>
                  <span className="text-[9px] text-slate-500">{item.date.slice(5)}</span>
                </div>
              );
            })}
          </div>
          <div className="flex items-center gap-4 mt-3 text-[10px] text-slate-500">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-red-500/60" /> 严重</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-amber-500/60" /> 告警</span>
          </div>
        </div>
      </div>
    </div>
  );
}

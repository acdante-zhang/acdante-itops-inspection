'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  ListChecks, Plus, Play, Clock, CheckCircle2, XCircle,
  Loader2, Search, Trash2, Calendar, Mail, Webhook,
} from 'lucide-react';
import { api, TARGET_TYPE_LABELS, STATUS_BG, SCHEDULE_LABELS, formatTime } from '@/lib/api';
import type { InspectionTask, InspectionTemplate, InspectionTarget, ScheduleType } from '@/lib/api';

export default function TasksPage() {
  const [tasks, setTasks] = useState<InspectionTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);

  const loadTasks = useCallback(() => {
    setLoading(true);
    api.getTasks()
      .then(data => setTasks(data.tasks || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadTasks(); }, [loadTasks]);

  const handleRun = async (id: string) => {
    try {
      await api.runTask(id);
      loadTasks();
    } catch (err) {
      console.error(err);
      alert('执行失败');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('确定删除该任务？')) return;
    try {
      await api.deleteTask(id);
      setTasks(prev => prev.filter(t => t.id !== id));
    } catch (err) { console.error(err); }
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <ListChecks size={20} className="text-cyan-400" /> 巡检任务管理
          </h1>
          <p className="text-sm text-slate-400 mt-1">创建调度任务、配置通知策略</p>
        </div>
        <button onClick={() => setShowAdd(true)} className="px-4 py-2 text-sm bg-cyan-600 hover:bg-cyan-500 text-white rounded-md flex items-center gap-1.5 transition-colors">
          <Plus size={14} /> 新建任务
        </button>
      </div>

      {/* Task List */}
      <div className="space-y-3">
        {loading ? (
          <div className="text-center py-12 text-slate-500">加载中...</div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            <ListChecks size={32} className="mx-auto mb-2 text-slate-600" />
            <p>暂无巡检任务</p>
            <p className="text-xs mt-1">点击"新建任务"开始创建</p>
          </div>
        ) : (
          tasks.map(task => (
            <div key={task.id} className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition-colors">
              <div className="flex items-center gap-4">
                <div className={`p-2 rounded-md ${task.status === 'running' ? 'bg-cyan-500/10' : task.status === 'completed' ? 'bg-green-500/10' : task.status === 'failed' ? 'bg-red-500/10' : 'bg-slate-700/50'}`}>
                  {task.status === 'running' ? <Loader2 size={18} className="text-cyan-400 animate-spin" /> :
                   task.status === 'completed' ? <CheckCircle2 size={18} className="text-green-400" /> :
                   task.status === 'failed' ? <XCircle size={18} className="text-red-400" /> :
                   <Clock size={18} className="text-slate-400" />}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-slate-200 font-medium">{task.name}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${STATUS_BG[task.status] || 'bg-slate-700 text-slate-400'}`}>
                      {task.status === 'running' ? '执行中' : task.status === 'completed' ? '已完成' : task.status === 'failed' ? '失败' : '待执行'}
                    </span>
                    <span className="px-1.5 py-0.5 rounded text-[9px] bg-blue-500/20 text-blue-400">
                      {SCHEDULE_LABELS[task.schedule_type] || task.schedule_type}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 mt-1 text-xs text-slate-500">
                    <span>上次执行: {formatTime(task.last_run_at)}</span>
                    {task.next_run_at && <span>下次执行: {formatTime(task.next_run_at)}</span>}
                    <span>{task.target_ids?.length || 0} 个对象</span>
                    {task.notify_email?.length > 0 && (
                      <span className="flex items-center gap-1"><Mail size={10} /> {task.notify_email.length} 通知</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={() => handleRun(task.id)} disabled={task.status === 'running'} className="px-3 py-1.5 text-xs bg-cyan-600 text-white rounded hover:bg-cyan-500 transition-colors disabled:opacity-50 flex items-center gap-1">
                    <Play size={12} /> 执行
                  </button>
                  <button onClick={() => handleDelete(task.id)} className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-red-400 transition-colors">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {showAdd && <AddTaskModal onClose={() => setShowAdd(false)} onCreated={() => { setShowAdd(false); loadTasks(); }} />}
    </div>
  );
}

function AddTaskModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [templates, setTemplates] = useState<InspectionTemplate[]>([]);
  const [targets, setTargets] = useState<InspectionTarget[]>([]);
  const [form, setForm] = useState({
    name: '',
    template_id: '',
    target_ids: [] as number[],
    schedule_type: 'once' as ScheduleType,
    notify_email: '',
    notify_webhook: '',
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getTemplates().then(d => setTemplates(d.templates || [])).catch(console.error);
    api.getTargets().then(d => setTargets(d.targets || [])).catch(console.error);
  }, []);

  const selectedTemplate = templates.find(t => t.id === form.template_id);
  const filteredTargets = selectedTemplate
    ? targets.filter(t => t.type === selectedTemplate.target_type)
    : targets;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.createTask({
        ...form,
        notify_email: form.notify_email ? form.notify_email.split(',').map(e => e.trim()) : [],
        notify_webhook: form.notify_webhook || undefined,
      });
      onCreated();
    } catch (err) {
      console.error(err);
      alert('创建失败');
    } finally {
      setSaving(false);
    }
  };

  const toggleTarget = (id: number) => {
    setForm(prev => ({
      ...prev,
      target_ids: prev.target_ids.includes(id)
        ? prev.target_ids.filter(i => i !== id)
        : [...prev.target_ids, id],
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-slate-800 border border-slate-700 rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="p-4 border-b border-slate-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-100">新建巡检任务</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">✕</button>
        </div>
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div>
            <label className="block text-xs text-slate-400 mb-1">任务名称 *</label>
            <input required value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="如: 每日生产环境巡检" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">巡检模板 *</label>
              <select value={form.template_id} onChange={e => setForm(p => ({ ...p, template_id: e.target.value, target_ids: [] }))} required className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500">
                <option value="">选择模板</option>
                {templates.map(t => <option key={t.id} value={t.id}>{t.name} ({TARGET_TYPE_LABELS[t.target_type]})</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">调度方式 *</label>
              <select value={form.schedule_type} onChange={e => setForm(p => ({ ...p, schedule_type: e.target.value as ScheduleType }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500">
                {Object.entries(SCHEDULE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-2">巡检对象 *</label>
            <div className="max-h-48 overflow-y-auto space-y-1 p-2 bg-slate-700/50 rounded-lg">
              {filteredTargets.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-4">暂无匹配的巡检对象</p>
              ) : (
                filteredTargets.map(target => (
                  <label key={target.id} className="flex items-center gap-2 p-2 rounded hover:bg-slate-600/50 cursor-pointer">
                    <input type="checkbox" checked={form.target_ids.includes(target.id)} onChange={() => toggleTarget(target.id)} className="rounded" />
                    <span className="text-xs text-slate-200">{target.name}</span>
                    <span className="text-[10px] text-slate-500 ml-auto">{target.connection_params?.host}</span>
                  </label>
                ))
              )}
            </div>
            {form.target_ids.length > 0 && <p className="text-[10px] text-cyan-400 mt-1">已选 {form.target_ids.length} 个对象</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1">通知邮箱（逗号分隔）</label>
              <input value={form.notify_email} onChange={e => setForm(p => ({ ...p, notify_email: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="admin@company.com" />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Webhook URL</label>
              <input value={form.notify_webhook} onChange={e => setForm(p => ({ ...p, notify_webhook: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="https://hooks.example.com/..." />
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm bg-slate-700 text-slate-300 rounded-md hover:bg-slate-600 transition-colors">取消</button>
            <button type="submit" disabled={saving || !form.template_id || form.target_ids.length === 0} className="px-4 py-2 text-sm bg-cyan-600 text-white rounded-md hover:bg-cyan-500 transition-colors disabled:opacity-50">
              {saving ? '创建中...' : '创建任务'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

'use client';

import { useState } from 'react';
import {
  Settings, Shield, Bell, Database, Key, Globe,
  Save, CheckCircle2, AlertTriangle, User,
} from 'lucide-react';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'general' | 'security' | 'notification' | 'system'>('general');
  const [saved, setSaved] = useState(false);

  const [general, setGeneral] = useState({
    platform_name: 'Acdante ITOps Inspection Platform',
    company_name: 'Acdante AI',
    logo_url: '',
    default_report_format: 'html',
    language: 'zh-CN',
    timezone: 'Asia/Shanghai',
  });

  const [security, setSecurity] = useState({
    credential_encryption: true,
    session_timeout: 30,
    max_login_attempts: 5,
    two_factor: false,
    ip_whitelist: '',
  });

  const [notification, setNotification] = useState({
    smtp_host: '',
    smtp_port: 465,
    smtp_user: '',
    smtp_password: '',
    smtp_ssl: true,
    default_recipients: '',
    webhook_url: '',
  });

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const tabs = [
    { key: 'general' as const, label: '通用设置', icon: <Globe size={16} /> },
    { key: 'security' as const, label: '安全设置', icon: <Shield size={16} /> },
    { key: 'notification' as const, label: '通知配置', icon: <Bell size={16} /> },
    { key: 'system' as const, label: '系统信息', icon: <Database size={16} /> },
  ];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Settings size={20} className="text-cyan-400" /> 系统设置
          </h1>
          <p className="text-sm text-slate-400 mt-1">平台配置、安全策略、通知设置</p>
        </div>
        <button onClick={handleSave} className="px-4 py-2 text-sm bg-cyan-600 hover:bg-cyan-500 text-white rounded-md flex items-center gap-1.5 transition-colors">
          <Save size={14} /> 保存设置
          {saved && <CheckCircle2 size={14} className="text-green-300" />}
        </button>
      </div>

      <div className="flex gap-4">
        {/* Tab Navigation */}
        <div className="w-48 space-y-1">
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors ${
                activeTab === tab.key ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="flex-1 bg-slate-800/50 border border-slate-700 rounded-lg p-6">
          {activeTab === 'general' && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-slate-100 mb-4">通用设置</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">平台名称</label>
                  <input value={general.platform_name} onChange={e => setGeneral(p => ({ ...p, platform_name: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">公司/品牌名称</label>
                  <input value={general.company_name} onChange={e => setGeneral(p => ({ ...p, company_name: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">默认报告格式</label>
                  <select value={general.default_report_format} onChange={e => setGeneral(p => ({ ...p, default_report_format: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500">
                    <option value="html">HTML</option>
                    <option value="docx">DOCX</option>
                    <option value="pdf">PDF</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">时区</label>
                  <select value={general.timezone} onChange={e => setGeneral(p => ({ ...p, timezone: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500">
                    <option value="Asia/Shanghai">Asia/Shanghai (UTC+8)</option>
                    <option value="UTC">UTC</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-slate-100 mb-4">安全设置</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                  <div>
                    <p className="text-sm text-slate-200">凭证加密存储</p>
                    <p className="text-xs text-slate-500">使用 AES-256 加密所有设备凭证</p>
                  </div>
                  <button onClick={() => setSecurity(p => ({ ...p, credential_encryption: !p.credential_encryption }))} className={`w-10 h-5 rounded-full transition-colors ${security.credential_encryption ? 'bg-cyan-500' : 'bg-slate-600'}`}>
                    <div className={`w-4 h-4 bg-white rounded-full transition-transform ${security.credential_encryption ? 'translate-x-5' : 'translate-x-0.5'}`} />
                  </button>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">会话超时(分钟)</label>
                    <input type="number" value={security.session_timeout} onChange={e => setSecurity(p => ({ ...p, session_timeout: Number(e.target.value) }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">最大登录尝试次数</label>
                    <input type="number" value={security.max_login_attempts} onChange={e => setSecurity(p => ({ ...p, max_login_attempts: Number(e.target.value) }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                  <div>
                    <p className="text-sm text-slate-200">双因素认证</p>
                    <p className="text-xs text-slate-500">启用 TOTP 二次验证</p>
                  </div>
                  <button onClick={() => setSecurity(p => ({ ...p, two_factor: !p.two_factor }))} className={`w-10 h-5 rounded-full transition-colors ${security.two_factor ? 'bg-cyan-500' : 'bg-slate-600'}`}>
                    <div className={`w-4 h-4 bg-white rounded-full transition-transform ${security.two_factor ? 'translate-x-5' : 'translate-x-0.5'}`} />
                  </button>
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">IP 白名单（逗号分隔，留空不限）</label>
                  <input value={security.ip_whitelist} onChange={e => setSecurity(p => ({ ...p, ip_whitelist: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="10.0.0.0/8, 192.168.1.0/24" />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notification' && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-slate-100 mb-4">通知配置</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">SMTP 服务器</label>
                  <input value={notification.smtp_host} onChange={e => setNotification(p => ({ ...p, smtp_host: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="smtp.example.com" />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">SMTP 端口</label>
                  <input type="number" value={notification.smtp_port} onChange={e => setNotification(p => ({ ...p, smtp_port: Number(e.target.value) }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">SMTP 用户名</label>
                  <input value={notification.smtp_user} onChange={e => setNotification(p => ({ ...p, smtp_user: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">SMTP 密码</label>
                  <input type="password" value={notification.smtp_password} onChange={e => setNotification(p => ({ ...p, smtp_password: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" />
                </div>
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">默认收件人（逗号分隔）</label>
                <input value={notification.default_recipients} onChange={e => setNotification(p => ({ ...p, default_recipients: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="admin@company.com" />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Webhook URL</label>
                <input value={notification.webhook_url} onChange={e => setNotification(p => ({ ...p, webhook_url: e.target.value }))} className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-sm text-slate-200 focus:outline-none focus:border-cyan-500" placeholder="https://hooks.example.com/..." />
              </div>
            </div>
          )}

          {activeTab === 'system' && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-slate-100 mb-4">系统信息</h2>
              <div className="space-y-2">
                {[
                  { label: '平台版本', value: 'v1.0.0' },
                  { label: '前端框架', value: 'Next.js 16 + React 19' },
                  { label: 'API 引擎', value: 'Go + Rust + Python' },
                  { label: '数据库', value: 'SQLite / PostgreSQL' },
                  { label: '任务队列', value: 'Asynq + Redis' },
                  { label: '报告引擎', value: 'python-docx + WeasyPrint + Jinja2' },
                  { label: '截图服务', value: 'Playwright + PaddleOCR' },
                  { label: '连接协议', value: 'SSH / SNMP / JDBC / ODBC / IPMI / Redfish' },
                ].map(item => (
                  <div key={item.label} className="flex items-center justify-between p-2 bg-slate-700/30 rounded">
                    <span className="text-xs text-slate-400">{item.label}</span>
                    <span className="text-xs text-slate-200 font-mono">{item.value}</span>
                  </div>
                ))}
              </div>
              <div className="p-4 bg-cyan-500/10 border border-cyan-500/20 rounded-lg mt-4">
                <h3 className="text-sm font-medium text-cyan-400 mb-2 flex items-center gap-1"><Key size={14} /> 技术架构</h3>
                <pre className="text-xs text-slate-300 whitespace-pre font-mono">{`
浏览器 → Next.js (5000) → Go API Gateway (8080)
                               ↓
                     Rust Data Engine (8081)
                               ↓
                     Python Driver → SSH/SNMP/JDBC → 目标设备
                               ↓
                     Report Engine → DOCX/HTML/PDF
                `}</pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

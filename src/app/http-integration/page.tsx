'use client';

import { useEffect, useState, useCallback, useMemo } from 'react';
import {
  Globe, Shield, Lock, Unlock, Key, Ticket, AlertTriangle,
  Search, Plus, Trash2, RefreshCw, XCircle,
  Clock, FileKey, Upload, Eye, EyeOff, ChevronDown,
  ChevronRight, Activity, Settings2,
  Wifi, FileText, Play, ShieldAlert, ShieldCheck,
  Terminal, Camera, Download, Maximize2, Image as ImageIcon,
} from 'lucide-react';

type TLSVersion = 'TLSv1.0' | 'TLSv1.1' | 'TLSv1.2' | 'TLSv1.3';
type AuthType = 'form' | 'basic' | 'token' | 'oauth2' | 'cookie' | 'none';
type CertStatus = 'valid' | 'expiring' | 'expired' | 'self_signed' | 'unknown';
type ConnStatus = 'connected' | 'disconnected' | 'testing' | 'error';

interface HTTPDevice {
  id: string; name: string; brand: string; model: string; base_url: string; port: number;
  use_https: boolean; auth_type: AuthType; username: string; password_enc: string;
  login_url: string; username_field?: string; password_field?: string; submit_selector?: string;
  tls_min_version: TLSVersion; tls_max_version: TLSVersion; verify_cert: boolean;
  accept_self_signed: boolean; custom_headers: Record<string, string>; cipher_suites: string[];
  timeout: number; status: ConnStatus; cert_status: CertStatus; cert_expiry: string | null;
  last_check: string | null; compat_mode: boolean; tags: string[]; created_at: string;
}

interface SSLCertificate {
  id: string; device_id: string; device_name: string; subject: string; issuer: string;
  serial: string; valid_from: string; valid_to: string; status: CertStatus;
  is_self_signed: boolean; key_size: number; signature_algorithm: string;
  san: string[]; imported: boolean; trusted: boolean;
}

interface HTTPInspectionItem {
  id: string; device_id: string; name: string; category: string; method: string;
  url_path: string; request_body: string; content_type: string;
  parser_type: 'json_path' | 'css_selector' | 'xpath' | 'regex' | 'raw' | 'screenshot';
  parser_expression: string;
  threshold: { operator: string; critical: number; warning: number; unit: string } | null;
  is_read_only: boolean; weight: number; order: number;
  screenshot_config: ScreenshotConfig | null;
}

interface ScreenshotConfig {
  navigate_type: 'url' | 'menu_click' | 'url_then_menu';
  target_url: string;
  menu_path: string[];
  wait_selector: string;
  wait_timeout: number;
  capture_area: 'full_page' | 'viewport' | 'element';
  capture_selector: string;
  word_template_key: string;
  word_section: string;
  word_position: number;
  image_width_mm: number;
}

interface Screenshot {
  id: string; device_id: string; device_name: string; item_id: string; item_name: string;
  url: string; captured_at: string; width: number; height: number;
  file_size: number; thumbnail_url: string; status: 'success' | 'failed' | 'pending';
  error_message: string | null; login_page: boolean; full_page: boolean;
  config: ScreenshotConfig | null;
}

interface ExecutionLog {
  id: string; device_id: string; device_name: string; started_at: string;
  completed_at: string | null; status: 'running' | 'completed' | 'failed' | 'partial';
  total_items: number; completed_items: number; ok_count: number; warning_count: number;
  critical_count: number; error_count: number; cert_warning: string | null;
}

const DEVICE_BRANDS = [
  { value: 'huawei_fw', label: 'Huawei USG', icon: '\u{1F6E1}\uFE0F', defaultPort: 443, authType: 'form' as AuthType, loginUrl: '/api/v1/sys/user/login' },
  { value: 'sangfor', label: 'Sangfor AF/SIP', icon: '\u{1F512}', defaultPort: 443, authType: 'form' as AuthType, loginUrl: '/cgi-bin/login.cgi' },
  { value: 'topsec', label: 'TopSec', icon: '\u{1F510}', defaultPort: 443, authType: 'form' as AuthType, loginUrl: '/login' },
  { value: 'venusec', label: 'Venustech', icon: '\u2B50', defaultPort: 443, authType: 'form' as AuthType, loginUrl: '/login.html' },
  { value: 'nsfocus', label: 'NSFOCUS NF', icon: '\u{1F310}', defaultPort: 443, authType: 'form' as AuthType, loginUrl: '/api/login' },
  { value: 'hillstone', label: 'Hillstone', icon: '\u{1F3D4}\uFE0F', defaultPort: 443, authType: 'form' as AuthType, loginUrl: '/rest/v1/auth' },
  { value: 'fortinet', label: 'FortiGate', icon: '\u{1F511}', defaultPort: 443, authType: 'form' as AuthType, loginUrl: '/logincheck' },
  { value: 'paloalto', label: 'Palo Alto', icon: '\u{1F17F}\uFE0F', defaultPort: 443, authType: 'form' as AuthType, loginUrl: '/api/' },
  { value: 'cisco_fw', label: 'Cisco Firepower', icon: '\u{1F535}', defaultPort: 443, authType: 'form' as AuthType, loginUrl: '/api/fdm/latest/fdm/login' },
  { value: 'generic', label: 'Generic HTTPS', icon: '\u{1F30D}', defaultPort: 443, authType: 'basic' as AuthType, loginUrl: '' },
  { value: 'legacy', label: 'Legacy (TLS1.0)', icon: '\u26A0\uFE0F', defaultPort: 443, authType: 'basic' as AuthType, loginUrl: '' },
];

const AUTH_CFG: Record<AuthType, { label: string; icon: React.ReactNode; desc: string }> = {
  form: { label: '\u8868\u5355\u767B\u5F55', icon: <Key size={14} />, desc: '\u6A21\u62DF\u6D4F\u89C8\u5668\u63D0\u4EA4\u7528\u6237\u540D\u5BC6\u7801\u8868\u5355' },
  basic: { label: 'Basic Auth', icon: <Lock size={14} />, desc: 'HTTP Basic Authentication' },
  token: { label: 'Token\u8BA4\u8BC1', icon: <Ticket size={14} />, desc: 'Bearer Token / API Key' },
  oauth2: { label: 'OAuth2', icon: <Shield size={14} />, desc: 'OAuth2 Client Credentials' },
  cookie: { label: 'Cookie', icon: <FileText size={14} />, desc: '\u624B\u52A8\u914D\u7F6ESession Cookie' },
  none: { label: '\u65E0\u9700\u8BA4\u8BC1', icon: <Unlock size={14} />, desc: '\u516C\u5F00\u63A5\u53E3' },
};

const TLS_V: TLSVersion[] = ['TLSv1.0', 'TLSv1.1', 'TLSv1.2', 'TLSv1.3'];

export default function HTTPIntegrationPage() {
  const [devices, setDevices] = useState<HTTPDevice[]>([]);
  const [certs, setCerts] = useState<SSLCertificate[]>([]);
  const [items, setItems] = useState<HTTPInspectionItem[]>([]);
  const [logs, setLogs] = useState<ExecutionLog[]>([]);
  const [screenshots, setScreenshots] = useState<Screenshot[]>([]);
  const [selId, setSelId] = useState<string | null>(null);
  const [tab, setTab] = useState<'connection' | 'certs' | 'items' | 'screenshots' | 'logs'>('connection');
  const [q, setQ] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [showCertUp, setShowCertUp] = useState(false);
  const [testId, setTestId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [previewImg, setPreviewImg] = useState<Screenshot | null>(null);

  const fetchAll = useCallback(async () => {
    try {
      const [d, c, i, l, s] = await Promise.all([
        fetch('/api/v1/http-integration/devices'), fetch('/api/v1/http-integration/certs'),
        fetch('/api/v1/http-integration/items'), fetch('/api/v1/http-integration/logs'),
        fetch('/api/v1/http-integration/screenshots'),
      ]);
      if (d.ok) setDevices(await d.json());
      if (c.ok) setCerts(await c.json());
      if (i.ok) setItems(await i.json());
      if (l.ok) setLogs(await l.json());
      if (s.ok) setScreenshots(await s.json());
    } catch { /* */ }
    setLoading(false);
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const sel = devices.find(d => d.id === selId) || null;
  const dCerts = certs.filter(c => c.device_id === selId);
  const dItems = items.filter(i => i.device_id === selId).sort((a, b) => a.order - b.order);
  const dLogs = logs.filter(l => l.device_id === selId);
  const dScreenshots = screenshots.filter(s => s.device_id === selId);
  const filtered = devices.filter(d => d.name.toLowerCase().includes(q.toLowerCase()) || d.brand.includes(q) || d.base_url.includes(q));

  const testConn = async (id: string) => {
    setTestId(id);
    try {
      const r = await fetch(`/api/v1/http-integration/devices/${id}/test`, { method: 'POST' });
      if (r.ok) { const data = await r.json(); setDevices(p => p.map(d => d.id === id ? { ...d, status: data.status, cert_status: data.cert_status, last_check: new Date().toISOString() } : d)); }
    } catch { /* */ }
    setTestId(null);
  };

  const delDev = async (id: string) => {
    if (!confirm('\u786E\u5B9A\u5220\u9664\u6B64\u8BBE\u5907\u8FDE\u63A5\uFF1F')) return;
    await fetch(`/api/v1/http-integration/devices/${id}`, { method: 'DELETE' });
    setDevices(p => p.filter(d => d.id !== id));
    if (selId === id) setSelId(null);
  };

  const runInsp = async (id: string) => { await fetch(`/api/v1/http-integration/devices/${id}/run`, { method: 'POST' }); fetchAll(); };

  if (loading) return <div className="flex items-center justify-center h-full"><RefreshCw className="animate-spin text-cyan-400" size={32} /><span className="ml-3 text-slate-400">{'\u52A0\u8F7D\u4E2D...'}</span></div>;

  return (
    <div className="flex h-full gap-0">
      <div className="w-80 bg-slate-900 border-r border-slate-700 flex flex-col shrink-0">
        <div className="p-3 border-b border-slate-700">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2"><Globe size={16} className="text-cyan-400" />HTTP{'\u8BBE\u5907\u8FDE\u63A5'}</h2>
            <button onClick={() => setShowAdd(true)} className="p-1.5 rounded bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30"><Plus size={14} /></button>
          </div>
          <div className="relative">
            <Search size={14} className="absolute left-2.5 top-2 text-slate-500" />
            <input type="text" placeholder={'\u641C\u7D22\u8BBE\u5907\u540D\u79F0/\u54C1\u724C/IP...'} value={q} onChange={e => setQ(e.target.value)} className="w-full pl-8 pr-3 py-1.5 bg-slate-800 border border-slate-600 rounded text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500" />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          {filtered.length === 0 ? (
            <div className="p-6 text-center"><Globe size={32} className="mx-auto text-slate-600 mb-2" /><p className="text-xs text-slate-500">{'\u6682\u65E0HTTP\u8BBE\u5907\u8FDE\u63A5'}</p></div>
          ) : filtered.map(d => (
            <div key={d.id} onClick={() => setSelId(d.id)} className={`px-3 py-2.5 cursor-pointer border-l-2 transition-colors group ${d.id === selId ? 'bg-slate-800 border-cyan-400' : 'border-transparent hover:bg-slate-800/50'}`}>
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm">{DEVICE_BRANDS.find(b => b.value === d.brand)?.icon || '\u{1F310}'}</span>
                    <span className="text-xs font-medium text-slate-200 truncate">{d.name}</span>
                    <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${d.status === 'connected' ? 'bg-green-400' : d.status === 'error' ? 'bg-red-400' : d.status === 'testing' ? 'bg-cyan-400 animate-pulse' : 'bg-slate-500'}`} />
                  </div>
                  <div className="mt-1"><span className="text-[10px] text-slate-500 font-mono">{d.use_https ? 'https' : 'http'}://{d.base_url}:{d.port}</span></div>
                  <div className="mt-1 flex items-center gap-2">
                    <span className={`text-[10px] ${d.cert_status === 'valid' ? 'text-green-400' : d.cert_status === 'expiring' ? 'text-amber-400' : d.cert_status === 'expired' ? 'text-red-400' : d.cert_status === 'self_signed' ? 'text-blue-400' : 'text-slate-500'} flex items-center gap-0.5`}>
                      {d.cert_status === 'valid' ? <ShieldCheck size={10} /> : d.cert_status === 'expired' ? <ShieldAlert size={10} /> : <FileKey size={10} />}
                      {d.cert_status === 'valid' ? '\u8BC1\u4E66\u6709\u6548' : d.cert_status === 'expiring' ? '\u5373\u5C06\u8FC7\u671F' : d.cert_status === 'expired' ? '\u5DF2\u8FC7\u671F' : d.cert_status === 'self_signed' ? '\u81EA\u7B7E\u540D' : '\u672A\u77E5'}
                    </span>
                    {d.compat_mode && <span className="text-[10px] text-amber-400 bg-amber-400/10 px-1 rounded flex items-center gap-0.5"><AlertTriangle size={9} />{'\u517C\u5BB9'}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={e => { e.stopPropagation(); testConn(d.id); }} className="p-1 rounded hover:bg-slate-700 text-slate-400 hover:text-cyan-400">
                    {testId === d.id ? <RefreshCw size={12} className="animate-spin" /> : <Wifi size={12} />}
                  </button>
                  <button onClick={e => { e.stopPropagation(); delDev(d.id); }} className="p-1 rounded hover:bg-slate-700 text-slate-400 hover:text-red-400"><Trash2 size={12} /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="p-3 border-t border-slate-700 bg-slate-900/50">
          <div className="grid grid-cols-3 gap-2 text-center">
            <div><div className="text-lg font-bold text-green-400">{devices.filter(d => d.status === 'connected').length}</div><div className="text-[10px] text-slate-500">{'\u5DF2\u8FDE\u63A5'}</div></div>
            <div><div className="text-lg font-bold text-amber-400">{certs.filter(c => c.status === 'expiring').length}</div><div className="text-[10px] text-slate-500">{'\u5373\u5C06\u8FC7\u671F'}</div></div>
            <div><div className="text-lg font-bold text-red-400">{certs.filter(c => c.status === 'expired').length}</div><div className="text-[10px] text-slate-500">{'\u5DF2\u8FC7\u671F'}</div></div>
          </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col overflow-hidden">
        {sel ? (
          <>
            <div className="px-4 py-3 border-b border-slate-700 bg-slate-900/30">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-xl">{DEVICE_BRANDS.find(b => b.value === sel.brand)?.icon || '\u{1F310}'}</span>
                  <div>
                    <h2 className="text-sm font-semibold text-slate-100">{sel.name}</h2>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className="text-[11px] text-slate-400">{DEVICE_BRANDS.find(b => b.value === sel.brand)?.label || sel.brand}</span>
                      <span className="text-[11px] text-slate-500 font-mono">{sel.use_https ? 'https' : 'http'}://{sel.base_url}:{sel.port}</span>
                      <span className={`text-[11px] px-1.5 py-0.5 rounded ${sel.status === 'connected' ? 'bg-green-500/20 text-green-400' : sel.status === 'error' ? 'bg-red-500/20 text-red-400' : 'bg-slate-700 text-slate-400'}`}>
                        {sel.status === 'connected' ? '\u5DF2\u8FDE\u63A5' : sel.status === 'error' ? '\u9519\u8BEF' : '\u672A\u8FDE\u63A5'}
                      </span>
                      {sel.compat_mode && <span className="text-[11px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">{'\u26A0\uFE0F'} {'\u517C\u5BB9\u6A21\u5F0F'} TLS {sel.tls_min_version}</span>}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => testConn(sel.id)} disabled={testId === sel.id} className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs bg-slate-700 text-slate-200 hover:bg-slate-600 disabled:opacity-50">
                    {testId === sel.id ? <RefreshCw size={12} className="animate-spin" /> : <Wifi size={12} />}
                    {testId === sel.id ? '\u6D4B\u8BD5\u4E2D...' : '\u6D4B\u8BD5\u8FDE\u63A5'}
                  </button>
                  <button onClick={() => runInsp(sel.id)} className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30"><Play size={12} />{'\u6267\u884C\u5DE1\u68C0'}</button>
                </div>
              </div>
            </div>
            <div className="flex border-b border-slate-700 bg-slate-900/50">
              {([{ k: 'connection' as const, l: '\u8FDE\u63A5\u914D\u7F6E', i: <Settings2 size={14} />, b: 0 }, { k: 'certs' as const, l: '\u8BC1\u4E66\u7BA1\u7406', i: <FileKey size={14} />, b: dCerts.length }, { k: 'items' as const, l: '\u5DE1\u68C0\u9879', i: <Terminal size={14} />, b: dItems.length }, { k: 'screenshots' as const, l: '\u622A\u56FE\u5DE1\u68C0', i: <Camera size={14} />, b: dScreenshots.length }, { k: 'logs' as const, l: '\u6267\u884C\u65E5\u5FD7', i: <Activity size={14} />, b: 0 }] as const).map(t => (
                <button key={t.k} onClick={() => setTab(t.k)} className={`flex items-center gap-1.5 px-4 py-2.5 text-xs font-medium transition-colors border-b-2 ${tab === t.k ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}>
                  {t.i}{t.l}{t.b !== undefined && t.b > 0 && <span className="ml-1 px-1.5 py-0.5 rounded-full bg-slate-700 text-[10px]">{t.b}</span>}
                </button>
              ))}
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {tab === 'connection' && <ConnTab device={sel} onUpdate={d => setDevices(p => p.map(v => v.id === d.id ? d : v))} />}
              {tab === 'certs' && <CertsTab certs={dCerts} onUpload={() => setShowCertUp(true)} />}
              {tab === 'items' && <ItemsTab items={dItems} deviceId={sel.id} onRefresh={fetchAll} />}
              {tab === 'screenshots' && <ScreenshotsTab screenshots={dScreenshots} onPreview={setPreviewImg} onCapture={async () => { await fetch(`/api/v1/http-integration/devices/${sel.id}/capture`, { method: 'POST' }); fetchAll(); }} />}
              {tab === 'logs' && <LogsTab logs={dLogs} />}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 rounded-2xl bg-slate-800 flex items-center justify-center mx-auto mb-4"><Globe size={32} className="text-cyan-400" /></div>
              <h3 className="text-lg font-semibold text-slate-200 mb-2">HTTP/HTTPS {'\u8BBE\u5907\u96C6\u6210'}</h3>
              <p className="text-sm text-slate-400 mb-4">{'\u9488\u5BF9\u65E0 SSH/SNMP \u63A5\u53E3\u7684\u5B89\u5168\u8BBE\u5907\u3001\u8001\u65E7\u8BBE\u5907\uFF0C\u901A\u8FC7 HTTP/HTTPS \u534F\u8BAE\u81EA\u52A8\u767B\u5F55\u8BBE\u5907 Web \u7BA1\u7406\u754C\u9762\uFF0C\u91C7\u96C6\u5DE1\u68C0\u6570\u636E\u3002'}</p>
              <div className="grid grid-cols-2 gap-3 text-left mb-6">
                {[{ i: <Lock size={14} className="text-cyan-400" />, t: 'TLS \u517C\u5BB9', d: '\u652F\u6301 TLS 1.0/1.1 \u8001\u534F\u8BAE' }, { i: <FileKey size={14} className="text-blue-400" />, t: '\u8BC1\u4E66\u7BA1\u7406', d: '\u81EA\u7B7E\u540D\u8BC1\u4E66\u5BFC\u5165\u4E0E\u4FE1\u4EFB' }, { i: <Key size={14} className="text-amber-400" />, t: '\u591A\u79CD\u8BA4\u8BC1', d: '\u8868\u5355/Basic/Token/OAuth2' }, { i: <Terminal size={14} className="text-green-400" />, t: '\u7075\u6D3B\u89E3\u6790', d: 'JSON/CSS/XPath/\u6B63\u5219' }].map((f, idx) => (
                  <div key={idx} className="p-2.5 rounded border border-slate-700 bg-slate-800/50">
                    <div className="flex items-center gap-2 mb-1">{f.i}<span className="text-xs font-medium text-slate-200">{f.t}</span></div>
                    <p className="text-[11px] text-slate-500">{f.d}</p>
                  </div>
                ))}
              </div>
              <button onClick={() => setShowAdd(true)} className="px-4 py-2 rounded-lg bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 text-sm font-medium"><Plus size={14} className="inline mr-1.5" />{'\u6DFB\u52A0 HTTP \u8BBE\u5907'}</button>
            </div>
          </div>
        )}
      </div>

      {showAdd && <AddDialog onClose={() => setShowAdd(false)} onAdd={dev => { setDevices(p => [...p, dev]); setShowAdd(false); setSelId(dev.id); }} />}
      {showCertUp && selId && <CertUpDialog deviceId={selId} deviceName={sel?.name || ''} onClose={() => setShowCertUp(false)} onUpload={fetchAll} />}
      {previewImg && <ScreenshotPreview screenshot={previewImg} onClose={() => setPreviewImg(null)} />}
    </div>
  );
}

function Section({ title, icon, badge, badgeColor, children }: { title: string; icon: React.ReactNode; badge?: string; badgeColor?: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-800/20 overflow-hidden">
      <div className="px-4 py-2.5 border-b border-slate-700 bg-slate-800/40 flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs font-medium text-slate-200">{icon}{title}</div>
        {badge && <span className={`text-[10px] px-1.5 py-0.5 rounded ${badgeColor === 'amber' ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-700 text-slate-400'}`}>{badge}</span>}
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
}

function Field({ label, full, children }: { label: string; full?: boolean; children: React.ReactNode }) {
  return <div className={full ? 'col-span-2' : ''}><label className="text-[11px] text-slate-400 block mb-1">{label}</label>{children}</div>;
}

function ConnTab({ device, onUpdate }: { device: HTTPDevice; onUpdate: (d: HTTPDevice) => void }) {
  const [edit, setEdit] = useState(false);
  const [f, setF] = useState(device);
  const [showPw, setShowPw] = useState(false);
  useEffect(() => { setF(device); setEdit(false); }, [device]);

  return (
    <div className="space-y-4 max-w-3xl">
      <Section title={'\u57FA\u7840\u8FDE\u63A5'} icon={<Globe size={16} />}>
        <div className="grid grid-cols-2 gap-3">
          <Field label={'\u8BBE\u5907\u540D\u79F0'}><input value={f.name} onChange={e => setF({ ...f, name: e.target.value })} disabled={!edit} className="input-field" /></Field>
          <Field label={'\u8BBE\u5907\u54C1\u724C'}>
            <select value={f.brand} onChange={e => { const b = DEVICE_BRANDS.find(x => x.value === e.target.value); setF({ ...f, brand: e.target.value, port: b?.defaultPort || f.port, auth_type: b?.authType || f.auth_type, login_url: b?.loginUrl || '' }); }} disabled={!edit} className="input-field">
              {DEVICE_BRANDS.map(b => <option key={b.value} value={b.value}>{b.icon} {b.label}</option>)}
            </select>
          </Field>
          <Field label={'\u534F\u8BAE'}>
            <div className="flex gap-2">
              <button onClick={() => edit && setF({ ...f, use_https: true })} className={`flex-1 py-1.5 rounded text-xs font-medium ${f.use_https ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-slate-800 text-slate-400 border border-slate-600'} ${!edit ? 'opacity-60' : ''}`}><Lock size={12} className="inline mr-1" />HTTPS</button>
              <button onClick={() => edit && setF({ ...f, use_https: false })} className={`flex-1 py-1.5 rounded text-xs font-medium ${!f.use_https ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-slate-800 text-slate-400 border border-slate-600'} ${!edit ? 'opacity-60' : ''}`}><Unlock size={12} className="inline mr-1" />HTTP</button>
            </div>
          </Field>
          <Field label={'\u7AEF\u53E3'}><input type="number" value={f.port} onChange={e => setF({ ...f, port: parseInt(e.target.value) || 443 })} disabled={!edit} className="input-field" /></Field>
          <Field label={'\u4E3B\u673A\u5730\u5740'} full><input value={f.base_url} onChange={e => setF({ ...f, base_url: e.target.value })} disabled={!edit} placeholder={'\u4F8B\u5982: 10.0.1.254'} className="input-field" /></Field>
          <Field label={'\u8D85\u65F6(\u79D2)'}><input type="number" value={f.timeout} onChange={e => setF({ ...f, timeout: parseInt(e.target.value) || 30 })} disabled={!edit} className="input-field" /></Field>
          <Field label={'\u6807\u7B7E'}><input value={f.tags.join(', ')} onChange={e => setF({ ...f, tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean) })} disabled={!edit} className="input-field" /></Field>
        </div>
      </Section>

      <Section title={'\u8BA4\u8BC1\u914D\u7F6E'} icon={<Key size={16} />}>
        <Field label={'\u8BA4\u8BC1\u65B9\u5F0F'}>
          <div className="grid grid-cols-3 gap-2">
            {(Object.entries(AUTH_CFG) as [AuthType, typeof AUTH_CFG[AuthType]][]).map(([k, c]) => (
              <button key={k} onClick={() => edit && setF({ ...f, auth_type: k })} disabled={!edit} className={`p-2 rounded text-left ${f.auth_type === k ? 'bg-cyan-500/20 border border-cyan-500/30 text-cyan-400' : 'bg-slate-800 border border-slate-700 text-slate-400 hover:border-slate-600'} ${!edit ? 'opacity-60' : ''}`}>
                <div className="flex items-center gap-1.5">{c.icon}<span className="text-xs font-medium">{c.label}</span></div>
                <p className="text-[10px] mt-1 text-slate-500 leading-tight">{c.desc}</p>
              </button>
            ))}
          </div>
        </Field>
        {(f.auth_type === 'form' || f.auth_type === 'basic') && (
          <div className="grid grid-cols-2 gap-3 mt-3">
            <Field label={'\u7528\u6237\u540D'}><input value={f.username} onChange={e => setF({ ...f, username: e.target.value })} disabled={!edit} className="input-field" /></Field>
            <Field label={'\u5BC6\u7801'}>
              <div className="relative">
                <input type={showPw ? 'text' : 'password'} value={f.password_enc} onChange={e => setF({ ...f, password_enc: e.target.value })} disabled={!edit} className="input-field pr-8" />
                <button onClick={() => setShowPw(!showPw)} className="absolute right-2 top-1.5 text-slate-500 hover:text-slate-300">{showPw ? <EyeOff size={14} /> : <Eye size={14} />}</button>
              </div>
            </Field>
          </div>
        )}
        {f.auth_type === 'form' && (
          <div className="mt-3 p-3 bg-slate-800/50 rounded border border-slate-700">
            <p className="text-[11px] text-slate-400 mb-2 font-medium">{'\u8868\u5355\u767B\u5F55\u914D\u7F6E'}</p>
            <div className="grid grid-cols-2 gap-3">
              <Field label={'\u767B\u5F55URL\u8DEF\u5F84'}><input value={f.login_url} onChange={e => setF({ ...f, login_url: e.target.value })} disabled={!edit} placeholder="/login" className="input-field" /></Field>
              <Field label={'\u7528\u6237\u540D\u5B57\u6BB5\u540D'}><input value={f.username_field || ''} onChange={e => setF({ ...f, username_field: e.target.value })} disabled={!edit} placeholder="username" className="input-field" /></Field>
              <Field label={'\u5BC6\u7801\u5B57\u6BB5\u540D'}><input value={f.password_field || ''} onChange={e => setF({ ...f, password_field: e.target.value })} disabled={!edit} placeholder="password" className="input-field" /></Field>
              <Field label={'\u63D0\u4EA4\u6309\u94AE\u9009\u62E9\u5668'}><input value={f.submit_selector || ''} onChange={e => setF({ ...f, submit_selector: e.target.value })} disabled={!edit} placeholder="button[type=submit]" className="input-field" /></Field>
            </div>
          </div>
        )}
        {f.auth_type === 'token' && <Field label="Bearer Token / API Key" full><input value={f.password_enc} onChange={e => setF({ ...f, password_enc: e.target.value })} disabled={!edit} className="input-field font-mono" /></Field>}
      </Section>

      <Section title="TLS/SSL \u914D\u7F6E" icon={<Lock size={16} />} badge={f.compat_mode ? '\u517C\u5BB9\u6A21\u5F0F' : undefined} badgeColor={f.compat_mode ? 'amber' : undefined}>
        <div className="grid grid-cols-2 gap-3">
          <Field label={'\u6700\u4F4E TLS \u7248\u672C'}>
            <select value={f.tls_min_version} onChange={e => { const v = e.target.value as TLSVersion; setF({ ...f, tls_min_version: v, compat_mode: v === 'TLSv1.0' || v === 'TLSv1.1' }); }} disabled={!edit} className="input-field">
              {TLS_V.map(v => <option key={v} value={v}>{v} {(v === 'TLSv1.0' || v === 'TLSv1.1') ? '\u26A0\uFE0F \u4E0D\u5B89\u5168' : '\u2713'}</option>)}
            </select>
          </Field>
          <Field label={'\u6700\u9AD8 TLS \u7248\u672C'}>
            <select value={f.tls_max_version} onChange={e => setF({ ...f, tls_max_version: e.target.value as TLSVersion })} disabled={!edit} className="input-field">
              {TLS_V.map(v => <option key={v} value={v}>{v}</option>)}
            </select>
          </Field>
        </div>
        <div className="flex flex-wrap gap-3 mt-3">
          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer"><input type="checkbox" checked={f.verify_cert} onChange={e => setF({ ...f, verify_cert: e.target.checked })} disabled={!edit} className="rounded border-slate-600" />{'\u9A8C\u8BC1\u670D\u52A1\u5668\u8BC1\u4E66'}</label>
          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer"><input type="checkbox" checked={f.accept_self_signed} onChange={e => setF({ ...f, accept_self_signed: e.target.checked })} disabled={!edit} className="rounded border-slate-600" />{'\u63A5\u53D7\u81EA\u7B7E\u540D\u8BC1\u4E66'}</label>
        </div>
        {f.compat_mode && (
          <div className="mt-3 p-3 rounded border border-amber-500/30 bg-amber-500/5">
            <div className="flex items-start gap-2">
              <AlertTriangle size={16} className="text-amber-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-xs text-amber-400 font-medium">{'\u517C\u5BB9\u6A21\u5F0F\u5DF2\u542F\u7528'}</p>
                <p className="text-[11px] text-slate-400 mt-1">{'\u6700\u4F4E TLS \u7248\u672C\u8BBE\u7F6E\u4E3A'} {f.tls_min_version}{'\uFF0C\u6B64\u534F\u8BAE\u5B58\u5728\u5DF2\u77E5\u5B89\u5168\u6F0F\u6D1E\u3002\u7CFB\u7EDF\u5C06\u5141\u8BB8\u4F7F\u7528\u8F83\u5F31\u7684\u52A0\u5BC6\u5957\u4EF6\u4E0E\u8001\u8BBE\u5907\u901A\u4FE1\u3002\u8BF7\u786E\u4FDD\u4EC5\u7528\u4E8E\u5185\u7F51\u5DE1\u68C0\u3002'}</p>
                <div className="mt-2 flex flex-wrap gap-1">
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400">{'\u5F31\u52A0\u5BC6\u5957\u4EF6\u5DF2\u542F\u7528'}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400">{'\u8BC1\u4E66\u9A8C\u8BC1\u53EF\u80FD\u964D\u7EA7'}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400">{'\u4EC5\u5EFA\u8BAE\u5185\u7F51\u4F7F\u7528'}</span>
                </div>
              </div>
            </div>
          </div>
        )}
        <Field label={'\u81EA\u5B9A\u4E49\u52A0\u5BC6\u5957\u4EF6 (\u9017\u53F7\u5206\u9694)'} full>
          <input value={f.cipher_suites.join(', ')} onChange={e => setF({ ...f, cipher_suites: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })} disabled={!edit} placeholder={'\u7559\u7A7A\u4F7F\u7528\u9ED8\u8BA4; \u8001\u8BBE\u5907: RSA_AES_128_CBC_SHA, RSA_AES_256_CBC_SHA'} className="input-field font-mono text-[11px]" />
        </Field>
      </Section>

      <Section title={'\u81EA\u5B9A\u4E49 HTTP \u8BF7\u6C42\u5934'} icon={<FileText size={16} />}>
        <div className="space-y-2">
          {Object.entries(f.custom_headers).map(([k, v], i) => (
            <div key={i} className="flex gap-2">
              <input value={k} onChange={e => { const h = { ...f.custom_headers }; delete h[k]; h[e.target.value] = v; setF({ ...f, custom_headers: h }); }} disabled={!edit} placeholder="Header-Name" className="input-field flex-1 font-mono text-[11px]" />
              <input value={v} onChange={e => setF({ ...f, custom_headers: { ...f.custom_headers, [k]: e.target.value } })} disabled={!edit} placeholder="Header-Value" className="input-field flex-1 font-mono text-[11px]" />
              {edit && <button onClick={() => { const h = { ...f.custom_headers }; delete h[k]; setF({ ...f, custom_headers: h }); }} className="p-1.5 text-slate-500 hover:text-red-400"><Trash2 size={12} /></button>}
            </div>
          ))}
          {edit && <button onClick={() => setF({ ...f, custom_headers: { ...f.custom_headers, '': '' } })} className="text-[11px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1"><Plus size={12} />{'\u6DFB\u52A0\u8BF7\u6C42\u5934'}</button>}
        </div>
      </Section>

      <div className="flex justify-end gap-2 pt-2">
        {edit ? (<><button onClick={() => { setF(device); setEdit(false); }} className="px-4 py-1.5 rounded text-xs bg-slate-700 text-slate-300 hover:bg-slate-600">{'\u53D6\u6D88'}</button><button onClick={() => { onUpdate(f); setEdit(false); }} className="px-4 py-1.5 rounded text-xs bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30">{'\u4FDD\u5B58\u914D\u7F6E'}</button></>) : (<button onClick={() => setEdit(true)} className="px-4 py-1.5 rounded text-xs bg-slate-700 text-slate-200 hover:bg-slate-600">{'\u7F16\u8F91\u914D\u7F6E'}</button>)}
      </div>
    </div>
  );
}

function CertsTab({ certs, onUpload }: { certs: SSLCertificate[]; onUpload: () => void }) {
  return (
    <div className="space-y-4 max-w-3xl">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-200">SSL/TLS {'\u8BC1\u4E66\u5217\u8868'}</h3>
        <button onClick={onUpload} className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30"><Upload size={12} />{'\u5BFC\u5165\u8BC1\u4E66'}</button>
      </div>
      <div className="grid grid-cols-4 gap-3">
        {[{ l: '\u6709\u6548', c: certs.filter(x => x.status === 'valid').length, cl: 'text-green-400', bg: 'bg-green-500/10', ic: <ShieldCheck size={16} /> }, { l: '\u5373\u5C06\u8FC7\u671F', c: certs.filter(x => x.status === 'expiring').length, cl: 'text-amber-400', bg: 'bg-amber-500/10', ic: <Clock size={16} /> }, { l: '\u5DF2\u8FC7\u671F', c: certs.filter(x => x.status === 'expired').length, cl: 'text-red-400', bg: 'bg-red-500/10', ic: <XCircle size={16} /> }, { l: '\u81EA\u7B7E\u540D', c: certs.filter(x => x.status === 'self_signed').length, cl: 'text-blue-400', bg: 'bg-blue-500/10', ic: <FileKey size={16} /> }].map(s => (
          <div key={s.l} className={`p-3 rounded border border-slate-700 ${s.bg}`}><div className={`flex items-center gap-2 ${s.cl}`}>{s.ic}<span className="text-lg font-bold">{s.c}</span></div><p className="text-[11px] text-slate-400 mt-1">{s.l}</p></div>
        ))}
      </div>
      {certs.length === 0 ? (
        <div className="p-8 text-center border border-dashed border-slate-700 rounded"><FileKey size={32} className="mx-auto text-slate-600 mb-2" /><p className="text-xs text-slate-500">{'\u6682\u65E0\u8BC1\u4E66\u8BB0\u5F55'}</p><p className="text-[11px] text-slate-600 mt-1">{'\u70B9\u51FB\u201C\u5BFC\u5165\u8BC1\u4E66\u201D\u4E0A\u4F20\u8BBE\u5907\u8BC1\u4E66'}</p></div>
      ) : (
        <div className="space-y-2">{certs.map(c => <CertCard key={c.id} cert={c} />)}</div>
      )}
      <div className="p-4 rounded border border-slate-700 bg-slate-800/30">
        <h4 className="text-xs font-medium text-slate-300 mb-2 flex items-center gap-2"><AlertTriangle size={14} className="text-amber-400" />{'\u8001\u8BBE\u5907\u8BC1\u4E66\u517C\u5BB9\u8BF4\u660E'}</h4>
        <div className="space-y-1.5 text-[11px] text-slate-400">
          <p>1. <strong className="text-slate-300">{'\u81EA\u7B7E\u540D\u8BC1\u4E66'}</strong>{'\uFF1A\u5B89\u5168\u8BBE\u5907\u901A\u5E38\u4F7F\u7528\u81EA\u7B7E\u540D\u8BC1\u4E66\uFF0C\u9700\u5728\u201C\u8FDE\u63A5\u914D\u7F6E\u201D\u4E2D\u5F00\u542F\u201C\u63A5\u53D7\u81EA\u7B7E\u540D\u8BC1\u4E66\u201D'}</p>
          <p>2. <strong className="text-slate-300">SHA-1 {'\u7B7E\u540D'}</strong>{'\uFF1A\u8001\u8BBE\u5907\u53EF\u80FD\u4F7F\u7528 SHA-1 \u7B7E\u540D\u7B97\u6CD5\uFF0C\u9700\u5728\u517C\u5BB9\u6A21\u5F0F\u4E0B\u624D\u80FD\u4FE1\u4EFB'}</p>
          <p>3. <strong className="text-slate-300">{'\u77ED\u5BC6\u94A5'}</strong>{'\uFF1A1024-bit RSA \u5BC6\u94A5\u5728\u73B0\u4EE3\u6D4F\u89C8\u5668\u4E2D\u4E0D\u88AB\u4FE1\u4EFB\uFF0C\u517C\u5BB9\u6A21\u5F0F\u53EF\u7ED5\u8FC7'}</p>
          <p>4. <strong className="text-slate-300">{'\u8BC1\u4E66\u5BFC\u5165'}</strong>{'\uFF1A\u652F\u6301 PEM/DER/CER/P7B \u683C\u5F0F\uFF0C\u5BFC\u5165\u540E\u53EF\u5168\u5C40\u4FE1\u4EFB\u8BE5 CA'}</p>
          <p>5. <strong className="text-slate-300">{'\u8BC1\u4E66\u94FE'}</strong>{'\uFF1A\u5982\u8BBE\u5907\u4F7F\u7528\u4E2D\u95F4 CA\uFF0C\u9700\u5BFC\u5165\u5B8C\u6574\u8BC1\u4E66\u94FE'}</p>
        </div>
      </div>
    </div>
  );
}

function CertCard({ cert }: { cert: SSLCertificate }) {
  const [exp, setExp] = useState(false);
  const cfg = { valid: { cl: 'text-green-400', bd: 'border-green-500/20', bg: 'bg-green-500/10', lb: '\u6709\u6548' }, expiring: { cl: 'text-amber-400', bd: 'border-amber-500/20', bg: 'bg-amber-500/10', lb: '\u5373\u5C06\u8FC7\u671F' }, expired: { cl: 'text-red-400', bd: 'border-red-500/20', bg: 'bg-red-500/10', lb: '\u5DF2\u8FC7\u671F' }, self_signed: { cl: 'text-blue-400', bd: 'border-blue-500/20', bg: 'bg-blue-500/10', lb: '\u81EA\u7B7E\u540D' }, unknown: { cl: 'text-slate-400', bd: 'border-slate-500/20', bg: 'bg-slate-500/10', lb: '\u672A\u77E5' } }[cert.status];
  const [days] = useState(() => Math.ceil((new Date(cert.valid_to).getTime() - new Date().getTime()) / 86400000));
  return (
    <div className={`rounded border ${cfg.bd} ${cfg.bg} overflow-hidden`}>
      <div className="p-3 flex items-center justify-between cursor-pointer" onClick={() => setExp(!exp)}>
        <div className="flex items-center gap-3"><FileKey size={18} className={cfg.cl} /><div><p className="text-xs font-medium text-slate-200">{cert.subject}</p><p className="text-[10px] text-slate-500 mt-0.5">{'\u7B7E\u53D1\u8005'}: {cert.issuer} | {cert.key_size}-bit {cert.signature_algorithm}</p></div></div>
        <div className="flex items-center gap-3"><div className="text-right"><span className={`text-[11px] font-medium ${cfg.cl}`}>{cfg.lb}</span><p className="text-[10px] text-slate-500">{cert.status === 'expired' ? `\u5DF2\u8FC7\u671F ${Math.abs(days)} \u5929` : cert.status === 'expiring' ? `${days} \u5929\u540E\u8FC7\u671F` : `\u6709\u6548\u81F3 ${new Date(cert.valid_to).toLocaleDateString()}`}</p></div>{cert.trusted && <ShieldCheck size={14} className="text-green-400" />}{exp ? <ChevronDown size={14} className="text-slate-500" /> : <ChevronRight size={14} className="text-slate-500" />}</div>
      </div>
      {exp && (
        <div className="px-3 pb-3 border-t border-slate-700/50 pt-2">
          <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-[11px]">
            <div><span className="text-slate-500">{'\u5E8F\u5217\u53F7'}:</span> <span className="text-slate-300 font-mono">{cert.serial}</span></div>
            <div><span className="text-slate-500">{'\u7B7E\u540D\u7B97\u6CD5'}:</span> <span className="text-slate-300">{cert.signature_algorithm}</span></div>
            <div><span className="text-slate-500">{'\u751F\u6548'}:</span> <span className="text-slate-300">{new Date(cert.valid_from).toLocaleString()}</span></div>
            <div><span className="text-slate-500">{'\u8FC7\u671F'}:</span> <span className="text-slate-300">{new Date(cert.valid_to).toLocaleString()}</span></div>
            <div className="col-span-2"><span className="text-slate-500">SAN:</span> <span className="text-slate-300 font-mono">{cert.san.join(', ')}</span></div>
            <div><span className="text-slate-500">{'\u6765\u6E90'}:</span> <span className="text-slate-300">{cert.imported ? '\u624B\u52A8\u5BFC\u5165' : '\u81EA\u52A8\u83B7\u53D6'}</span></div>
            <div><span className="text-slate-500">{'\u4FE1\u4EFB'}:</span> <span className={cert.trusted ? 'text-green-400' : 'text-amber-400'}>{cert.trusted ? '\u5DF2\u4FE1\u4EFB' : '\u672A\u4FE1\u4EFB'}</span></div>
          </div>
        </div>
      )}
    </div>
  );
}

function ItemsTab({ items, deviceId, onRefresh }: { items: HTTPInspectionItem[]; deviceId: string; onRefresh: () => void }) {
  const [add, setAdd] = useState(false);
  const cats = [...new Set(items.map(i => i.category))];
  return (
    <div className="space-y-4 max-w-3xl">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-200">HTTP {'\u5DE1\u68C0\u9879\u914D\u7F6E'}</h3>
        <button onClick={() => setAdd(!add)} className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30"><Plus size={12} />{'\u6DFB\u52A0\u5DE1\u68C0\u9879'}</button>
      </div>
      {add && <AddItemForm deviceId={deviceId} onDone={() => { setAdd(false); onRefresh(); }} />}
      {items.length === 0 ? (
        <div className="p-8 text-center border border-dashed border-slate-700 rounded"><Terminal size={32} className="mx-auto text-slate-600 mb-2" /><p className="text-xs text-slate-500">{'\u6682\u65E0\u5DE1\u68C0\u9879'}</p></div>
      ) : cats.map(cat => (
        <div key={cat}>
          <h4 className="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-2">{cat}</h4>
          <div className="space-y-1.5">{items.filter(i => i.category === cat).map(item => <ItemCard key={item.id} item={item} />)}</div>
        </div>
      ))}
    </div>
  );
}

function ItemCard({ item }: { item: HTTPInspectionItem }) {
  const [exp, setExp] = useState(false);
  const isSS = item.parser_type === 'screenshot';
  const navLabel = { url: '\u76F4\u63A5 URL', menu_click: '\u83DC\u5355\u5BFC\u822A', url_then_menu: 'URL + \u83DC\u5355' };
  const areaLabel = { full_page: '\u5168\u9875', viewport: '\u53EF\u89C6\u533A\u57DF', element: '\u6307\u5B9A\u5143\u7D20' };
  return (
    <div className="rounded border border-slate-700 bg-slate-800/30 overflow-hidden">
      <div className="px-3 py-2 flex items-center justify-between cursor-pointer" onClick={() => setExp(!exp)}>
        <div className="flex items-center gap-2">
          {isSS ? <Camera size={12} className="text-cyan-400" /> : item.is_read_only ? <Lock size={12} className="text-green-400" /> : <AlertTriangle size={12} className="text-amber-400" />}
          <span className="text-xs text-slate-200">{item.name}</span>
          {isSS ? <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400">{'\u622A\u56FE'}</span> : <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-700 text-slate-400 font-mono">{item.method} {item.url_path}</span>}
        </div>
        <div className="flex items-center gap-2">
          {isSS && item.screenshot_config?.word_template_key && <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 font-mono" title="Word \u6A21\u677F\u5360\u4F4D\u7B26">{item.screenshot_config.word_template_key}</span>}
          {!isSS && item.threshold && <span className="text-[10px] text-amber-400">{item.threshold.operator} {item.threshold.warning}/{item.threshold.critical}{item.threshold.unit}</span>}
          <span className="text-[10px] text-slate-500">w:{item.weight}</span>{exp ? <ChevronDown size={12} className="text-slate-500" /> : <ChevronRight size={12} className="text-slate-500" />}
        </div>
      </div>
      {exp && (
        <div className="px-3 pb-3 border-t border-slate-700/50 pt-2">
          {isSS && item.screenshot_config ? (
            <div className="space-y-2">
              <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-[11px]">
                <div><span className="text-slate-500">{'\u5BFC\u822A\u65B9\u5F0F'}:</span> <span className="text-cyan-400">{navLabel[item.screenshot_config.navigate_type] || item.screenshot_config.navigate_type}</span></div>
                <div><span className="text-slate-500">{'\u622A\u56FE\u533A\u57DF'}:</span> <span className="text-slate-300">{areaLabel[item.screenshot_config.capture_area] || item.screenshot_config.capture_area}</span></div>
                {item.screenshot_config.target_url && <div className="col-span-2"><span className="text-slate-500">{'\u76EE\u6807 URL'}:</span> <span className="text-slate-300 font-mono">{item.screenshot_config.target_url}</span></div>}
                {item.screenshot_config.menu_path.length > 0 && item.screenshot_config.menu_path[0] && <div className="col-span-2"><span className="text-slate-500">{'\u83DC\u5355\u8DEF\u5F84'}:</span> <span className="text-slate-300">{item.screenshot_config.menu_path.join(' \u2192 ')}</span></div>}
                {item.screenshot_config.wait_selector && <div className="col-span-2"><span className="text-slate-500">{'\u7B49\u5F85\u5143\u7D20'}:</span> <span className="text-slate-300 font-mono">{item.screenshot_config.wait_selector}</span> <span className="text-slate-500">({item.screenshot_config.wait_timeout}ms)</span></div>}
                {item.screenshot_config.capture_selector && <div className="col-span-2"><span className="text-slate-500">{'\u622A\u56FE\u5143\u7D20'}:</span> <span className="text-slate-300 font-mono">{item.screenshot_config.capture_selector}</span></div>}
              </div>
              {item.screenshot_config.word_template_key && (
                <div className="p-2 rounded bg-amber-500/5 border border-amber-500/20">
                  <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-[11px]">
                    <div><span className="text-slate-500">Word {'\u5360\u4F4D\u7B26'}:</span> <span className="text-amber-400 font-mono">{item.screenshot_config.word_template_key}</span></div>
                    <div><span className="text-slate-500">{'\u62A5\u544A\u7AE0\u8287'}:</span> <span className="text-slate-300">{item.screenshot_config.word_section || '-'}</span></div>
                    <div><span className="text-slate-500">{'\u4F4D\u7F6E\u5E8F\u53F7'}:</span> <span className="text-slate-300">{item.screenshot_config.word_position}</span></div>
                    <div><span className="text-slate-500">{'\u56FE\u7247\u5BBD\u5EA6'}:</span> <span className="text-slate-300">{item.screenshot_config.image_width_mm}mm</span></div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-[11px]">
              <div><span className="text-slate-500">{'\u89E3\u6790'}:</span> <span className="text-slate-300">{item.parser_type}</span></div>
              <div><span className="text-slate-500">{'\u8868\u8FBE\u5F0F'}:</span> <span className="text-slate-300 font-mono">{item.parser_expression}</span></div>
              <div><span className="text-slate-500">Content-Type:</span> <span className="text-slate-300">{item.content_type}</span></div>
              <div><span className="text-slate-500">{'\u53EA\u8BFB'}:</span> <span className={item.is_read_only ? 'text-green-400' : 'text-amber-400'}>{item.is_read_only ? '\u662F' : '\u5426'}</span></div>
            </div>
          )}
          {!isSS && item.request_body && <div className="mt-2"><span className="text-[11px] text-slate-500">{'\u8BF7\u6C42\u4F53'}:</span><pre className="mt-1 p-2 rounded bg-slate-900 text-[10px] text-slate-300 font-mono overflow-x-auto">{item.request_body}</pre></div>}
        </div>
      )}
    </div>
  );
}

function AddItemForm({ deviceId, onDone }: { deviceId: string; onDone: () => void }) {
  const [f, setF] = useState({ name: '', category: '\u7CFB\u7EDF\u4FE1\u606F', method: 'GET', url_path: '', request_body: '', content_type: 'application/json', parser_type: 'json_path' as 'json_path' | 'css_selector' | 'xpath' | 'regex' | 'raw' | 'screenshot', parser_expression: '', is_read_only: true, weight: 10, order: 1, has_threshold: false, threshold_op: 'gt', threshold_warn: 0, threshold_crit: 0, threshold_unit: '' });
  const [sc, setSc] = useState<ScreenshotConfig>({ navigate_type: 'url', target_url: '', menu_path: [''], wait_selector: '', wait_timeout: 5000, capture_area: 'full_page', capture_selector: '', word_template_key: '', word_section: '', word_position: 1, image_width_mm: 160 });
  const isScreenshot = f.parser_type === 'screenshot';
  const submit = async () => {
    if (!f.name || (!isScreenshot && !f.url_path)) return;
    if (isScreenshot && !sc.target_url && sc.navigate_type !== 'menu_click') return;
    const payload: Record<string, unknown> = { device_id: deviceId, ...f, threshold: f.has_threshold ? { operator: f.threshold_op, critical: f.threshold_crit, warning: f.threshold_warn, unit: f.threshold_unit } : null };
    if (isScreenshot) { payload.screenshot_config = { ...sc, menu_path: sc.menu_path.filter(Boolean) }; }
    await fetch('/api/v1/http-integration/items', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    onDone();
  };
  return (
    <div className="p-4 rounded border border-cyan-500/20 bg-cyan-500/5 space-y-3">
      <h4 className="text-xs font-medium text-cyan-400">{'\u6DFB\u52A0 HTTP \u5DE1\u68C0\u9879'}</h4>
      <div className="grid grid-cols-2 gap-3">
        <div><label className="text-[11px] text-slate-400 block mb-1">{'\u540D\u79F0'}</label><input value={f.name} onChange={e => setF({ ...f, name: e.target.value })} className="input-field" /></div>
        <div><label className="text-[11px] text-slate-400 block mb-1">{'\u5206\u7C7B'}</label>
          <select value={f.category} onChange={e => setF({ ...f, category: e.target.value })} className="input-field">
            {['\u7CFB\u7EDF\u4FE1\u606F', '\u7F51\u7EDC\u914D\u7F6E', '\u5B89\u5168\u7B56\u7565', '\u6027\u80FD\u76D1\u63A7', '\u65E5\u5FD7\u5BA1\u8BA1', '\u8BC1\u4E66\u72B6\u6001', '\u7CFB\u7EDF\u72B6\u6001', '\u622A\u56FE\u5DE1\u68C0'].map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div><label className="text-[11px] text-slate-400 block mb-1">{'\u89E3\u6790\u7C7B\u578B'}</label>
          <select value={f.parser_type} onChange={e => setF({ ...f, parser_type: e.target.value as typeof f.parser_type })} className="input-field">
            <option value="json_path">JSONPath</option><option value="css_selector">CSS Selector</option><option value="xpath">XPath</option><option value="regex">{'\u6B63\u5219\u8868\u8FBE\u5F0F'}</option><option value="raw">{'\u539F\u59CB\u54CD\u5E94'}</option><option value="screenshot">{'\u622A\u56FE\u5DE1\u68C0'}</option>
          </select>
        </div>
        {!isScreenshot && (<><div><label className="text-[11px] text-slate-400 block mb-1">{'\u65B9\u6CD5'}</label>
          <select value={f.method} onChange={e => setF({ ...f, method: e.target.value })} className="input-field">
            {['GET', 'POST', 'PUT', 'DELETE'].map(m => <option key={m} value={m}>{m}</option>)}
          </select></div>
          <div><label className="text-[11px] text-slate-400 block mb-1">URL {'\u8DEF\u5F84'}</label><input value={f.url_path} onChange={e => setF({ ...f, url_path: e.target.value })} placeholder="/api/v1/status" className="input-field font-mono" /></div>
          <div className="col-span-2"><label className="text-[11px] text-slate-400 block mb-1">{'\u89E3\u6790\u8868\u8FBE\u5F0F'}</label><input value={f.parser_expression} onChange={e => setF({ ...f, parser_expression: e.target.value })} placeholder="$.data.status" className="input-field font-mono" /></div>
        </>)}
      </div>
      {isScreenshot && (
        <div className="space-y-3 p-3 rounded border border-cyan-500/20 bg-slate-900/50">
          <h5 className="text-[11px] font-medium text-cyan-400 flex items-center gap-1.5"><Camera size={12} />{'\u622A\u56FE\u914D\u7F6E'}</h5>
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2"><label className="text-[11px] text-slate-400 block mb-1">{'\u5BFC\u822A\u65B9\u5F0F'}</label>
              <div className="flex gap-2">
                {([{ v: 'url' as const, l: '\u76F4\u63A5 URL', d: '\u8BBF\u95EE\u6307\u5B9A\u8DEF\u5F84\u540E\u622A\u56FE' }, { v: 'menu_click' as const, l: '\u83DC\u5355\u5BFC\u822A', d: '\u70B9\u51FB\u83DC\u5355\u540E\u622A\u56FE' }, { v: 'url_then_menu' as const, l: 'URL + \u83DC\u5355', d: '\u5148\u8BBF\u95EE URL \u518D\u70B9\u83DC\u5355' }]).map(o => (
                  <button key={o.v} onClick={() => setSc({ ...sc, navigate_type: o.v })} className={`flex-1 p-2 rounded text-left text-xs ${sc.navigate_type === o.v ? 'bg-cyan-500/20 border border-cyan-500/30 text-cyan-400' : 'bg-slate-800 border border-slate-700 text-slate-400 hover:border-slate-600'}`}>
                    <span className="font-medium">{o.l}</span><p className="text-[10px] text-slate-500 mt-0.5">{o.d}</p>
                  </button>
                ))}
              </div>
            </div>
            {(sc.navigate_type === 'url' || sc.navigate_type === 'url_then_menu') && (
              <div className="col-span-2"><label className="text-[11px] text-slate-400 block mb-1">{'\u76EE\u6807 URL \u8DEF\u5F84'}</label><input value={sc.target_url} onChange={e => setSc({ ...sc, target_url: e.target.value })} placeholder={'\u4F8B: /ui/#/system/status \u6216 /admin/monitor'} className="input-field font-mono" /></div>
            )}
            {(sc.navigate_type === 'menu_click' || sc.navigate_type === 'url_then_menu') && (
              <div className="col-span-2">
                <label className="text-[11px] text-slate-400 block mb-1">{'\u83DC\u5355\u70B9\u51FB\u8DEF\u5F84 (\u6309\u987A\u5E8F\uFF0C\u591A\u7EA7\u83DC\u5355\u7528\u9017\u53F7\u5206\u9694)'}</label>
                <input value={sc.menu_path.join(', ')} onChange={e => setSc({ ...sc, menu_path: e.target.value.split(',').map(s => s.trim()) })} placeholder={'\u4F8B: \u7CFB\u7EDF\u7BA1\u7406, \u7CFB\u7EDF\u72B6\u6001, \u6027\u80FD\u76D1\u63A7'} className="input-field" />
                <p className="text-[10px] text-slate-500 mt-1">{'\u652F\u6301 CSS \u9009\u62E9\u5668\u6216\u83DC\u5355\u6587\u672C\uFF0C\u4F8B: #menu-system, .submenu-status, a[data-page="monitor"]'}</p>
              </div>
            )}
            <div><label className="text-[11px] text-slate-400 block mb-1">{'\u7B49\u5F85\u5143\u7D20\u51FA\u73B0 (CSS \u9009\u62E9\u5668)'}</label><input value={sc.wait_selector} onChange={e => setSc({ ...sc, wait_selector: e.target.value })} placeholder={'\u4F8B: .dashboard-loaded, #main-content'} className="input-field font-mono" /></div>
            <div><label className="text-[11px] text-slate-400 block mb-1">{'\u7B49\u5F85\u8D85\u65F6 (ms)'}</label><input type="number" value={sc.wait_timeout} onChange={e => setSc({ ...sc, wait_timeout: parseInt(e.target.value) || 5000 })} className="input-field" /></div>
            <div><label className="text-[11px] text-slate-400 block mb-1">{'\u622A\u56FE\u533A\u57DF'}</label>
              <select value={sc.capture_area} onChange={e => setSc({ ...sc, capture_area: e.target.value as ScreenshotConfig['capture_area'] })} className="input-field">
                <option value="full_page">{'\u5168\u9875\u622A\u56FE'}</option><option value="viewport">{'\u53EF\u89C6\u533A\u57DF'}</option><option value="element">{'\u6307\u5B9A\u5143\u7D20'}</option>
              </select>
            </div>
            {sc.capture_area === 'element' && (
              <div><label className="text-[11px] text-slate-400 block mb-1">{'\u5143\u7D20 CSS \u9009\u62E9\u5668'}</label><input value={sc.capture_selector} onChange={e => setSc({ ...sc, capture_selector: e.target.value })} placeholder={'\u4F8B: #dashboard-chart, .status-panel'} className="input-field font-mono" /></div>
            )}
          </div>
          <div className="pt-2 border-t border-slate-700/50">
            <h6 className="text-[11px] font-medium text-amber-400 flex items-center gap-1.5 mb-2"><FileText size={12} />{'Word \u62A5\u544A\u6A21\u677F\u6620\u5C04'}</h6>
            <div className="grid grid-cols-2 gap-3">
              <div><label className="text-[11px] text-slate-400 block mb-1">{'\u6A21\u677F\u5360\u4F4D\u7B26 Key'}</label><input value={sc.word_template_key} onChange={e => setSc({ ...sc, word_template_key: e.target.value })} placeholder={'\u4F8B: {{screenshot_system_status}}'} className="input-field font-mono" /></div>
              <div><label className="text-[11px] text-slate-400 block mb-1">{'\u62A5\u544A\u7AE0\u8287'}</label>
                <select value={sc.word_section} onChange={e => setSc({ ...sc, word_section: e.target.value })} className="input-field">
                  <option value="">{'\u8BF7\u9009\u62E9...'}</option>
                  {['\u6982\u89C8', '\u7CFB\u7EDF\u72B6\u6001', '\u7F51\u7EDC\u914D\u7F6E', '\u5B89\u5168\u7B56\u7565', '\u6027\u80FD\u5206\u6790', '\u95EE\u9898\u6C47\u603B', '\u9644\u5F55'].map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div><label className="text-[11px] text-slate-400 block mb-1">{'\u7AE0\u8287\u5185\u4F4D\u7F6E\u5E8F\u53F7'}</label><input type="number" value={sc.word_position} onChange={e => setSc({ ...sc, word_position: parseInt(e.target.value) || 1 })} className="input-field" /></div>
              <div><label className="text-[11px] text-slate-400 block mb-1">{'\u56FE\u7247\u5BBD\u5EA6 (mm)'}</label><input type="number" value={sc.image_width_mm} onChange={e => setSc({ ...sc, image_width_mm: parseInt(e.target.value) || 160 })} className="input-field" /></div>
            </div>
            <p className="text-[10px] text-slate-500 mt-2">{'\u622A\u56FE\u5C06\u81EA\u52A8\u63D2\u5165\u5230 Word \u62A5\u544A\u6A21\u677F\u4E2D\u5BF9\u5E94\u7684\u5360\u4F4D\u7B26\u4F4D\u7F6E\u3002\u5360\u4F4D\u7B26\u683C\u5F0F: {{key}}\uFF0C\u9700\u5728 Word \u6A21\u677F\u4E2D\u9884\u5148\u653E\u7F6E\u3002'}</p>
          </div>
        </div>
      )}
      {!isScreenshot && (
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer"><input type="checkbox" checked={f.is_read_only} onChange={e => setF({ ...f, is_read_only: e.target.checked })} className="rounded border-slate-600" />{'\u53EA\u8BFB\u64CD\u4F5C'}</label>
          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer"><input type="checkbox" checked={f.has_threshold} onChange={e => setF({ ...f, has_threshold: e.target.checked })} className="rounded border-slate-600" />{'\u542F\u7528\u9608\u503C'}</label>
          {f.has_threshold && (<><div className="flex items-center gap-1"><span className="text-[11px] text-slate-400">Warning:</span><input type="number" value={f.threshold_warn} onChange={e => setF({ ...f, threshold_warn: parseInt(e.target.value) || 0 })} className="input-field w-20" /></div><div className="flex items-center gap-1"><span className="text-[11px] text-slate-400">Critical:</span><input type="number" value={f.threshold_crit} onChange={e => setF({ ...f, threshold_crit: parseInt(e.target.value) || 0 })} className="input-field w-20" /></div></>)}
        </div>
      )}
      <div className="flex justify-end gap-2"><button onClick={onDone} className="px-3 py-1.5 rounded text-xs bg-slate-700 text-slate-300 hover:bg-slate-600">{'\u53D6\u6D88'}</button><button onClick={submit} className="px-3 py-1.5 rounded text-xs bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30">{'\u6DFB\u52A0'}</button></div>
    </div>
  );
}

function LogsTab({ logs }: { logs: ExecutionLog[] }) {
  const sc = { running: 'bg-cyan-500/20 text-cyan-400', completed: 'bg-green-500/20 text-green-400', failed: 'bg-red-500/20 text-red-400', partial: 'bg-amber-500/20 text-amber-400' };
  const sl = { running: '\u6267\u884C\u4E2D', completed: '\u5DF2\u5B8C\u6210', failed: '\u5931\u8D25', partial: '\u90E8\u5206\u5B8C\u6210' };
  return (
    <div className="max-w-3xl">
      <h3 className="text-sm font-medium text-slate-200 mb-3">{'\u6267\u884C\u65E5\u5FD7'}</h3>
      {logs.length === 0 ? (
        <div className="p-8 text-center border border-dashed border-slate-700 rounded"><Activity size={32} className="mx-auto text-slate-600 mb-2" /><p className="text-xs text-slate-500">{'\u6682\u65E0\u6267\u884C\u8BB0\u5F55'}</p></div>
      ) : (
        <div className="space-y-2">{logs.map(log => (
          <div key={log.id} className="p-3 rounded border border-slate-700 bg-slate-800/30">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2"><span className={`text-[11px] px-2 py-0.5 rounded ${sc[log.status]}`}>{sl[log.status]}</span><span className="text-xs text-slate-300">{log.device_name}</span></div>
              <span className="text-[11px] text-slate-500">{new Date(log.started_at).toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-4 text-[11px]">
              <span className="text-slate-400">{log.completed_items}/{log.total_items} {'\u9879'}</span>
              <span className="text-green-400">OK:{log.ok_count}</span>
              <span className="text-amber-400">Warn:{log.warning_count}</span>
              <span className="text-red-400">Crit:{log.critical_count}</span>
              <span className="text-red-500">Err:{log.error_count}</span>
            </div>
            {log.cert_warning && <div className="mt-2 flex items-center gap-1.5 text-[11px] text-amber-400"><AlertTriangle size={12} />{log.cert_warning}</div>}
          </div>
        ))}</div>
      )}
    </div>
  );
}

function AddDialog({ onClose, onAdd }: { onClose: () => void; onAdd: (d: HTTPDevice) => void }) {
  const [step, setStep] = useState(0);
  const [f, setF] = useState({ name: '', brand: 'huawei_fw', base_url: '', port: 443, use_https: true, auth_type: 'form' as AuthType, username: '', password: '', login_url: '/api/v1/sys/user/login', tls_min: 'TLSv1.2' as TLSVersion, tls_max: 'TLSv1.3' as TLSVersion, verify_cert: true, accept_self_signed: false, compat_mode: false });

  const selectBrand = (b: typeof DEVICE_BRANDS[number]) => {
    setF({ ...f, brand: b.value, port: b.defaultPort, auth_type: b.authType, login_url: b.loginUrl, compat_mode: b.value === 'legacy' });
    setStep(1);
  };

  const submit = async () => {
    if (!f.name || !f.base_url) return;
    const r = await fetch('/api/v1/http-integration/devices', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: f.name, brand: f.brand, model: DEVICE_BRANDS.find(b => b.value === f.brand)?.label || '', base_url: f.base_url, port: f.port, use_https: f.use_https, auth_type: f.auth_type, username: f.username, password_enc: f.password, login_url: f.login_url, tls_min_version: f.tls_min, tls_max_version: f.tls_max, verify_cert: f.verify_cert, accept_self_signed: f.accept_self_signed, compat_mode: f.compat_mode, custom_headers: {}, cipher_suites: [], timeout: 30, tags: [] }) });
    if (r.ok) { const d = await r.json(); onAdd(d); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div className="w-[600px] max-h-[80vh] bg-slate-900 border border-slate-700 rounded-lg shadow-2xl flex flex-col" onClick={e => e.stopPropagation()}>
        <div className="px-4 py-3 border-b border-slate-700 flex items-center justify-between">
          <div className="flex items-center gap-2"><Globe size={16} className="text-cyan-400" /><h3 className="text-sm font-semibold text-slate-200">{'\u6DFB\u52A0 HTTP \u8BBE\u5907'}</h3></div>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300"><XCircle size={16} /></button>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {step === 0 ? (
            <div>
              <p className="text-xs text-slate-400 mb-3">{'\u9009\u62E9\u8BBE\u5907\u54C1\u724C\uFF0C\u7CFB\u7EDF\u5C06\u81EA\u52A8\u586B\u5145\u9ED8\u8BA4\u914D\u7F6E'}</p>
              <div className="grid grid-cols-2 gap-2">
                {DEVICE_BRANDS.map(b => (
                  <button key={b.value} onClick={() => selectBrand(b)} className="p-3 rounded border border-slate-700 bg-slate-800/50 hover:border-cyan-500/30 hover:bg-slate-800 text-left transition-colors group">
                    <div className="flex items-center gap-2"><span className="text-lg">{b.icon}</span><span className="text-xs font-medium text-slate-200 group-hover:text-cyan-400">{b.label}</span></div>
                    <p className="text-[10px] text-slate-500 mt-1">Port:{b.defaultPort} | {AUTH_CFG[b.authType].label}</p>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div><label className="text-[11px] text-slate-400 block mb-1">{'\u8BBE\u5907\u540D\u79F0'}</label><input value={f.name} onChange={e => setF({ ...f, name: e.target.value })} placeholder={'\u4F8B: \u603B\u90E8\u9632\u706B\u5899-USG6000'} className="input-field" /></div>
                <div><label className="text-[11px] text-slate-400 block mb-1">{'\u54C1\u724C'}</label>
                  <select value={f.brand} onChange={e => { const b = DEVICE_BRANDS.find(x => x.value === e.target.value); if (b) setF({ ...f, brand: b.value, port: b.defaultPort, auth_type: b.authType, login_url: b.loginUrl }); }} className="input-field">
                    {DEVICE_BRANDS.map(b => <option key={b.value} value={b.value}>{b.icon} {b.label}</option>)}
                  </select>
                </div>
                <div><label className="text-[11px] text-slate-400 block mb-1">{'\u4E3B\u673A\u5730\u5740'}</label><input value={f.base_url} onChange={e => setF({ ...f, base_url: e.target.value })} placeholder="10.0.1.254" className="input-field" /></div>
                <div><label className="text-[11px] text-slate-400 block mb-1">{'\u7AEF\u53E3'}</label><input type="number" value={f.port} onChange={e => setF({ ...f, port: parseInt(e.target.value) || 443 })} className="input-field" /></div>
              </div>
              <div className="flex gap-2">
                <button onClick={() => setF({ ...f, use_https: true })} className={`flex-1 py-1.5 rounded text-xs font-medium ${f.use_https ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-slate-800 text-slate-400 border border-slate-600'}`}><Lock size={12} className="inline mr-1" />HTTPS</button>
                <button onClick={() => setF({ ...f, use_https: false })} className={`flex-1 py-1.5 rounded text-xs font-medium ${!f.use_https ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-slate-800 text-slate-400 border border-slate-600'}`}><Unlock size={12} className="inline mr-1" />HTTP</button>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div><label className="text-[11px] text-slate-400 block mb-1">{'\u7528\u6237\u540D'}</label><input value={f.username} onChange={e => setF({ ...f, username: e.target.value })} className="input-field" /></div>
                <div><label className="text-[11px] text-slate-400 block mb-1">{'\u5BC6\u7801'}</label><input type="password" value={f.password} onChange={e => setF({ ...f, password: e.target.value })} className="input-field" /></div>
              </div>
              <div><label className="text-[11px] text-slate-400 block mb-1">{'\u767B\u5F55 URL \u8DEF\u5F84'}</label><input value={f.login_url} onChange={e => setF({ ...f, login_url: e.target.value })} className="input-field font-mono" /></div>
              <div className="grid grid-cols-2 gap-3">
                <div><label className="text-[11px] text-slate-400 block mb-1">{'\u6700\u4F4E TLS'}</label>
                  <select value={f.tls_min} onChange={e => { const v = e.target.value as TLSVersion; setF({ ...f, tls_min: v, compat_mode: v === 'TLSv1.0' || v === 'TLSv1.1' }); }} className="input-field">
                    {TLS_V.map(v => <option key={v} value={v}>{v}</option>)}
                  </select>
                </div>
                <div><label className="text-[11px] text-slate-400 block mb-1">{'\u6700\u9AD8 TLS'}</label>
                  <select value={f.tls_max} onChange={e => setF({ ...f, tls_max: e.target.value as TLSVersion })} className="input-field">
                    {TLS_V.map(v => <option key={v} value={v}>{v}</option>)}
                  </select>
                </div>
              </div>
              <div className="flex flex-wrap gap-3">
                <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer"><input type="checkbox" checked={f.verify_cert} onChange={e => setF({ ...f, verify_cert: e.target.checked })} className="rounded border-slate-600" />{'\u9A8C\u8BC1\u8BC1\u4E66'}</label>
                <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer"><input type="checkbox" checked={f.accept_self_signed} onChange={e => setF({ ...f, accept_self_signed: e.target.checked })} className="rounded border-slate-600" />{'\u63A5\u53D7\u81EA\u7B7E\u540D'}</label>
              </div>
              {f.compat_mode && (
                <div className="p-3 rounded border border-amber-500/30 bg-amber-500/5 flex items-start gap-2">
                  <AlertTriangle size={14} className="text-amber-400 shrink-0 mt-0.5" />
                  <p className="text-[11px] text-amber-400">{'\u517C\u5BB9\u6A21\u5F0F\u5DF2\u542F\u7528\uFF0C\u5C06\u4F7F\u7528\u8F83\u5F31\u7684 TLS \u914D\u7F6E\u4E0E\u8001\u8BBE\u5907\u901A\u4FE1\u3002\u4EC5\u5EFA\u8BAE\u5185\u7F51\u73AF\u5883\u4F7F\u7528\u3002'}</p>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="px-4 py-3 border-t border-slate-700 flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-1.5 rounded text-xs bg-slate-700 text-slate-300 hover:bg-slate-600">{'\u53D6\u6D88'}</button>
          {step === 1 && <button onClick={() => setStep(0)} className="px-4 py-1.5 rounded text-xs bg-slate-700 text-slate-300 hover:bg-slate-600">{'\u8FD4\u56DE'}</button>}
          {step === 0 ? null : <button onClick={submit} disabled={!f.name || !f.base_url} className="px-4 py-1.5 rounded text-xs bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 disabled:opacity-50">{'\u6DFB\u52A0\u8BBE\u5907'}</button>}
        </div>
      </div>
    </div>
  );
}

function CertUpDialog({ deviceId, deviceName, onClose, onUpload }: { deviceId: string; deviceName: string; onClose: () => void; onUpload: () => void }) {
  const [f, setF] = useState({ cert_pem: '', trusted: true, note: '' });
  const submit = async () => {
    if (!f.cert_pem) return;
    await fetch('/api/v1/http-integration/certs', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ device_id: deviceId, device_name: deviceName, cert_pem: f.cert_pem, trusted: f.trusted }) });
    onUpload(); onClose();
  };
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div className="w-[500px] bg-slate-900 border border-slate-700 rounded-lg shadow-2xl" onClick={e => e.stopPropagation()}>
        <div className="px-4 py-3 border-b border-slate-700 flex items-center justify-between">
          <div className="flex items-center gap-2"><FileKey size={16} className="text-blue-400" /><h3 className="text-sm font-semibold text-slate-200">{'\u5BFC\u5165 SSL \u8BC1\u4E66'}</h3></div>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300"><XCircle size={16} /></button>
        </div>
        <div className="p-4 space-y-3">
          <p className="text-xs text-slate-400">{'\u4E3A'} <strong className="text-slate-200">{deviceName}</strong> {'\u5BFC\u5165\u8BC1\u4E66\uFF0C\u652F\u6301 PEM/DER/CER \u683C\u5F0F'}</p>
          <div><label className="text-[11px] text-slate-400 block mb-1">{'\u8BC1\u4E66\u5185\u5BB9 (PEM \u683C\u5F0F)'}</label>
            <textarea value={f.cert_pem} onChange={e => setF({ ...f, cert_pem: e.target.value })} rows={8} placeholder="-----BEGIN CERTIFICATE-----&#10;MIIDXTCCAkWgAwIBAgIJAJC1HiIAZAiU...&#10;-----END CERTIFICATE-----" className="input-field font-mono text-[11px] resize-none" />
          </div>
          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer"><input type="checkbox" checked={f.trusted} onChange={e => setF({ ...f, trusted: e.target.checked })} className="rounded border-slate-600" />{'\u8BBE\u4E3A\u53D7\u4FE1\u4EFB\u8BC1\u4E66'}</label>
          <div className="p-3 rounded bg-slate-800/50 border border-slate-700">
            <p className="text-[11px] text-slate-400 font-medium mb-1">{'\u8BF4\u660E'}</p>
            <ul className="text-[10px] text-slate-500 space-y-0.5">
              <li>{'\u2022 \u5BFC\u5165\u7684\u8BC1\u4E66\u5C06\u88AB\u6DFB\u52A0\u5230\u7CFB\u7EDF\u4FE1\u4EFB\u5B58\u50A8\u4E2D'}</li>
              <li>{'\u2022 \u81EA\u7B7E\u540D\u8BC1\u4E66\u9700\u52FE\u9009\u201C\u53D7\u4FE1\u4EFB\u201D\u624D\u80FD\u901A\u8FC7\u8FDE\u63A5\u6D4B\u8BD5'}</li>
              <li>{'\u2022 \u652F\u6301\u5BFC\u5165 CA \u8BC1\u4E66\uFF0C\u8BE5 CA \u7B7E\u53D1\u7684\u6240\u6709\u8BC1\u4E66\u90FD\u5C06\u88AB\u4FE1\u4EFB'}</li>
              <li>{'\u2022 \u5BF9\u4E8E\u8001\u8BBE\u5907\uFF0C\u8BF7\u786E\u4FDD\u517C\u5BB9\u6A21\u5F0F\u5DF2\u542F\u7528'}</li>
            </ul>
          </div>
        </div>
        <div className="px-4 py-3 border-t border-slate-700 flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-1.5 rounded text-xs bg-slate-700 text-slate-300 hover:bg-slate-600">{'\u53D6\u6D88'}</button>
          <button onClick={submit} disabled={!f.cert_pem} className="px-4 py-1.5 rounded text-xs bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 disabled:opacity-50">{'\u5BFC\u5165\u8BC1\u4E66'}</button>
        </div>
      </div>
    </div>
  );
}

function ScreenshotsTab({ screenshots, onPreview, onCapture }: { screenshots: Screenshot[]; onPreview: (s: Screenshot) => void; onCapture: () => void }) {
  const [capturing, setCapturing] = useState(false);
  const handleCapture = async () => {
    setCapturing(true);
    await onCapture();
    setCapturing(false);
  };
  return (
    <div className="max-w-4xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-slate-200">{'\u622A\u56FE\u5DE1\u68C0'}</h3>
          <p className="text-[11px] text-slate-500 mt-0.5">{'\u901A\u8FC7 Headless Browser \u767B\u5F55\u540E\u622A\u53D6\u8BBE\u5907 Web \u7BA1\u7406\u754C\u9762\uFF0C\u4F5C\u4E3A\u5DE1\u68C0\u8BC1\u636E\u5B58\u6863'}</p>
        </div>
        <button onClick={handleCapture} disabled={capturing} className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 disabled:opacity-50">
          {capturing ? <RefreshCw size={12} className="animate-spin" /> : <Camera size={12} />}
          {capturing ? '\u622A\u56FE\u4E2D...' : '\u7ACB\u5373\u622A\u56FE'}
        </button>
      </div>

      {capturing && (
        <div className="p-4 rounded-lg border border-cyan-500/20 bg-cyan-500/5">
          <div className="flex items-center gap-3">
            <RefreshCw size={18} className="text-cyan-400 animate-spin" />
            <div>
              <p className="text-xs text-cyan-400 font-medium">{'\u6B63\u5728\u622A\u56FE...'}</p>
              <div className="mt-1.5 flex items-center gap-2 text-[11px] text-slate-400">
                <span className="flex items-center gap-1"><Lock size={10} className="text-green-400" />{'\u767B\u5F55\u8BA4\u8BC1'}</span>
                <span>{'\u2192'}</span>
                <span className="flex items-center gap-1"><Camera size={10} className="text-cyan-400 animate-pulse" />{'\u622A\u53D6\u9875\u9762'}</span>
                <span>{'\u2192'}</span>
                <span className="flex items-center gap-1"><ImageIcon size={10} className="text-slate-500" />{'\u5B58\u50A8\u5F52\u6863'}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="p-3 rounded border border-slate-700 bg-slate-800/30">
        <h4 className="text-[11px] font-medium text-slate-400 mb-2 flex items-center gap-1.5"><Camera size={12} />{'\u622A\u56FE\u5DE1\u68C0\u6D41\u7A0B\u8BF4\u660E'}</h4>
        <div className="grid grid-cols-4 gap-2 text-[10px]">
          {[{ step: '1', title: '\u767B\u5F55\u8BA4\u8BC1', desc: '\u4F7F\u7528\u4FDD\u5B58\u7684\u51ED\u636E\u81EA\u52A8\u767B\u5F55', icon: <Key size={12} className="text-cyan-400" /> },
            { step: '2', title: '\u5BFC\u822A\u76EE\u6807\u9875', desc: '\u8BBF\u95EE\u6307\u5B9A URL \u8DEF\u5F84', icon: <Globe size={12} className="text-blue-400" /> },
            { step: '3', title: '\u622A\u53D6\u9875\u9762', desc: '\u5168\u9875/\u533A\u57DF\u622A\u56FE', icon: <Camera size={12} className="text-green-400" /> },
            { step: '4', title: '\u5B58\u50A8\u5F52\u6863', desc: '\u5173\u8054\u5DE1\u68C0\u62A5\u544A', icon: <FileText size={12} className="text-amber-400" /> }
          ].map(s => (
            <div key={s.step} className="p-2 rounded bg-slate-800/50 border border-slate-700/50">
              <div className="flex items-center gap-1.5 mb-1">{s.icon}<span className="font-medium text-slate-300">{s.title}</span></div>
              <p className="text-slate-500">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {screenshots.length === 0 ? (
        <div className="p-8 text-center border border-dashed border-slate-700 rounded">
          <Camera size={32} className="mx-auto text-slate-600 mb-2" />
          <p className="text-xs text-slate-500">{'\u6682\u65E0\u622A\u56FE\u8BB0\u5F55'}</p>
          <p className="text-[11px] text-slate-600 mt-1">{'\u70B9\u51FB\u201C\u7ACB\u5373\u622A\u56FE\u201D\u5F00\u59CB\u91C7\u96C6'}</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3">
          {screenshots.map(s => (
            <div key={s.id} className="rounded border border-slate-700 bg-slate-800/30 overflow-hidden group">
              <div className="relative aspect-video bg-slate-900 flex items-center justify-center cursor-pointer" onClick={() => s.status === 'success' && onPreview(s)}>
                {s.status === 'success' ? (
                  <>
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end justify-center pb-2">
                      <div className="flex items-center gap-2">
                        <span className="p-1.5 rounded bg-slate-800/80 text-slate-200"><Maximize2 size={12} /></span>
                        <span className="p-1.5 rounded bg-slate-800/80 text-slate-200"><Download size={12} /></span>
                      </div>
                    </div>
                    <div className="text-center">
                      <ImageIcon size={24} className="mx-auto text-slate-600 mb-1" />
                      <span className="text-[10px] text-slate-500 font-mono">{s.width}x{s.height}</span>
                    </div>
                    {s.login_page && <span className="absolute top-1.5 left-1.5 text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">{'\u767B\u5F55\u9875'}</span>}
                  </>
                ) : s.status === 'failed' ? (
                  <div className="text-center"><XCircle size={20} className="mx-auto text-red-400 mb-1" /><span className="text-[10px] text-red-400">{'\u622A\u56FE\u5931\u8D25'}</span></div>
                ) : (
                  <div className="text-center"><Clock size={20} className="mx-auto text-slate-500 mb-1" /><span className="text-[10px] text-slate-500">{'\u5F85\u622A\u53D6'}</span></div>
                )}
              </div>
              <div className="p-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-200 truncate">{s.item_name}</span>
                  <span className={`text-[10px] ${s.status === 'success' ? 'text-green-400' : s.status === 'failed' ? 'text-red-400' : 'text-slate-500'}`}>
                    {s.status === 'success' ? '\u6210\u529F' : s.status === 'failed' ? '\u5931\u8D25' : '\u5F85\u622A\u53D6'}
                  </span>
                </div>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-[10px] text-slate-500 font-mono truncate max-w-[180px]">{s.url}</span>
                  <span className="text-[10px] text-slate-500">{new Date(s.captured_at).toLocaleString()}</span>
                </div>
                {s.error_message && <p className="text-[10px] text-red-400 mt-1">{s.error_message}</p>}
                {s.status === 'success' && <p className="text-[10px] text-slate-500 mt-1">{(s.file_size / 1024).toFixed(1)} KB | {s.width}x{s.height}</p>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ScreenshotPreview({ screenshot, onClose }: { screenshot: Screenshot; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80" onClick={onClose}>
      <div className="max-w-4xl w-full mx-4 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl" onClick={e => e.stopPropagation()}>
        <div className="px-4 py-3 border-b border-slate-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Camera size={16} className="text-cyan-400" />
            <h3 className="text-sm font-semibold text-slate-200">{screenshot.item_name}</h3>
            <span className="text-[11px] text-slate-500 font-mono">{screenshot.url}</span>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300"><XCircle size={16} /></button>
        </div>
        <div className="p-4">
          <div className="aspect-video bg-slate-950 rounded flex items-center justify-center border border-slate-700">
            <div className="text-center">
              <ImageIcon size={48} className="mx-auto text-slate-600 mb-2" />
              <p className="text-sm text-slate-400">{screenshot.width} x {screenshot.height}</p>
              <p className="text-[11px] text-slate-500 mt-1">{'\u622A\u56FE\u6587\u4EF6'}: {(screenshot.file_size / 1024).toFixed(1)} KB</p>
              <p className="text-[11px] text-slate-500 mt-0.5">{'\u622A\u53D6\u65F6\u95F4'}: {new Date(screenshot.captured_at).toLocaleString()}</p>
            </div>
          </div>
          <div className="mt-3 flex items-center justify-between">
            <div className="flex items-center gap-3 text-[11px] text-slate-400">
              <span>{'\u8BBE\u5907'}: {screenshot.device_name}</span>
              {screenshot.login_page && <span className="text-cyan-400">{'\u767B\u5F55\u9875\u622A\u56FE'}</span>}
              {screenshot.full_page && <span className="text-green-400">{'\u5168\u9875\u622A\u56FE'}</span>}
            </div>
            <button className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs bg-slate-700 text-slate-200 hover:bg-slate-600"><Download size={12} />{'\u4E0B\u8F7D\u539F\u56FE'}</button>
          </div>
        </div>
      </div>
    </div>
  );
}

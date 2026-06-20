'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, Monitor, FileText, ListChecks, FileBarChart,
  BookOpen, Settings, ChevronDown, ChevronRight, Shield,
  Server, Network, Database, HardDrive, Cpu,
} from 'lucide-react';
import { useState } from 'react';

interface NavItem {
  label: string;
  icon: React.ReactNode;
  path: string;
  badge?: string;
  badgeColor?: string;
}

interface NavGroup {
  label: string;
  icon: React.ReactNode;
  children?: NavItem[];
  path?: string;
  badge?: string;
  badgeColor?: string;
}

const navGroups: NavGroup[] = [
  {
    label: '总览仪表盘', icon: <LayoutDashboard size={18} />,
    path: '/',
  },
  {
    label: '巡检管理', icon: <ListChecks size={18} />,
    children: [
      { label: '巡检对象', path: '/targets', icon: <Monitor size={16} /> },
      { label: '巡检模板', path: '/templates', icon: <FileText size={16} /> },
      { label: '巡检任务', path: '/tasks', icon: <ListChecks size={16} /> },
    ],
  },
  {
    label: '巡检报告', icon: <FileBarChart size={18} />,
    path: '/reports',
  },
  {
    label: '巡检知识库', icon: <BookOpen size={18} />,
    path: '/knowledge',
  },
  {
    label: '系统设置', icon: <Settings size={18} />,
    path: '/settings',
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [expandedGroups, setExpandedGroups] = useState<string[]>(['巡检管理']);

  const toggleGroup = (label: string) => {
    setExpandedGroups(prev =>
      prev.includes(label) ? prev.filter(g => g !== label) : [...prev, label]
    );
  };

  const isActive = (path: string) => {
    if (path === '/') return pathname === '/';
    return pathname.startsWith(path);
  };

  return (
    <aside className="w-60 bg-slate-900 border-r border-slate-700 flex flex-col h-screen overflow-y-auto shrink-0">
      <div className="p-4 border-b border-slate-700">
        <h1 className="text-lg font-bold text-cyan-400 flex items-center gap-2">
          <Shield size={22} /> Acdante
        </h1>
        <p className="text-xs text-slate-400 mt-1">IT运维巡检平台 v1.0</p>
      </div>

      <nav className="flex-1 p-2 space-y-0.5">
        {navGroups.map(group => (
          <div key={group.label}>
            {group.path ? (
              <Link
                href={group.path}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                  isActive(group.path) ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-300 hover:bg-slate-800'
                }`}
              >
                {group.icon}
                <span className="flex-1">{group.label}</span>
                {group.badge && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${group.badgeColor || 'bg-slate-700 text-slate-400'}`}>
                    {group.badge}
                  </span>
                )}
              </Link>
            ) : (
              <>
                <button
                  onClick={() => toggleGroup(group.label)}
                  className="flex items-center gap-3 px-3 py-2 w-full text-sm text-slate-400 hover:text-slate-200 transition-colors"
                >
                  {group.icon}
                  <span className="flex-1 text-left">{group.label}</span>
                  {expandedGroups.includes(group.label) ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </button>
                {expandedGroups.includes(group.label) && group.children && (
                  <div className="ml-4 space-y-0.5">
                    {group.children.map(child => (
                      <Link
                        key={child.path}
                        href={child.path}
                        className={`flex items-center gap-3 px-3 py-1.5 rounded-md text-sm transition-colors ${
                          isActive(child.path) ? 'bg-cyan-500/20 text-cyan-400' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                        }`}
                      >
                        {child.icon}
                        <span className="flex-1">{child.label}</span>
                        {child.badge && (
                          <span className={`text-[10px] px-1.5 py-0.5 rounded ${child.badgeColor || 'bg-slate-700 text-slate-400'}`}>
                            {child.badge}
                          </span>
                        )}
                      </Link>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-700">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 text-xs font-bold">A</div>
          <div>
            <p className="text-sm text-slate-200">Admin</p>
            <p className="text-xs text-slate-500">系统管理员</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

import type { Metadata } from 'next';
import './globals.css';
import AppShell from '@/components/layout/app-shell';

export const metadata: Metadata = {
  title: 'Acdante ITOps Inspection Platform',
  description: 'IT运维巡检平台 - 多协议、多对象自动化巡检系统',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" className="dark">
      <body className="font-sans antialiased">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}

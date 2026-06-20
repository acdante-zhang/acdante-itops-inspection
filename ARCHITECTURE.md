# Architecture Design / 架构设计说明

[English](#english) | [中文](#中文)

---

<a id="english"></a>

## System Architecture

### Overview

Acdante ITOps Inspection Platform adopts a modern web architecture with Next.js as the frontend framework and API layer, designed for seamless transition to a microservices architecture in production.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser (Client)                         │
│                    React 19 + Next.js 16 App                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Next.js Application (5000)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Pages     │  │ Components  │  │    API Routes (/api)    │ │
│  │  (React)    │  │  (shadcn)   │  │   (Mock Backend)        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   SQLite DB     │ │  Local Storage  │ │  External APIs  │
│   (Dev Mode)    │ │  (Backups)      │ │  (AI, SMTP)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Production Architecture (Target)

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer                            │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Next.js SSR    │ │  Go API Gateway │ │  Static Assets  │
│  (Frontend)     │ │    (8080)       │ │    (CDN)        │
└─────────────────┘ └────────┬────────┘ └─────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Rust Data Engine│ │ Python Workers  │ │  PostgreSQL     │
│    (8081)       │ │  (Collectors)   │ │   Database      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   SSH/SNMP      │ │   JDBC/ODBC     │ │   HTTP/HTTPS    │
│   Connections   │ │   Connections   │ │   Connections   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16 | React framework with App Router |
| React | 19 | UI library |
| TypeScript | 5 | Type safety |
| Tailwind CSS | 4 | Utility-first styling |
| shadcn/ui | - | Component library |
| Radix UI | - | Accessible primitives |
| Lucide React | - | Icon library |
| Recharts | - | Data visualization |

### Backend (Development)

| Technology | Purpose |
|------------|---------|
| Next.js API Routes | Mock backend API |
| SQLite | Development database |
| In-memory storage | Session and cache |

### Backend (Production Target)

| Technology | Purpose |
|------------|---------|
| Go (Gin) | API Gateway, business logic |
| Rust | High-performance data collection |
| Python | SSH/SNMP/JDBC drivers, report generation |
| PostgreSQL | Production database |
| Redis | Caching and session storage |

## Module Design

### 1. Inspection Objects Module

Manages target devices and systems to be inspected.

**Key Features:**
- Multi-protocol connection management
- Device type classification and tagging
- Connection testing and health monitoring
- Offline mode for disconnected devices

**Data Model:**
```typescript
interface InspectionTarget {
  id: string;
  name: string;
  type: TargetType;
  brand: string;
  model: string;
  version: string;
  connection_params: ConnectionParams;
  offline_mode: boolean;
  status: 'active' | 'inactive' | 'error';
  health_score: number;
  last_inspection_at: string;
}
```

### 2. Inspection Templates Module

Defines inspection items and commands for different device types.

**Key Features:**
- Version and brand marking
- Read-only command warnings
- Custom inspection items
- Template inheritance and copying

**Data Model:**
```typescript
interface InspectionTemplate {
  id: string;
  name: string;
  target_type: TargetType;
  brand: string;
  version: string;
  items: InspectionItem[];
  default_timeout: number;
}

interface InspectionItem {
  id: string;
  name: string;
  category: string;
  command: string;
  command_type: 'ssh' | 'snmp' | 'sql' | 'http' | 'redfish';
  is_read_only: boolean;
  timeout: number;
  warning_threshold?: string;
  critical_threshold?: string;
}
```

### 3. Task Scheduling Module

Manages inspection task execution and scheduling.

**Key Features:**
- 7 scheduling cycles (once/minutely/hourly/daily/weekly/monthly/quarterly)
- Custom time points (day of week, day of month, specific time)
- Task status tracking
- Notification policies

**Data Model:**
```typescript
interface InspectionTask {
  id: string;
  name: string;
  template_id: string;
  target_ids: string[];
  schedule_type: ScheduleType;
  schedule_config: ScheduleConfig;
  status: 'pending' | 'running' | 'completed' | 'failed';
  notify_channels: string[];
}
```

### 4. Report Generation Module

Generates comprehensive inspection reports.

**Key Features:**
- Multiple output formats (HTML/DOCX/PDF)
- Composite reports from multiple tasks
- AI-powered analysis
- Customizable report templates

**Data Model:**
```typescript
interface InspectionReport {
  id: string;
  task_id: string;
  target_ids: string[];
  format: 'html' | 'docx' | 'pdf';
  health_score: number;
  total_items: number;
  ok_count: number;
  warning_count: number;
  critical_count: number;
  summary: string;
  ai_analysis?: string;
}
```

### 5. Config Backup Module

Backs up device configurations with version control.

**Key Features:**
- Configuration version comparison
- Multiple storage backends (FTP/NFS/S3/Local)
- Scheduled backup tasks
- Change detection and diff

**Data Model:**
```typescript
interface ConfigBackup {
  id: string;
  target_id: string;
  config_content: string;
  version_tag: string;
  storage_type: 'local' | 'ftp' | 'nfs' | 's3';
  storage_path: string;
  has_diff: boolean;
  diff_summary: string;
}
```

### 6. IP Management Module

Manages IP address allocation and availability.

**Key Features:**
- Network segment visualization
- TCPING/PING detection
- Manual IP marking
- Historical detection records

**Data Model:**
```typescript
interface IPSegment {
  id: string;
  name: string;
  cidr: string;
  description: string;
  gateway: string;
  vlan_id: number;
  ips: IPEntry[];
}

interface IPEntry {
  ip: string;
  status: 'available' | 'used' | 'reserved' | 'unreachable';
  hostname?: string;
  last_seen?: string;
  manual_mark: boolean;
  remark?: string;
}
```

## API Design

### RESTful API Structure

```
/api/v1/
├── health                    # Health check
├── dashboard/stats          # Dashboard statistics
├── targets/                 # Inspection objects
│   ├── GET /                # List targets
│   ├── POST /               # Create target
│   ├── GET /:id             # Get target
│   ├── PUT /:id             # Update target
│   ├── DELETE /:id          # Delete target
│   └── POST /:id/test       # Test connection
├── templates/               # Inspection templates
│   ├── GET /                # List templates
│   ├── POST /               # Create template
│   ├── GET /:id             # Get template
│   ├── PUT /:id             # Update template
│   └── DELETE /:id          # Delete template
├── tasks/                   # Inspection tasks
│   ├── GET /                # List tasks
│   ├── POST /               # Create task
│   ├── POST /:id/run        # Run task
│   └── DELETE /:id          # Delete task
├── reports/                 # Inspection reports
│   ├── GET /                # List reports
│   ├── GET /:id             # Get report
│   ├── POST /generate       # Generate report
│   └── POST /:id/analyze    # AI analysis
├── config-backups/          # Configuration backups
│   ├── GET /                # List backups
│   ├── POST /               # Create backup
│   └── GET /:id/diff        # Compare versions
├── ip-segments/             # IP management
│   ├── GET /                # List segments
│   ├── POST /               # Create segment
│   └── POST /:id/scan       # Scan segment
├── knowledge/               # Knowledge base
│   ├── GET /                # List entries
│   ├── POST /               # Create entry
│   └── PUT /:id             # Update entry
├── users/                   # User management
│   ├── GET /                # List users
│   ├── POST /               # Create user
│   └── PUT /:id             # Update user
├── notification-channels/   # Notification channels
│   ├── GET /                # List channels
│   ├── POST /               # Create channel
│   └── PUT /:id             # Update channel
├── themes/                  # Theme configuration
│   └── GET /                # List themes
└── ai/config                # AI configuration
    ├── GET /                # Get config
    └── PUT /                # Update config
```

## Security Design

### Authentication & Authorization

- Role-based access control (RBAC)
- User scope filtering for data visibility
- API key management for external integrations
- Session management with JWT tokens

### Data Security

- Encrypted credential storage
- Secure connection protocols (SSH/TLS)
- Audit logging for all operations
- Input validation and sanitization

### Network Security

- Webhook signature verification
- Syslog TLS encryption
- IP whitelist support
- Rate limiting

## Deployment

### Development Environment

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Access at http://localhost:5000
```

### Production Deployment

```bash
# Build application
pnpm build

# Start production server
pnpm start
```

### Docker Deployment (Future)

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build
EXPOSE 5000
CMD ["pnpm", "start"]
```

## Performance Considerations

### Frontend Optimization

- React Server Components for reduced client bundle
- Static generation for documentation pages
- Image optimization with Next.js Image component
- Code splitting and lazy loading

### Backend Optimization

- Connection pooling for database access
- Caching layer with Redis
- Async task processing for inspections
- Batch operations for bulk data

### Scalability

- Horizontal scaling with load balancer
- Database read replicas
- CDN for static assets
- Distributed task queue

---

<a id="中文"></a>

## 系统架构

### 概述

Acdante ITOps 巡检平台采用现代化 Web 架构，以 Next.js 作为前端框架和 API 层，设计为可无缝过渡到生产环境的微服务架构。

### 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         浏览器（客户端）                          │
│                    React 19 + Next.js 16 应用                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Next.js 应用 (5000)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   页面      │  │   组件      │  │    API 路由 (/api)      │ │
│  │  (React)    │  │  (shadcn)   │  │   (模拟后端)            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   SQLite 数据库 │ │   本地存储      │ │   外部 API      │
│   (开发模式)    │ │   (备份文件)    │ │   (AI, SMTP)    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 生产架构（目标）

```
┌─────────────────────────────────────────────────────────────────┐
│                         负载均衡器                               │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Next.js SSR    │ │  Go API 网关    │ │   静态资源      │
│  (前端)         │ │    (8080)       │ │    (CDN)        │
└─────────────────┘ └────────┬────────┘ └─────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Rust 数据引擎   │ │ Python Workers  │ │  PostgreSQL     │
│    (8081)       │ │  (采集器)       │ │    数据库       │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   SSH/SNMP      │ │   JDBC/ODBC     │ │   HTTP/HTTPS    │
│    连接         │ │    连接         │ │    连接         │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 技术栈

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Next.js | 16 | React 框架（App Router） |
| React | 19 | UI 库 |
| TypeScript | 5 | 类型安全 |
| Tailwind CSS | 4 | 原子化 CSS |
| shadcn/ui | - | 组件库 |
| Radix UI | - | 无障碍原语 |
| Lucide React | - | 图标库 |
| Recharts | - | 数据可视化 |

### 后端（开发环境）

| 技术 | 用途 |
|------|------|
| Next.js API Routes | 模拟后端 API |
| SQLite | 开发数据库 |
| 内存存储 | 会话和缓存 |

### 后端（生产目标）

| 技术 | 用途 |
|------|------|
| Go (Gin) | API 网关，业务逻辑 |
| Rust | 高性能数据采集 |
| Python | SSH/SNMP/JDBC 驱动，报告生成 |
| PostgreSQL | 生产数据库 |
| Redis | 缓存和会话存储 |

## 模块设计

### 1. 巡检对象模块

管理待巡检的目标设备和系统。

**核心功能：**
- 多协议连接管理
- 设备类型分类和标签
- 连接测试和健康监控
- 离线模式支持

### 2. 巡检模板模块

定义不同设备类型的巡检项和命令。

**核心功能：**
- 版本和品牌标记
- 只读命令警告
- 自定义巡检项
- 模板继承和复制

### 3. 任务调度模块

管理巡检任务执行和调度。

**核心功能：**
- 7种调度周期（一次性/每分钟/每小时/每天/每周/每月/季度）
- 自定义时间点（周几、月几号、具体时间）
- 任务状态跟踪
- 通知策略

### 4. 报告生成模块

生成全面的巡检报告。

**核心功能：**
- 多种输出格式（HTML/DOCX/PDF）
- 多任务综合报告
- AI 智能分析
- 可定制报告模板

### 5. 配置备份模块

备份设备配置并进行版本控制。

**核心功能：**
- 配置版本对比
- 多种存储后端（FTP/NFS/S3/本地）
- 定时备份任务
- 变更检测和差异对比

### 6. IP管理模块

管理 IP 地址分配和可用性。

**核心功能：**
- 网段可视化
- TCPING/PING 探测
- 手动 IP 标记
- 历史探测记录

## API 设计

### RESTful API 结构

```
/api/v1/
├── health                    # 健康检查
├── dashboard/stats          # 仪表盘统计
├── targets/                 # 巡检对象
├── templates/               # 巡检模板
├── tasks/                   # 巡检任务
├── reports/                 # 巡检报告
├── config-backups/          # 配置备份
├── ip-segments/             # IP 管理
├── knowledge/               # 知识库
├── users/                   # 用户管理
├── notification-channels/   # 通知渠道
├── themes/                  # 主题配置
└── ai/config                # AI 配置
```

## 安全设计

### 认证与授权

- 基于角色的访问控制（RBAC）
- 用户范围过滤数据可见性
- 外部集成的 API 密钥管理
- JWT 令牌会话管理

### 数据安全

- 加密凭证存储
- 安全连接协议（SSH/TLS）
- 所有操作的审计日志
- 输入验证和清理

### 网络安全

- Webhook 签名验证
- Syslog TLS 加密
- IP 白名单支持
- 速率限制

## 部署

### 开发环境

```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 访问 http://localhost:5000
```

### 生产部署

```bash
# 构建应用
pnpm build

# 启动生产服务器
pnpm start
```

## 性能优化

### 前端优化

- React Server Components 减少客户端包大小
- 文档页面静态生成
- Next.js Image 组件图片优化
- 代码分割和懒加载

### 后端优化

- 数据库连接池
- Redis 缓存层
- 巡检异步任务处理
- 批量数据操作

### 可扩展性

- 负载均衡器水平扩展
- 数据库读副本
- 静态资源 CDN
- 分布式任务队列

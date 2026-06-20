# Acdante ITOps Inspection Platform

[English](#english) | [中文](#中文)

---

<a id="english"></a>

## Acdante ITOps Inspection Platform

Enterprise-grade IT infrastructure inspection platform supporting multi-protocol, multi-device automated inspection with customizable templates, task scheduling, and comprehensive reporting.

### Features

| Module | Description |
|--------|-------------|
| **Inspection Objects** | 20+ device types, 7 connection protocols (SSH/SNMP/JDBC/IPMI/Redfish/HTTP/Telnet) |
| **Inspection Templates** | 20+ built-in templates with version/brand marking, custom inspection items |
| **Task Scheduling** | 7 scheduling cycles (once/minutely/hourly/daily/weekly/monthly/quarterly), custom time points |
| **Report Generation** | HTML/DOCX/PDF formats, composite reports, AI-powered analysis |
| **Config Backup** | Version comparison, FTP/NFS/S3/local storage, scheduled backups |
| **IP Management** | Network segment visualization, TCPING/PING detection, manual marking, history records |
| **Knowledge Base** | Custom content, pin/bookmark, image support |
| **System Management** | User management, audit logs, 4 notification channels (Email/DingTalk/WeChat/Feishu) |
| **Theme Switching** | 5 built-in themes (Dark Tech/Light Business/Dopamine/Greenfield/Sunset) |
| **AI Analysis** | OpenAI-compatible API, deep analysis and diagnosis |

### Supported Inspection Objects

- **Operating Systems**: Linux, Windows, AIX
- **Network Devices**: Huawei/H3C switches, routers, firewalls, F5 load balancers
- **SAN Switches**: Brocade, Cisco, Huawei, Lenovo OEM
- **Storage**: Huawei OceanStor, EMC, NetApp
- **Databases**: Oracle (11g/12c/19c), MySQL 8.0, PostgreSQL 15, SQL Server
- **BMC**: Dell iDRAC (Redfish), IPMI
- **Virtualization**: VMware ESXi, vCenter, Sangfor HCI, H3C CAS
- **Cloud**: Alibaba Cloud, Tencent Cloud, Huawei Cloud
- **Kubernetes**: Node status, Pod runtime, resource usage

### Tech Stack

```
Frontend:  Next.js 16 + React 19 + TypeScript + Tailwind CSS 4 + shadcn/ui
Backend:   Next.js API Routes (Production: Go + Rust + Python)
Database:  SQLite (Dev) / PostgreSQL (Production)
```

### Quick Start

```bash
# Clone repository
git clone https://github.com/acdante-zhang/acdante-itops-inspection.git
cd acdante-itops-inspection

# Install dependencies
pnpm install

# Start development server
pnpm dev

# Visit http://localhost:5000
```

### Production Deployment

```bash
# Build
pnpm build

# Start production server
pnpm start
```

### Architecture

```
Browser → Next.js (5000) → /api/v1/*
  (Production) → Go API Gateway (8080) → Rust Data Engine (8081)
                                          → Python Driver → SSH/SNMP/JDBC → Target Devices
                                          → Report Engine → DOCX/HTML/PDF
```

### Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Detailed architecture design
- [AGENTS.md](./AGENTS.md) - Development guidelines

### License

Apache License 2.0

---

<a id="中文"></a>

## Acdante ITOps Inspection Platform

企业级IT基础设施巡检平台，支持多协议、多对象自动化巡检，提供可定制的巡检模板、任务调度和全面的报告生成功能。

### 核心功能

| 模块 | 描述 |
|------|------|
| **巡检对象管理** | 20+设备类型，7种连接协议（SSH/SNMP/JDBC/IPMI/Redfish/HTTP/Telnet） |
| **巡检模板引擎** | 20+内置模板，支持版本/品牌标记，自定义巡检项 |
| **巡检任务调度** | 7种调度周期（一次性/每分钟/每小时/每天/每周/每月/季度），自定义时间点 |
| **巡检报告生成** | HTML/DOCX/PDF格式，综合报告整合，AI智能分析 |
| **设备配置备份** | 版本对比，FTP/NFS/S3/本地存储，定时备份 |
| **IP地址管理** | 网段可视化，TCPING/PING探测，手动标记，历史探测记录 |
| **巡检知识库** | 自定义内容，置顶/标记，贴图支持 |
| **系统管理** | 用户管理，审计日志，4种通知渠道（邮件/钉钉/微信/飞书） |
| **主题切换** | 5套主题（深色科技/浅色商务/多巴胺/绿野/日落） |
| **AI智能分析** | OpenAI兼容接口，深度分析和诊断 |

### 支持的巡检对象

- **操作系统**：Linux、Windows、AIX
- **网络设备**：华为/华三交换机、路由器、防火墙、F5负载均衡
- **SAN交换机**：Brocade、Cisco、华为、联想OEM
- **存储设备**：华为OceanStor、EMC、NetApp
- **数据库**：Oracle（11g/12c/19c）、MySQL 8.0、PostgreSQL 15、SQL Server
- **BMC管理**：Dell iDRAC（Redfish）、IPMI
- **虚拟化**：VMware ESXi、vCenter、深信服HCI、华三CAS
- **云平台**：阿里云、腾讯云、华为云
- **K8s集群**：节点状态、Pod运行、资源使用

### 技术栈

```
前端：  Next.js 16 + React 19 + TypeScript + Tailwind CSS 4 + shadcn/ui
后端：  Next.js API Routes（生产环境：Go + Rust + Python）
数据库：SQLite（开发）/ PostgreSQL（生产）
```

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/acdante-zhang/acdante-itops-inspection.git
cd acdante-itops-inspection

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 访问 http://localhost:5000
```

### 生产环境部署

```bash
# 构建
pnpm build

# 启动生产服务器
pnpm start
```

### 系统架构

```
浏览器 → Next.js (5000) → /api/v1/*
  (生产环境) → Go API网关 (8080) → Rust数据引擎 (8081)
                                    → Python驱动 → SSH/SNMP/JDBC → 目标设备
                                    → 报告引擎 → DOCX/HTML/PDF
```

### 文档

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 详细架构设计说明
- [AGENTS.md](./AGENTS.md) - 开发规范

### 开源协议

Apache License 2.0

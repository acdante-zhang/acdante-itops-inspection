# Acdante ITOps Inspection Platform

[English](#english) | [中文](#中文)

---

<a id="english"></a>

## Acdante ITOps Inspection Platform

Enterprise-grade IT infrastructure inspection platform supporting multi-protocol, multi-device automated inspection with customizable templates, task scheduling, and comprehensive reporting.

> **Latest: v3.0.0** — DBCheck Database Engine Integration + SNMP Collection Engine + Full DOCX/PDF Report Generation

---

### 🆕 What's New in v3.0.0

| Feature | Description |
|---------|-------------|
| **DBCheck Database Engine** | Integrated [DBCheck v2.6.0](https://github.com/fiyo/DBCheck) — 10 database types, 130+ YAML rules, 5-dimension health scoring, AI diagnosis |
| **SNMP Collection Engine** | Python-based SNMP v1/v2c/v3 collector with 136 built-in OIDs, 12 device templates (Huawei/H3C/Cisco/Dell/F5/etc.) |
| **DOCX/PDF Reports** | Full DOCX (editable) and PDF report generation with cover page, health dashboard, issue summary, and detailed results |
| **Template Expansion** | 26 built-in inspection templates (12 SNMP + 7 DBCheck + 7 infrastructure) |

### Features

| Module | v1.0 | v3.0 |
|--------|------|------|
| **Inspection Objects** | 20+ device types, 7 protocols | **27+ device types, 8 protocols** (added dbcheck) |
| **Inspection Templates** | 12 built-in templates | **26 built-in templates** (12 SNMP + 7 DBCheck DB + 7 infra) |
| **Database Inspection** | 4 DB types, 5-10 items each | **10 DB types, 50-130+ items each** (DBCheck powered) |
| **SNMP Monitoring** | Basic SNMP support | **Full SNMP engine**, 136 OIDs, 12 vendor templates |
| **Report Generation** | HTML only | **DOCX + PDF + HTML**, editable Word reports |
| **Task Scheduling** | 7 scheduling cycles | 7 cycles + DBCheck integration |
| **Rule Engine** | Simple thresholds | **YAML rule engine** (130+ rules) + safe sandbox |
| **Health Scoring** | Simple weighted | **5-dimension scoring** (performance/security/config/capacity/availability) |

### Supported Inspection Objects

- **Operating Systems**: Linux, Windows, AIX
- **Network Devices**: Huawei/H3C switches, routers, firewalls, F5 load balancers
- **SAN Switches**: Brocade, Cisco, Huawei, Lenovo OEM
- **Storage**: Huawei OceanStor, EMC, NetApp
- **Databases**: Oracle (11g/12c/19c/21c), MySQL 5.7/8.0/8.4, PostgreSQL 12-16, SQL Server 2016-2022
- **Domestic Databases**: 达梦 DM8, TiDB, KingbaseES, GBase 8s, IvorySQL, YashanDB (DBCheck powered)
- **BMC**: Dell iDRAC (Redfish), IPMI
- **Security**: 深信服, Checkpoint, Cisco ASA, Huawei USG
- **Kubernetes**: Node status, Pod runtime, resource usage

### Tech Stack

```
Frontend:  Next.js 16 + React 19 + TypeScript + Tailwind CSS 4 + shadcn/ui
Backend:   Next.js API Routes + Python FastAPI (SNMP/Reports/DBCheck)
           Production: Go + Rust + Python
Database:  SQLite (Dev) / PostgreSQL (Production)
Engines:   DBCheck v2.6.0 (DB Inspection) + PySNMP (SNMP) + python-docx/WeasyPrint (Reports)
```

### Quick Start

```bash
# Clone repository
git clone https://github.com/acdante-zhang/acdante-itops-inspection.git
cd acdante-itops-inspection

# Install frontend dependencies
pnpm install

# Install Python dependencies (for SNMP + Reports + DBCheck)
python3 -m venv venv
source venv/bin/activate
pip install pysnmp python-docx weasyprint fastapi uvicorn jinja2 matplotlib pymysql psycopg2-binary docxtpl pyyaml cryptography paramiko

# Start Python backend API (port 8000)
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Start frontend dev server (port 5000)
pnpm dev

# Visit http://localhost:5000
```

### Project Structure (v3.0)

```
acdante-itops-inspection/
├── _vendor/dbcheck/               # DBCheck v2.6.0 engine (10 DB types)
├── backend/
│   ├── dbcheck_bridge/            # DBCheck integration layer
│   │   ├── dbcheck_wrapper.py     # Core wrapper for DBCheck
│   │   ├── dbcheck_config.py      # Type mapping & config
│   │   ├── dbcheck_templates.py   # Template sync
│   │   └── dbcheck_updater.py     # Version management
│   ├── snmp_engine/               # SNMP collection engine
│   │   ├── snmp_collector.py      # SNMP v1/v2c/v3 collector
│   │   ├── snmp_oid_registry.py   # 136 OIDs, 11 vendor MIBs
│   │   └── snmp_templates.py      # 12 device templates
│   ├── report_engine/             # Report generation engine
│   │   ├── docx_generator.py      # Editable DOCX reports
│   │   ├── pdf_generator.py       # PDF reports (WeasyPrint)
│   │   └── report_generator.py    # Unified API
│   ├── api/routes.py              # REST API (SNMP + Reports + DBCheck)
│   └── main.py                    # FastAPI entry point
├── src/
│   ├── app/
│   │   ├── snmp/                  # SNMP management page
│   │   ├── dbcheck/               # Database inspection config page
│   │   ├── reports/               # Enhanced report page
│   │   └── api/v1/[...path]/      # Next.js API routes (26 templates)
│   ├── components/layout/         # UI components
│   └── lib/api.ts                 # TypeScript API client
└── database/schema.sql            # Updated schema (DBCheck + SNMP tables)
```

### Architecture

```
Browser → Next.js (5000) → /api/v1/*
         → Python FastAPI (8000)
              ├── SNMP Engine → SNMP v1/v2c/v3 → Network Devices
              ├── Report Engine → DOCX/PDF/HTML Reports
              └── DBCheck Bridge → DBCheck Engine → 10 Database Types

(Production) → Go API Gateway (8080) → Rust Data Engine (8081)
                                      → Python Driver → SSH/SNMP/JDBC → Target Devices
```

### Version History

| Version | Date | Highlights |
|---------|------|------------|
| **v3.0.0** | 2026-06 | DBCheck DB engine, SNMP engine, DOCX/PDF reports, 26 templates, 10 DB types |
| v2.0.0 | 2026-06 | SNMP templates, report engine foundation |
| v1.0.0 | 2026-05 | Initial release: Next.js frontend, basic inspection |

### Updating DBCheck

DBCheck is integrated as a vendor module. To update:

```bash
# Option 1: Git update (if DBCheck repo is accessible)
cd _vendor/dbcheck
git pull origin main

# Option 2: Manual update
# Download latest from https://github.com/fiyo/DBCheck
# Replace _vendor/dbcheck/ directory

# Option 3: Lock to specific version
cd _vendor/dbcheck
git checkout v2.5.0
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

> **最新: v3.0.0** — DBCheck 数据库巡检引擎集成 + SNMP 采集引擎 + 完整 DOCX/PDF 报告生成

---

### 🆕 v3.0.0 更新内容

| 功能 | 说明 |
|------|------|
| **DBCheck 数据库引擎** | 集成 [DBCheck v2.6.0](https://github.com/fiyo/DBCheck) — 10种数据库、130+ YAML规则、5维度健康评分、AI诊断 |
| **SNMP 采集引擎** | Python SNMP v1/v2c/v3 采集器，136个内置OID，12个设备模板（华为/华三/思科/Dell/F5等） |
| **DOCX/PDF 报告** | 完整DOCX（可编辑）和PDF报告生成，含封面、健康仪表盘、问题汇总、详细结果 |
| **模板大幅扩展** | 26个内置巡检模板（12个SNMP + 7个DBCheck数据库 + 7个基础设施） |

### 核心功能

| 模块 | v1.0 | v3.0 |
|------|------|------|
| **巡检对象** | 20+设备类型，7种协议 | **27+设备类型，8种协议**（新增dbcheck） |
| **巡检模板** | 12个内置模板 | **26个内置模板**（12 SNMP + 7 DBCheck数据库 + 7 基础设施） |
| **数据库巡检** | 4种DB，5-10项/DB | **10种DB，50-130+项/DB**（DBCheck驱动） |
| **SNMP监控** | 基础SNMP支持 | **完整SNMP引擎**，136 OID，12厂商模板 |
| **报告生成** | 仅HTML | **DOCX + PDF + HTML**，可编辑Word报告 |
| **任务调度** | 7种周期 | 7种周期 + DBCheck集成 |
| **规则引擎** | 简单阈值 | **YAML规则引擎**（130+规则）+ 安全沙箱 |
| **健康评分** | 简单加权 | **5维度评分**（性能/安全/配置/容量/可用性） |

### 支持的巡检对象

- **操作系统**：Linux、Windows、AIX
- **网络设备**：华为/华三交换机、路由器、防火墙、F5负载均衡
- **SAN交换机**：Brocade、Cisco、华为、联想OEM
- **存储设备**：华为OceanStor、EMC、NetApp
- **数据库**：Oracle（11g/12c/19c/21c）、MySQL 5.7/8.0/8.4、PostgreSQL 12-16、SQL Server 2016-2022
- **国产数据库**：达梦 DM8、TiDB、KingbaseES、GBase 8s、IvorySQL、YashanDB（DBCheck驱动）
- **BMC管理**：Dell iDRAC（Redfish）、IPMI
- **安全设备**：深信服、Checkpoint、Cisco ASA、华为 USG
- **K8s集群**：节点状态、Pod运行、资源使用

### 技术栈

```
前端：  Next.js 16 + React 19 + TypeScript + Tailwind CSS 4 + shadcn/ui
后端：  Next.js API Routes + Python FastAPI（SNMP/报告/DBCheck）
       生产环境：Go + Rust + Python
数据库：SQLite（开发）/ PostgreSQL（生产）
引擎：  DBCheck v2.6.0（数据库巡检）+ PySNMP（SNMP）+ python-docx/WeasyPrint（报告）
```

### 快速开始

```bash
# 克隆仓库
git clone https://github.com/acdante-zhang/acdante-itops-inspection.git
cd acdante-itops-inspection

# 安装前端依赖
pnpm install

# 安装Python依赖（SNMP + 报告 + DBCheck）
python3 -m venv venv
source venv/bin/activate
pip install pysnmp python-docx weasyprint fastapi uvicorn jinja2 matplotlib pymysql psycopg2-binary docxtpl pyyaml cryptography paramiko

# 启动Python后端API（端口8000）
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# 启动前端开发服务器（端口5000）
pnpm dev

# 访问 http://localhost:5000
```

### 项目结构（v3.0）

```
acdante-itops-inspection/
├── _vendor/dbcheck/               # DBCheck v2.6.0 引擎（10种数据库）
├── backend/
│   ├── dbcheck_bridge/            # DBCheck 集成桥接层
│   │   ├── dbcheck_wrapper.py     # DBCheck 核心包装器
│   │   ├── dbcheck_config.py      # 类型映射配置
│   │   ├── dbcheck_templates.py   # 模板同步器
│   │   └── dbcheck_updater.py     # 版本更新管理
│   ├── snmp_engine/               # SNMP 采集引擎
│   │   ├── snmp_collector.py      # SNMP v1/v2c/v3 采集器
│   │   ├── snmp_oid_registry.py   # 136 OID，11厂商MIB库
│   │   └── snmp_templates.py      # 12个设备SNMP模板
│   ├── report_engine/             # 报告生成引擎
│   │   ├── docx_generator.py      # 可编辑DOCX报告
│   │   ├── pdf_generator.py       # PDF报告（WeasyPrint）
│   │   └── report_generator.py    # 统一API入口
│   ├── api/routes.py              # REST API（SNMP + 报告 + DBCheck）
│   └── main.py                    # FastAPI 入口
├── src/
│   ├── app/
│   │   ├── snmp/                  # SNMP管理页面
│   │   ├── dbcheck/               # 数据库巡检配置页
│   │   ├── reports/               # 增强报告页面
│   │   └── api/v1/[...path]/      # Next.js API路由（26个模板）
│   ├── components/layout/         # UI组件
│   └── lib/api.ts                 # TypeScript API客户端
└── database/schema.sql            # 更新后的Schema（DBCheck + SNMP表）
```

### 系统架构

```
浏览器 → Next.js (5000) → /api/v1/*
        → Python FastAPI (8000)
             ├── SNMP 引擎 → SNMP v1/v2c/v3 → 网络设备
             ├── 报告引擎 → DOCX/PDF/HTML 报告
             └── DBCheck 桥接 → DBCheck 引擎 → 10种数据库

(生产环境) → Go API网关 (8080) → Rust数据引擎 (8081)
                                 → Python驱动 → SSH/SNMP/JDBC → 目标设备
```

### 版本历史

| 版本 | 日期 | 主要内容 |
|------|------|----------|
| **v3.0.0** | 2026-06 | DBCheck数据库引擎、SNMP采集引擎、DOCX/PDF报告、26个模板、10种DB |
| v2.0.0 | 2026-06 | SNMP模板、报告引擎基础 |
| v1.0.0 | 2026-05 | 初始版本：Next.js前端、基础巡检功能 |

### 更新 DBCheck

DBCheck 作为内置模块集成。更新方法：

```bash
# 方式1: Git更新（DBCheck仓库可访问时）
cd _vendor/dbcheck
git pull origin main

# 方式2: 手动更新
# 从 https://github.com/fiyo/DBCheck 下载最新版
# 替换 _vendor/dbcheck/ 目录

# 方式3: 锁定特定版本
cd _vendor/dbcheck
git checkout v2.5.0
```

### 文档

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 详细架构设计说明
- [AGENTS.md](./AGENTS.md) - 开发规范

### 开源协议

Apache License 2.0

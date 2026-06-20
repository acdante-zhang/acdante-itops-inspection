# AcdanteSQLMon

[English](#english) | [中文](#中文)

---

<a id="english"></a>

## AcdanteSQLMon — Lightweight Oracle Deadlock & Slow SQL Monitoring Platform

A lightweight, real-time monitoring platform for Oracle database deadlock detection and slow SQL analysis. Supports Oracle 10g/11g/19c/23c/26ai with full RAC cluster compatibility.

### Features

| Module | Description |
|--------|-------------|
| **Wait Events** | Real-time wait event monitoring with INST_ID distinction, GV$ global view queries, wait class color coding, and event explanation panel |
| **Lock Analysis** | Lock relationship directed graph (Canvas), deadlock detection with red markers, holder client info, drill-down to SQL text, client IP detection (SQL + LSOF) |
| **Wait Analysis** | Historical wait event timeline (Recharts), wait class pie chart, TOP slow SQL correlation analysis, configurable time ranges (10m/30m/1h/6h/24h) |
| **Instance Management** | Multi-version driver adaptation (oracledb thin mode for 19c+, cx_Oracle + Instant Client for 10g/11g), test connection, health cards |
| **One-Click Kill** | Verification code + double confirmation dialog, full audit logging (SQL/locks/client/session info), ALTER SYSTEM KILL + kill -9 dual commands |
| **Event Guide** | 15+ common wait event knowledge base with causes, resolutions, and Oracle official documentation links |
| **Custom SQL** | SQL editor with syntax highlighting, preset query templates, save custom templates, safety filtering (SELECT/WITH only), CSV export |

### Architecture

```
Browser → Next.js (5000) → Go API Gateway (8080) → /api/v1/*
                                    ↓
                            Rust Data Engine (8081) → /api/v1/analysis/*
                                    ↓
                            Python Driver → Oracle Database
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, TypeScript 5, shadcn/ui, Tailwind CSS 4, Recharts |
| API Gateway | Go 1.23, Gin v1.10, SQLite, CORS |
| Data Engine | Rust (actix-web 4) — code ready |
| Driver Layer | Python (oracledb / cx_Oracle) |
| Scripts | Shell (Bash) |

### Quick Start

```bash
# Clone the repository
git clone https://github.com/chunxi01/AcdanteSQLMon.git
cd AcdanteSQLMon

# Install frontend dependencies
pnpm install

# Build Go backend
cd go-server && go build -o acdante-sqlmon . && cd ..

# Start development
bash scripts/dev.sh
```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/health | Health check |
| GET | /api/v1/dashboard/stats | Dashboard statistics |
| GET | /api/v1/wait-events | Wait events list |
| GET | /api/v1/locks | Lock information |
| GET | /api/v1/locks/graph | Lock relationship graph |
| GET | /api/v1/wait-analysis | Wait event history analysis |
| GET | /api/v1/wait-analysis/top-sql | TOP slow SQL ranking |
| GET | /api/v1/instances | Instance list |
| POST | /api/v1/instances | Add instance |
| POST | /api/v1/instances/:id/test | Test instance connection |
| GET | /api/v1/kill/candidates | Killable sessions |
| POST | /api/v1/kill/execute | Execute kill |
| GET | /api/v1/kill/audit | Kill audit log |
| GET | /api/v1/event-guide | Wait event knowledge base |
| GET | /api/v1/custom-sql/templates | SQL query templates |
| POST | /api/v1/custom-sql/execute | Execute custom SQL |
| GET | /api/v1/sessions/:sid/detail | Session detail drill-down |
| GET | /api/v1/sessions/:sid/client-ip | Client IP detection (SQL+LSOF) |

### Oracle Version Compatibility

| Version | Driver | Instant Client Required | Connection Mode |
|---------|--------|------------------------|-----------------|
| 10g | cx_Oracle | Yes (Basic + SDK) | Thick mode |
| 11g | cx_Oracle | Yes (Basic + SDK) | Thick mode |
| 19c | oracledb | No | Thin mode |
| 23c | oracledb | No | Thin mode |
| 26ai | oracledb | No | Thin mode |

### License

MIT License — see [LICENSE](./LICENSE)

---

<a id="中文"></a>

## AcdanteSQLMon — 轻量化 Oracle 死锁与卡慢 SQL 监控平台

轻量化的 Oracle 数据库死锁/卡慢 SQL 实时监控平台，支持 Oracle 10g/11g/19c/23c/26ai 全版本，兼容 RAC 集群环境。

### 功能模块

| 模块 | 说明 |
|------|------|
| **等待事件展示** | 实时等待事件监控，区分 INST_ID，查询 GV$ 全局视图，等待分类色标，事件解释面板 |
| **锁分析与死锁检测** | Canvas 锁关系有向图，死锁红色标记，持有者客户端信息，下钻 SQL 文本，客户端 IP 检测（SQL+LSOF） |
| **等待事件分析** | 历史等待事件时序折线图（Recharts），等待类别饼图，TOP 卡慢 SQL 关联分析，可配置时间范围（10m/30m/1h/6h/24h） |
| **实例管理** | 多版本驱动适配（19c+ 用 oracledb thin mode，10g/11g 用 cx_Oracle + Instant Client），测试连接，健康卡片 |
| **一键查杀** | 验证码 + 二次确认弹窗，完整审计日志（SQL/锁/客户端/会话信息），ALTER SYSTEM KILL + kill -9 双方案 |
| **等待事件知识库** | 15+ 常见等待事件知识库，含原因、解决建议、Oracle 官方文档链接 |
| **自定义 SQL** | SQL 编辑器，预设查询模板，保存自定义模板，安全过滤（仅允许 SELECT/WITH），CSV 导出 |

### 架构

```
浏览器 → Next.js (5000) → Go API 网关 (8080) → /api/v1/*
                                    ↓
                            Rust 数据引擎 (8081) → /api/v1/analysis/*
                                    ↓
                            Python 驱动 → Oracle 数据库
```

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 16, React 19, TypeScript 5, shadcn/ui, Tailwind CSS 4, Recharts |
| API 网关 | Go 1.23, Gin v1.10, SQLite, CORS |
| 数据引擎 | Rust (actix-web 4) — 代码已就绪 |
| 驱动层 | Python (oracledb / cx_Oracle) |
| 脚本 | Shell (Bash) |

### 快速启动

```bash
# 克隆仓库
git clone https://github.com/chunxi01/AcdanteSQLMon.git
cd AcdanteSQLMon

# 安装前端依赖
pnpm install

# 编译 Go 后端
cd go-server && go build -o acdante-sqlmon . && cd ..

# 启动开发环境
bash scripts/dev.sh
```

### Oracle 版本兼容性

| 版本 | 驱动 | 需要 Instant Client | 连接模式 |
|------|------|---------------------|----------|
| 10g | cx_Oracle | 是（Basic + SDK） | Thick mode |
| 11g | cx_Oracle | 是（Basic + SDK） | Thick mode |
| 19c | oracledb | 否 | Thin mode |
| 23c | oracledb | 否 | Thin mode |
| 26ai | oracledb | 否 | Thin mode |

### 许可证

MIT License — 详见 [LICENSE](./LICENSE)

# Acdante ITOps Inspection Platform — IT运维巡检平台

## 项目概览

轻量化多协议、多对象自动化IT运维巡检系统，支持自定义巡检任务、模板以及生成可定制的报告。

**核心能力**：
- 巡检对象管理（多协议接入：SSH/SNMP/JDBC/ODBC/IPMI/Redfish/HTTP）
- 巡检模板引擎（版本标记、品牌标记、只读命令提醒、阈值判断）
- 巡检任务调度（一次性/周期执行、通知策略）
- 报告生成（HTML/DOCX/PDF、健康度评分、问题汇总）
- 巡检知识库（常见问题解析、排查方法）
- 系统设置（安全策略、通知配置）

**支持巡检对象类型**：
- 操作系统：Linux、Windows、AIX
- 网络设备：华为/华三交换机、路由器、防火墙、F5负载均衡
- SAN交换机：Brocade、Cisco、华为、联想OEM
- 存储设备：华为OceanStor、EMC、NetApp
- 数据库：Oracle(11g/12c/19c)、MySQL 8.0、PostgreSQL 15
- BMC管理：Dell iDRAC(Redfish)、IPMI

## 技术栈

### 前端
- **Framework**: Next.js 16 (App Router)
- **Core**: React 19
- **Language**: TypeScript 5
- **UI 组件**: shadcn/ui (基于 Radix UI)
- **Styling**: Tailwind CSS 4
- **图标**: Lucide React

### 后端（Next.js API Routes，端口5000）
- 当前通过 Next.js catch-all API 路由 (`/api/v1/[...path]`) 实现
- 模拟数据驱动，可无缝切换到 Go API Gateway + Rust 数据引擎

### 生产架构（Go+Rust+Python 三层）
- **Go API Gateway** (端口 8080)：RESTful 接口、业务逻辑
- **Rust Data Engine** (端口 8081)：高性能采集、连接池
- **Python Worker**：SSH/SNMP/JDBC连接、报告生成

## B/S 架构

```
浏览器 → Next.js (5000) → /api/v1/*
  (生产) → Go API Gateway (8080) → Rust Data Engine (8081)
                                    → Python Driver → SSH/SNMP/JDBC → 目标设备
                                    → Report Engine → DOCX/HTML/PDF
```

## 文件结构

```
├── src/                          # Next.js 前端
│   ├── app/
│   │   ├── layout.tsx            # 根布局（暗色主题 + 侧边栏）
│   │   ├── globals.css           # 全局样式
│   │   ├── page.tsx              # 总览仪表盘
│   │   ├── targets/page.tsx      # 巡检对象管理
│   │   ├── templates/page.tsx    # 巡检模板管理
│   │   ├── tasks/page.tsx        # 巡检任务管理
│   │   ├── reports/page.tsx      # 巡检报告
│   │   ├── knowledge/page.tsx    # 巡检知识库
│   │   ├── settings/page.tsx     # 系统设置
│   │   └── api/v1/[...path]/route.ts  # API 路由（模拟后端）
│   ├── components/
│   │   ├── layout/               # 布局组件（侧边栏+应用外壳）
│   │   └── ui/                   # shadcn/ui 组件
│   └── lib/
│       ├── api.ts                # API 客户端 + 类型定义
│       └── utils.ts              # 通用工具函数
├── go-server/                    # Go API 网关（生产环境）
├── rust-engine/                  # Rust 高性能数据引擎（生产环境）
├── python-driver/                # Python Oracle 驱动适配
├── scripts/                      # 巡检脚本
└── assets/                       # 上传的巡检脚本参考
```

## API 端点清单

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/health | 健康检查 |
| GET | /api/v1/dashboard/stats | 仪表盘统计数据 |
| GET | /api/v1/targets | 巡检对象列表 |
| POST | /api/v1/targets | 创建巡检对象 |
| PUT | /api/v1/targets/:id | 更新巡检对象 |
| DELETE | /api/v1/targets/:id | 删除巡检对象 |
| POST | /api/v1/targets/:id/test | 连接测试 |
| GET | /api/v1/templates | 巡检模板列表 |
| POST | /api/v1/templates | 创建模板 |
| PUT | /api/v1/templates/:id | 更新模板 |
| DELETE | /api/v1/templates/:id | 删除模板 |
| GET | /api/v1/tasks | 巡检任务列表 |
| POST | /api/v1/tasks | 创建任务 |
| POST | /api/v1/tasks/:id/run | 执行任务 |
| DELETE | /api/v1/tasks/:id | 删除任务 |
| GET | /api/v1/results | 巡检结果列表 |
| GET | /api/v1/reports | 报告列表 |
| GET | /api/v1/reports/:id | 报告详情 |
| POST | /api/v1/reports/generate | 生成报告 |
| GET | /api/v1/knowledge | 知识库列表 |
| GET | /api/v1/knowledge/:id | 知识库详情 |

## 页面模块 (7个)

### 总览仪表盘 (/)
- 统计卡片（巡检对象/模板/严重问题/今日报告）
- 巡检对象类型分布
- 最近告警列表
- 近期任务状态
- 健康趋势图

### 巡检对象管理 (/targets)
- 对象列表CRUD、类型筛选、搜索
- 连接测试、批量导入、离线模式
- 支持多协议配置（SSH/SNMP/JDBC等）
- 健康度评分

### 巡检模板管理 (/templates)
- 模板列表、版本标记、品牌标记
- 巡检项展开详情（命令/类型/只读/权重）
- 非只读命令警告提醒
- 模板复制、编辑、删除

### 巡检任务管理 (/tasks)
- 任务创建、调度配置（一次性/周期）
- 手动执行、状态跟踪
- 通知策略（邮件/Webhook）

### 巡检报告 (/reports)
- 报告列表、在线预览
- 健康度评分条、问题汇总
- 概览/问题/详情三Tab
- 下载（HTML/DOCX/PDF）

### 巡检知识库 (/knowledge)
- 常见问题卡片（症状/原因/解决方案）
- 搜索与分类筛选
- 严重程度标记、参考文档链接

### 系统设置 (/settings)
- 通用设置（平台名称/报告格式/时区）
- 安全设置（加密/超时/2FA/IP白名单）
- 通知配置（SMTP/Webhook）
- 系统信息（技术栈架构展示）

## 开发命令

- `pnpm dev` — 启动前端开发服务器（端口5000，含API路由）
- `pnpm build` — 构建前端生产版本
- `pnpm lint` — ESLint 检查
- `pnpm ts-check` — TypeScript 类型检查

## 关键设计决策

1. **Next.js API Routes 替代 Go 后端**：开发环境使用 Next.js API Routes 提供模拟数据，生产环境切换到 Go+Rust+Python 三层架构
2. **多版本 SQL 适配**：Oracle 11g/12c/19c 各版本查询语句差异通过模板版本标记管理
3. **只读命令提醒**：所有巡检项必须标记是否只读，非只读命令显示醒目警告
4. **品牌/版本标记**：每个巡检模板绑定品牌和版本，不同品牌/版本的相同设备类型命令可能有差异
5. **离线采集支持**：巡检对象可标记为离线模式，接受上传的采集数据
6. **健康度评分**：每个对象和报告都有0-100分的健康度评分，权重由巡检项决定
7. **预置丰富模板**：内置 Linux、Oracle(11g/12c/19c)、华为/华三网络、Brocade SAN、华为存储、Windows、AIX、MySQL、PostgreSQL、Dell iDRAC 等模板

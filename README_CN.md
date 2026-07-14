# Acdante ITOps Inspection Platform

> 企业级IT基础设施巡检平台 | Enterprise IT Infrastructure Inspection Platform

## 🚀 快速开始

### 方式一：本地启动（推荐开发）

```bash
# 1. 安装依赖
npm install
pip install -r backend/requirements.txt

# 2. 一键启动
chmod +x start.sh
./start.sh

# 3. 访问
# 前端: http://localhost:5000
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方式二：Docker部署（推荐生产）

```bash
docker-compose up -d
# 前端: http://localhost:5000
# 后端: http://localhost:8000
```

### 方式三：分离启动

```bash
# Terminal 1: Python后端
PYTHON_API_PORT=8000 python -m backend.main

# Terminal 2: Next.js前端
PYTHON_API_URL=http://127.0.0.1:8000 npm run dev
```

## 📊 功能模块

| 模块 | 说明 | 状态 |
|------|------|------|
| SSH巡检 | Linux/网络设备/AIX命令执行 | ✅ |
| SNMP巡检 | v1/v2c/v3, 136+ OID | ✅ |
| DBCheck巡检 | 10种数据库, 130+规则 | ✅ |
| HTTP巡检 | 防火墙/安全设备Web API | ✅ |
| 定时调度 | APScheduler | ✅ |
| 报告生成 | HTML/DOCX | ✅ |
| PACS-AI | GPU/vLLM/DICOM专用巡检 | ✅ |
| WebSocket | 实时任务进度 | ✅ |

## 🏥 PACS-AI影像质控

本平台特别针对PACS-AI影像质控系统提供专用巡检模板：

- **GPU服务器巡检**: nvidia-smi全指标（使用率/显存/温度/功耗/进程）
- **vLLM推理服务巡检**: API健康/模型加载/端口监听
- **PACS系统服务巡检**: DICOM端口/Web服务/存储空间/容器状态
- **网络设备巡检**: 交换机/防火墙专用模板

### 快速GPU巡检

```bash
curl -X POST http://localhost:8000/api/v1/pacs/inspect/gpu \
  -H "Content-Type: application/json" \
  -d '{"host": "192.168.1.100", "username": "root", "password": "xxx"}'
```

## 📁 项目结构

```
acdante-itops-inspection/
├── src/                    # Next.js 前端
│   ├── app/               # 页面
│   │   ├── page.tsx       # 仪表盘
│   │   ├── targets/       # 巡检对象
│   │   ├── templates/     # 巡检模板
│   │   ├── tasks/         # 巡检任务
│   │   ├── reports/       # 巡检报告
│   │   ├── snmp/          # SNMP巡检
│   │   └── dbcheck/       # 数据库巡检
│   ├── components/        # UI组件
│   └── lib/               # 工具函数
├── backend/               # Python 后端
│   ├── core/              # 核心引擎
│   │   ├── ssh_executor.py    # SSH巡检引擎
│   │   ├── inspect_engine.py  # 统一巡检调度
│   │   ├── database.py        # SQLite持久化
│   │   ├── scheduler.py       # 任务调度器
│   │   └── websocket.py       # WebSocket
│   ├── api/               # API路由
│   │   ├── real_routes.py     # 真实API
│   │   └── pacs_routes.py     # PACS-AI API
│   ├── templates/         # 巡检模板
│   │   ├── pacs_ai_templates.py   # PACS-AI专用
│   │   └── extended_templates.py  # 扩展设备
│   ├── snmp_engine/       # SNMP引擎
│   ├── dbcheck_bridge/    # DBCheck桥接
│   └── report_engine/     # 报告生成
├── scripts/               # 运维脚本
│   ├── test_ssh.py        # SSH测试
│   └── init_db.py         # 数据库初始化
├── start.sh               # 一键启动
├── docker-compose.yml     # Docker部署
└── DEV_GUIDE.md           # 开发指南
```

## 🔌 API文档

启动后端后访问: http://localhost:8000/docs

### 核心端点

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/dashboard/stats | 仪表盘 |
| GET/POST | /api/v1/targets | 巡检对象 |
| POST | /api/v1/targets/:id/test | 测试连接 |
| GET | /api/v1/templates | 模板列表 |
| GET/POST | /api/v1/tasks | 任务管理 |
| POST | /api/v1/tasks/:id/run | 执行巡检 |
| GET | /api/v1/results | 巡检结果 |
| GET | /api/v1/reports | 报告列表 |

### PACS-AI端点

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/pacs/templates | PACS模板 |
| POST | /api/v1/pacs/inspect/gpu | GPU巡检 |
| POST | /api/v1/pacs/inspect/vllm | vLLM巡检 |
| POST | /api/v1/pacs/inspect/pacs | PACS系统巡检 |

## 🔧 环境变量

| Variable | Default | Description |
|----------|---------|-------------|
| PYTHON_API_PORT | 8000 | Python后端端口 |
| NEXT_PORT | 5000 | Next.js前端端口 |
| PYTHON_API_URL | http://127.0.0.1:8000 | 后端地址 |
| ITOPS_DB_PATH | backend/data/itops.db | 数据库路径 |
| SSH_TIMEOUT | 30 | SSH超时(秒) |
| LOG_LEVEL | INFO | 日志级别 |

## 📝 开发说明

详见 [DEV_GUIDE.md](DEV_GUIDE.md)

## 📄 License

MIT License

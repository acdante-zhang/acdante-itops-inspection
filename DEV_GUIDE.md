# Acdante ITOps - Development Guide

## Quick Start

### Development (Mock Mode)
```bash
npm install
npm run dev
# Open http://localhost:5000
```

### Development (With Real Backend)
```bash
# Terminal 1: Start Python backend
pip install -r backend/requirements.txt
PYTHON_API_PORT=8000 python -m backend.main

# Terminal 2: Start Next.js frontend
PYTHON_API_URL=http://127.0.0.1:8000 npm run dev
# Open http://localhost:5000
```

### One-Click Start
```bash
chmod +x start.sh
./start.sh
```

### Docker
```bash
docker-compose up -d
```

## Architecture

```
frontend (Next.js :5000)
    │
    ├── /api/v1/* → Proxy to Python backend
    │
backend (FastAPI :8000)
    │
    ├── /api/v1/targets     → CRUD巡检对象
    ├── /api/v1/templates   → 巡检模板
    ├── /api/v1/tasks       → 巡检任务
    ├── /api/v1/tasks/:id/run → 执行巡检
    ├── /api/v1/results     → 巡检结果
    ├── /api/v1/reports     → 报告
    ├── /api/v1/snmp/*      → SNMP引擎
    ├── /api/v1/dbcheck/*   → DBCheck引擎
    └── /api/v1/health      → 健康检查

    core/
    ├── ssh_executor.py     → SSH巡检引擎
    ├── inspect_engine.py   → 统一巡检调度
    ├── database.py         → SQLite持久化
    └── scheduler.py        → 定时任务调度

    templates/
    └── pacs_ai_templates.py → PACS-AI专用模板
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/dashboard/stats | 仪表盘统计 |
| GET | /api/v1/targets | 巡检对象列表 |
| POST | /api/v1/targets | 创建巡检对象 |
| POST | /api/v1/targets/:id/test | 测试连接 |
| GET | /api/v1/templates | 模板列表 |
| GET | /api/v1/tasks | 任务列表 |
| POST | /api/v1/tasks | 创建任务 |
| POST | /api/v1/tasks/:id/run | 执行巡检 |
| GET | /api/v1/results | 巡检结果 |
| GET | /api/v1/reports | 报告列表 |
| GET | /api/v1/snmp/templates | SNMP模板 |
| POST | /api/v1/snmp/test | SNMP连接测试 |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PYTHON_API_PORT | 8000 | Python后端端口 |
| NEXT_PORT | 5000 | Next.js前端端口 |
| PYTHON_API_URL | http://127.0.0.1:8000 | Python后端地址 |
| ITOPS_DB_PATH | backend/data/itops.db | SQLite数据库路径 |

# Changelog

## v3.1.0 (2026-07-14)

### 🆕 新增核心模块

- **SSH巡检引擎** (`backend/core/ssh_executor.py`)
  - 基于paramiko的SSH命令执行
  - 支持密码/密钥认证
  - 设备类型适配: Linux/Huawei/H3C/Cisco/Brocade/AIX
  - subprocess降级模式 (paramiko未安装时)
  - 批量命令执行 + 阈值判断

- **统一巡检调度** (`backend/core/inspect_engine.py`)
  - SSH/SNMP/DBCheck/HTTP四种协议统一调度
  - 健康分数自动计算
  - 巡检结果标准化

- **数据持久化** (`backend/core/database.py`)
  - SQLite数据库
  - 巡检对象/模板/任务/结果/报告 CRUD
  - 仪表盘统计

- **任务调度器** (`backend/core/scheduler.py`)
  - APScheduler定时巡检
  - 支持: hourly/daily/weekly/monthly/manual

- **真实API路由** (`backend/api/real_routes.py`)
  - 替代Mock数据
  - 连接前端与真实后端

### 🏥 PACS-AI影像质控专用模板

- **GPU服务器巡检** (`pacs_ai_templates.py`)
  - nvidia-smi全指标: 使用率/显存/温度/功耗/进程
  - CUDA版本/驱动版本

- **vLLM推理服务巡检**
  - API健康检查/模型加载/端口监听
  - 系统内存/Swap使用

- **PACS系统服务巡检**
  - DICOM端口/Web服务/存储空间
  - 数据库连接/容器状态

- **网络设备巡检**
  - 交换机/防火墙专用模板

### 🔧 扩展设备模板

- 华为OceanStor存储
- F5 BIG-IP负载均衡
- Dell iDRAC Redfish
- Windows Server
- AIX

### 🐳 部署支持

- `start.sh`: 一键启动脚本
- `Dockerfile.python`: Python后端Docker镜像
- `docker-compose.yml`: 全栈Docker部署
- `DEV_GUIDE.md`: 开发指南

### 📊 SNMP引擎

- 136+内置OID
- 10个厂商支持
- v1/v2c/v3协议

### 🔌 API端点

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/dashboard/stats | 仪表盘统计 |
| GET/POST | /api/v1/targets | 巡检对象CRUD |
| POST | /api/v1/targets/:id/test | 测试连接 |
| GET | /api/v1/templates | 模板列表 |
| GET/POST | /api/v1/tasks | 任务CRUD |
| POST | /api/v1/tasks/:id/run | 执行巡检 |
| GET | /api/v1/results | 巡检结果 |
| GET | /api/v1/reports | 报告列表 |
| GET | /api/v1/snmp/templates | SNMP模板 |
| POST | /api/v1/snmp/test | SNMP连接测试 |
| GET | /api/v1/pacs/templates | PACS-AI模板 |
| POST | /api/v1/pacs/inspect/gpu | GPU巡检 |
| POST | /api/v1/pacs/inspect/vllm | vLLM巡检 |
| POST | /api/v1/pacs/inspect/pacs | PACS系统巡检 |

---

## v3.0.0 (2026-07-09)

- DBCheck数据库引擎集成
- SNMP采集引擎
- DOCX/PDF报告生成
- 26个内置巡检模板

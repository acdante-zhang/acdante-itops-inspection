"""
Acdante ITOps - PACS-AI 影像质控专用巡检模板
针对医学影像AI系统的特殊巡检需求
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PACSAITemplate:
    """PACS-AI影像质控巡检模板"""
    id: str
    name: str
    description: str
    category: str  # infrastructure, application, gpu, network, storage
    items: List[Dict] = field(default_factory=list)


# ============================================================
# GPU服务器巡检模板（L20/T4/A100等）
# ============================================================

GPU_SERVER_TEMPLATE = PACSAITemplate(
    id="pacs-ai-gpu-server-v1",
    name="PACS-AI GPU服务器巡检模板",
    description="AI推理服务器GPU状态、显存、温度、CUDA环境巡检",
    category="infrastructure",
    items=[
        {
            "id": "gpu-01", "name": "GPU设备列表", "category": "GPU",
            "command": "nvidia-smi --query-gpu=index,name,uuid --format=csv,noheader 2>/dev/null || echo 'nvidia-smi not available'",
            "command_type": "ssh", "parser": "raw", "weight": 10, "order": 1,
        },
        {
            "id": "gpu-02", "name": "GPU使用率", "category": "GPU",
            "command": "nvidia-smi --query-gpu=index,utilization.gpu --format=csv,noheader 2>/dev/null || echo 'N/A'",
            "command_type": "ssh", "parser": "raw",
            "threshold": {"operator": "gt", "critical": 95, "warning": 80, "unit": "%"},
            "suggestion": "GPU使用率过高，检查推理任务队列",
            "weight": 20, "order": 2,
        },
        {
            "id": "gpu-03", "name": "GPU显存使用", "category": "GPU",
            "command": "nvidia-smi --query-gpu=index,memory.used,memory.total,memory.free --format=csv,noheader 2>/dev/null || echo 'N/A'",
            "command_type": "ssh", "parser": "raw",
            "threshold": {"operator": "gt", "critical": 95, "warning": 85, "unit": "%"},
            "suggestion": "显存接近满载，检查是否有僵尸进程占用显存",
            "weight": 20, "order": 3,
        },
        {
            "id": "gpu-04", "name": "GPU温度", "category": "GPU",
            "command": "nvidia-smi --query-gpu=index,temperature.gpu --format=csv,noheader 2>/dev/null || echo 'N/A'",
            "command_type": "ssh", "parser": "raw",
            "threshold": {"operator": "gt", "critical": 85, "warning": 75, "unit": "°C"},
            "suggestion": "GPU温度过高，检查机房散热和服务器风扇",
            "weight": 15, "order": 4,
        },
        {
            "id": "gpu-05", "name": "GPU功耗", "category": "GPU",
            "command": "nvidia-smi --query-gpu=index,power.draw,power.limit --format=csv,noheader 2>/dev/null || echo 'N/A'",
            "command_type": "ssh", "parser": "raw", "weight": 5, "order": 5,
        },
        {
            "id": "gpu-06", "name": "GPU进程列表", "category": "GPU",
            "command": "nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader 2>/dev/null || echo 'No GPU processes'",
            "command_type": "ssh", "parser": "raw", "weight": 15, "order": 6,
        },
        {
            "id": "gpu-07", "name": "CUDA版本", "category": "环境",
            "command": "nvcc --version 2>/dev/null | grep release || nvidia-smi | grep CUDA || echo 'N/A'",
            "command_type": "ssh", "parser": "raw", "weight": 5, "order": 7,
        },
        {
            "id": "gpu-08", "name": "NVIDIA驱动版本", "category": "环境",
            "command": "nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 2>/dev/null || echo 'N/A'",
            "command_type": "ssh", "parser": "raw", "weight": 5, "order": 8,
        },
    ],
)


# ============================================================
# vLLM推理服务巡检模板
# ============================================================

VLLM_SERVICE_TEMPLATE = PACSAITemplate(
    id="pacs-ai-vllm-service-v1",
    name="PACS-AI vLLM推理服务巡检模板",
    description="vLLM大模型推理服务状态、API可用性、模型加载状态",
    category="application",
    items=[
        {
            "id": "vllm-01", "name": "vLLM进程状态", "category": "服务",
            "command": "ps aux | grep 'vllm' | grep -v grep | head -10",
            "command_type": "ssh", "parser": "raw",
            "suggestion": "vLLM服务未运行，检查服务状态",
            "weight": 20, "order": 1,
        },
        {
            "id": "vllm-02", "name": "vLLM API健康检查", "category": "API",
            "command": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8106/v1/models 2>/dev/null || echo '000'",
            "command_type": "ssh", "parser": "raw",
            "threshold": {"operator": "ne", "critical": 200, "warning": 200, "unit": ""},
            "suggestion": "vLLM API不可用，检查服务是否启动",
            "weight": 20, "order": 2,
        },
        {
            "id": "vllm-03", "name": "已加载模型列表", "category": "模型",
            "command": "curl -s http://localhost:8106/v1/models 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); [print(m[\"id\"]) for m in d.get(\"data\",[])]' 2>/dev/null || echo 'N/A'",
            "command_type": "ssh", "parser": "raw", "weight": 15, "order": 3,
        },
        {
            "id": "vllm-04", "name": "推理端口监听", "category": "网络",
            "command": "ss -tlnp | grep -E '(8102|8103|8104|8105|8106)' 2>/dev/null || echo 'No inference ports found'",
            "command_type": "ssh", "parser": "raw", "weight": 15, "order": 4,
        },
        {
            "id": "vllm-05", "name": "系统内存使用", "category": "系统",
            "command": "free -m | awk 'NR==2{printf \"%.1f%%\", $3/$2*100}'",
            "command_type": "ssh", "parser": "raw",
            "threshold": {"operator": "gt", "critical": 95, "warning": 85, "unit": "%"},
            "suggestion": "系统内存不足，检查是否有内存泄漏",
            "weight": 15, "order": 5,
        },
        {
            "id": "vllm-06", "name": "Swap使用", "category": "系统",
            "command": "free -m | awk 'NR==3{printf \"%.1f%%\", $3/$2*100}'",
            "command_type": "ssh", "parser": "raw",
            "threshold": {"operator": "gt", "critical": 80, "warning": 50, "unit": "%"},
            "weight": 10, "order": 6,
        },
    ],
)


# ============================================================
# PACS系统服务巡检模板
# ============================================================

PACS_SYSTEM_TEMPLATE = PACSAITemplate(
    id="pacs-ai-system-v1",
    name="PACS-AI系统服务巡检模板",
    description="PACS影像系统核心服务、DICOM端口、数据库连接、存储空间",
    category="application",
    items=[
        {
            "id": "pacs-01", "name": "DICOM服务端口", "category": "DICOM",
            "command": "ss -tlnp | grep -E '(:104|:11112|:8080|:8042|:8100)' 2>/dev/null || echo 'No DICOM ports found'",
            "command_type": "ssh", "parser": "raw",
            "suggestion": "DICOM服务端口未监听，检查PACS服务状态",
            "weight": 20, "order": 1,
        },
        {
            "id": "pacs-02", "name": "Web服务状态", "category": "Web",
            "command": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/ 2>/dev/null || echo '000'",
            "command_type": "ssh", "parser": "raw", "weight": 15, "order": 2,
        },
        {
            "id": "pacs-03", "name": "影像存储空间", "category": "存储",
            "command": "df -h /data/dicom /data/images /data/pacs 2>/dev/null | awk 'NR>1{print $6, $5}' || df -h | grep -E '(data|dicom|pacs)' | awk '{print $6, $5}'",
            "command_type": "ssh", "parser": "raw",
            "threshold": {"operator": "gt", "critical": 90, "warning": 80, "unit": "%"},
            "suggestion": "影像存储空间不足，清理历史影像或扩容",
            "weight": 20, "order": 3,
        },
        {
            "id": "pacs-04", "name": "数据库连接", "category": "数据库",
            "command": "ss -tlnp | grep -E '(:5432|:3306|:1521|:1433)' 2>/dev/null || echo 'No DB ports found'",
            "command_type": "ssh", "parser": "raw", "weight": 15, "order": 4,
        },
        {
            "id": "pacs-05", "name": "AI推理服务端口", "category": "AI",
            "command": "ss -tlnp | grep -E '(:8106|:8107|:8108)' 2>/dev/null || echo 'No AI inference ports found'",
            "command_type": "ssh", "parser": "raw", "weight": 15, "order": 5,
        },
        {
            "id": "pacs-06", "name": "Docker容器状态", "category": "容器",
            "command": "docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}' 2>/dev/null | grep -iE '(pacs|dicom|ai|vllm|model)' || echo 'No PACS containers found'",
            "command_type": "ssh", "parser": "raw", "weight": 15, "order": 6,
        },
        {
            "id": "pacs-07", "name": "系统日志错误", "category": "日志",
            "command": "journalctl -p err --since '1 hour ago' | grep -iE '(pacs|dicom|ai|model|vllm)' | tail -20 2>/dev/null || echo 'No recent errors'",
            "command_type": "ssh", "parser": "raw", "weight": 10, "order": 7,
        },
    ],
)


# ============================================================
# 网络设备巡检模板（PACS-AI专用）
# ============================================================

PACS_NETWORK_TEMPLATE = PACSAITemplate(
    id="pacs-ai-network-v1",
    name="PACS-AI网络设备巡检模板",
    description="PACS-AI系统关联网络设备（核心交换机、防火墙）",
    category="network",
    items=[
        {
            "id": "net-01", "name": "设备版本", "category": "系统",
            "command": "display version | head -10",
            "command_type": "ssh", "parser": "raw", "weight": 5, "order": 1,
        },
        {
            "id": "net-02", "name": "CPU使用率", "category": "CPU",
            "command": "display cpu-usage",
            "command_type": "ssh", "parser": "raw",
            "threshold": {"operator": "gt", "critical": 90, "warning": 70, "unit": "%"},
            "weight": 20, "order": 2,
        },
        {
            "id": "net-03", "name": "内存使用率", "category": "内存",
            "command": "display memory-usage",
            "command_type": "ssh", "parser": "raw",
            "threshold": {"operator": "gt", "critical": 85, "warning": 70, "unit": "%"},
            "weight": 20, "order": 3,
        },
        {
            "id": "net-04", "name": "上联接口状态", "category": "接口",
            "command": "display interface brief | include GE",
            "command_type": "ssh", "parser": "raw",
            "suggestion": "上联接口异常，检查光纤连接",
            "weight": 15, "order": 4,
        },
        {
            "id": "net-05", "name": "PACS相关VLAN", "category": "VLAN",
            "command": "display vlan | include PACS",
            "command_type": "ssh", "parser": "raw", "weight": 10, "order": 5,
        },
        {
            "id": "net-06", "name": "告警信息", "category": "告警",
            "command": "display alarm active all",
            "command_type": "ssh", "parser": "raw",
            "suggestion": "存在活跃告警，需及时处理",
            "weight": 15, "order": 6,
        },
    ],
)


# ============================================================
# 模板注册表
# ============================================================

ALL_PACS_TEMPLATES = {
    "pacs-ai-gpu-server-v1": GPU_SERVER_TEMPLATE,
    "pacs-ai-vllm-service-v1": VLLM_SERVICE_TEMPLATE,
    "pacs-ai-system-v1": PACS_SYSTEM_TEMPLATE,
    "pacs-ai-network-v1": PACS_NETWORK_TEMPLATE,
}


def get_pacs_templates() -> List[PACSAITemplate]:
    """获取所有PACS-AI模板"""
    return list(ALL_PACS_TEMPLATES.values())


def get_pacs_template(template_id: str) -> Optional[PACSAITemplate]:
    """获取指定PACS-AI模板"""
    return ALL_PACS_TEMPLATES.get(template_id)


def get_pacs_templates_for_db() -> List[Dict]:
    """获取模板列表（用于写入数据库）"""
    templates = []
    for tpl in ALL_PACS_TEMPLATES.values():
        templates.append({
            "id": tpl.id,
            "name": tpl.name,
            "target_type": "linux" if tpl.category in ("infrastructure", "application") else "network",
            "brand": "PACS-AI",
            "version": "v1.0.0",
            "description": tpl.description,
            "is_builtin": 1,
            "items": tpl.items,
            "created_by": "system (PACS-AI)",
        })
    return templates

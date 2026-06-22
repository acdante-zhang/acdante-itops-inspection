"""
Acdante ITOps - 报告生成引擎核心
支持 DOCX 和 PDF 格式的巡检报告生成
"""

import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# 报告引擎目录
REPORT_ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(REPORT_ENGINE_DIR, "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(REPORT_ENGINE_DIR), "..", "..", "workspace", "reports")

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)


class ReportFormat(str, Enum):
    HTML = "html"
    DOCX = "docx"
    PDF = "pdf"


class DeviceType(str, Enum):
    """设备类型枚举"""
    ROUTER = "router"
    SWITCH = "switch"
    FIREWALL = "firewall"
    LOAD_BALANCER = "load_balancer"
    SERVER = "server"
    STORAGE = "storage"
    SAN_SWITCH = "san_switch"
    VMWARE = "vmware"
    IBM_MINICOMPUTER = "ibm_minicomputer"
    BLADE_CENTER = "blade_center"
    BACKUP = "backup"
    IPS = "ips"
    WAF = "waf"
    VPN = "vpn"
    BASTION = "bastion"
    NETGAP = "netgap"  # 网闸
    TAPE_LIBRARY = "tape_library"
    DATABASE = "database"
    OTHER = "other"


@dataclass
class DeviceInfo:
    """设备基本信息"""
    name: str = ""                    # 设备名称 (如: 生产边界路由器)
    ip: str = ""                      # 管理IP
    device_type: DeviceType = DeviceType.OTHER
    brand: str = ""                   # 品牌 (H3C/华为/EMC/IBM等)
    model: str = ""                   # 型号
    serial_number: str = ""           # 序列号
    os_version: str = ""              # 系统版本
    hardware_config: Dict = field(default_factory=dict)  # 硬件配置
    location: str = ""                # 位置
    role: str = ""                    # 角色/用途
    extra_info: Dict = field(default_factory=dict)  # 额外信息


@dataclass
class InspectionCheckItem:
    """单个巡检检查项"""
    name: str                         # 检查内容名称
    operation: str = ""               # 检查操作/命令
    result: str = ""                  # 巡检结果
    status: str = "ok"                # ok/warning/critical/error/skipped
    raw_value: str = ""               # 原始值
    threshold: str = ""               # 阈值
    suggestion: str = ""              # 建议
    screenshot: str = ""              # 截图说明


@dataclass
class InspectionSection:
    """巡检检查分区 (如: 基本信息检查、设备运行状态检查、协议检查等)"""
    title: str
    items: List[InspectionCheckItem] = field(default_factory=list)
    section_type: str = "check"  # info / check / protocol / security
    extra_data: Dict = field(default_factory=dict)  # 额外数据 (如基本信息的key-value)


@dataclass
class DeviceInspectionResult:
    """单台设备的完整巡检结果"""
    device: DeviceInfo = field(default_factory=DeviceInfo)
    sections: List[InspectionSection] = field(default_factory=list)
    overall_status: str = "ok"        # 整体状态
    summary: str = ""                 # 设备巡检总结
    inspection_date: str = ""         # 巡检日期
    inspector: str = ""               # 巡检人员


@dataclass
class ReportSection:
    """报告章节"""
    title: str
    content: str = ""
    level: int = 1  # 1=标题, 2=子标题
    items: List[Dict] = field(default_factory=list)


@dataclass
class ReportConfig:
    """报告配置"""
    title: str = "IT基础设施巡检报告"
    subtitle: str = ""
    platform_name: str = "Acdante ITOps Inspection Platform"
    company_name: str = ""            # 客户单位名称
    client_contact: str = ""          # 客户联系人
    client_phone: str = ""            # 客户联系电话
    contract_number: str = ""         # 合同编号
    inspector: str = ""
    report_date: str = ""
    inspection_period: str = ""       # 巡检周期 (如: 月度/季度)
    inspection_date_range: str = ""   # 巡检时间范围 (如: 2024.09.23-9.29)
    service_team: str = ""            # 技术服务团队
    engineers: List[Dict] = field(default_factory=list)  # 巡检工程师列表
    service_content: str = ""         # 巡检服务内容
    report_authors: List[str] = field(default_factory=list)  # 报告编写人
    report_reviewer: str = ""         # 报告审批人
    author_date: str = ""             # 编写日期
    reviewer_date: str = ""           # 审批日期
    include_cover: bool = True
    include_toc: bool = True
    include_charts: bool = True
    include_appendix: bool = True
    template: str = "standard"  # standard, detailed, compact


@dataclass
class InspectionReportData:
    """巡检报告数据"""
    report_id: str = ""
    task_name: str = ""
    task_id: str = ""
    target_count: int = 0
    health_score: int = 0
    total_items: int = 0
    ok_count: int = 0
    warning_count: int = 0
    critical_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    summary: str = ""
    generated_at: str = ""
    targets: List[Dict] = field(default_factory=list)
    results: List[Dict] = field(default_factory=list)
    issues: List[Dict] = field(default_factory=list)
    categories: List[Dict] = field(default_factory=list)
    health_trend: List[Dict] = field(default_factory=list)
    ai_analysis: str = ""
    recommendations: List[str] = field(default_factory=list)
    config: ReportConfig = field(default_factory=ReportConfig)
    # 新增: 设备巡检结果列表 (用于模板化报告)
    device_results: List[DeviceInspectionResult] = field(default_factory=list)
    # 新增: 报告分区标题列表
    report_sections: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.report_id:
            self.report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"


class ReportGenerator:
    """报告生成器核心"""
    
    def __init__(self, data: InspectionReportData):
        self.data = data
        self._ensure_dates()
    
    def _ensure_dates(self):
        """确保日期格式统一"""
        if not self.data.generated_at:
            self.data.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_health_level(self) -> str:
        """获取健康等级"""
        score = self.data.health_score
        if score >= 90:
            return "优秀"
        elif score >= 75:
            return "良好"
        elif score >= 60:
            return "一般"
        else:
            return "较差"
    
    def get_health_color(self) -> str:
        """获取健康等级颜色"""
        score = self.data.health_score
        if score >= 90:
            return "#22c55e"
        elif score >= 75:
            return "#3b82f6"
        elif score >= 60:
            return "#eab308"
        else:
            return "#ef4444"
    
    def get_status_label(self, status: str) -> str:
        """获取状态标签"""
        labels = {
            "ok": "正常",
            "warning": "警告",
            "critical": "严重",
            "error": "错误",
            "skipped": "跳过",
            "pending": "待执行",
            "running": "执行中",
            "completed": "已完成",
            "failed": "失败",
        }
        return labels.get(status, status)
    
    def get_status_color(self, status: str) -> str:
        """获取状态颜色"""
        colors = {
            "ok": "#22c55e",
            "warning": "#eab308",
            "critical": "#ef4444",
            "error": "#dc2626",
            "skipped": "#9ca3af",
        }
        return colors.get(status, "#6b7280")
    
    def get_category_distribution(self) -> Dict[str, Dict]:
        """获取分类统计分布"""
        distribution = {}
        for result in self.data.results:
            cat = result.get("category", "其他")
            if cat not in distribution:
                distribution[cat] = {"total": 0, "ok": 0, "warning": 0, "critical": 0}
            distribution[cat]["total"] += 1
            status = result.get("status", "ok")
            if status in distribution[cat]:
                distribution[cat][status] += 1
        return distribution
    
    def generate_html(self) -> str:
        """生成HTML报告"""
        from .pdf_generator import PDFGenerator
        gen = PDFGenerator(self.data)
        return gen.render_html()
    
    def generate_docx(self, output_path: str = None) -> str:
        """生成DOCX报告"""
        from .docx_generator import DocxGenerator
        gen = DocxGenerator(self.data)
        if not output_path:
            output_path = os.path.join(OUTPUT_DIR, f"{self.data.report_id}.docx")
        return gen.generate(output_path)
    
    def generate_pdf(self, output_path: str = None) -> str:
        """生成PDF报告"""
        from .pdf_generator import PDFGenerator
        gen = PDFGenerator(self.data)
        if not output_path:
            output_path = os.path.join(OUTPUT_DIR, f"{self.data.report_id}.pdf")
        return gen.generate(output_path)
    
    def generate_all(self) -> Dict[str, str]:
        """生成所有格式报告"""
        paths = {}
        
        # 生成DOCX
        try:
            paths['docx'] = self.generate_docx()
        except Exception as e:
            paths['docx_error'] = str(e)
        
        # 生成PDF
        try:
            paths['pdf'] = self.generate_pdf()
        except Exception as e:
            paths['pdf_error'] = str(e)
        
        return paths


# ============================================================
# 报告数据构建工具
# ============================================================

def build_report_data_from_inspection(
    task_name: str,
    task_id: str,
    targets: List[Dict],
    results: List[Dict],
    config: Optional[ReportConfig] = None,
) -> InspectionReportData:
    """从巡检结果构建报告数据"""
    
    # 统计
    total = len(results)
    ok_count = sum(1 for r in results if r.get("status") == "ok")
    warning_count = sum(1 for r in results if r.get("status") == "warning")
    critical_count = sum(1 for r in results if r.get("status") == "critical")
    error_count = sum(1 for r in results if r.get("status") == "error")
    skipped_count = sum(1 for r in results if r.get("status") == "skipped")
    
    # 健康度评分
    if total > 0:
        weights_sum = sum(r.get("weight", 10) for r in results)
        ok_weights = sum(r.get("weight", 10) for r in results if r.get("status") == "ok")
        warning_weights = sum(r.get("weight", 10) * 0.5 for r in results if r.get("status") == "warning")
        critical_weights = sum(r.get("weight", 10) * 0 for r in results if r.get("status") == "critical")
        health_score = int((ok_weights + warning_weights) / weights_sum * 100) if weights_sum > 0 else 100
    else:
        health_score = 100
    
    # 问题列表
    issues = [
        {
            "target_name": r.get("target_name", ""),
            "item_name": r.get("item_name", r.get("name", "")),
            "category": r.get("category", ""),
            "status": r.get("status", ""),
            "value": str(r.get("value", r.get("raw_value", ""))),
            "threshold": str(r.get("threshold", "")),
            "suggestion": r.get("suggestion", ""),
        }
        for r in results if r.get("status") in ("warning", "critical", "error")
    ]
    
    # 分类统计
    categories = []
    cat_map = {}
    for r in results:
        cat = r.get("category", "其他")
        if cat not in cat_map:
            cat_map[cat] = {"category": cat, "total": 0, "ok": 0, "warning": 0, "critical": 0}
        cat_map[cat]["total"] += 1
        status = r.get("status", "ok")
        if status in cat_map[cat]:
            cat_map[cat][status] += 1
    categories = list(cat_map.values())
    
    # 摘要
    if critical_count > 0:
        summary = f"巡检发现 {critical_count} 个严重问题、{warning_count} 个警告，健康度评分 {health_score} 分。"
        if issues:
            top_issue = issues[0]
            summary += f" 最严重问题：{top_issue['target_name']} - {top_issue['item_name']}。"
    elif warning_count > 0:
        summary = f"巡检发现 {warning_count} 个警告项，整体运行基本正常，健康度评分 {health_score} 分。"
    else:
        summary = f"所有巡检项均正常，系统运行良好，健康度评分 {health_score} 分。"
    
    # 建议
    recommendations = []
    for issue in issues[:5]:
        if issue.get("suggestion"):
            recommendations.append(f"[{issue['target_name']}] {issue['item_name']}: {issue['suggestion']}")
    
    return InspectionReportData(
        task_name=task_name,
        task_id=task_id,
        target_count=len(targets),
        health_score=health_score,
        total_items=total,
        ok_count=ok_count,
        warning_count=warning_count,
        critical_count=critical_count,
        error_count=error_count,
        skipped_count=skipped_count,
        summary=summary,
        targets=targets,
        results=results,
        issues=issues,
        categories=categories,
        recommendations=recommendations,
        config=config or ReportConfig(),
    )


def build_report_data_from_device_results(
    task_name: str,
    task_id: str,
    device_results: List["DeviceInspectionResult"],
    config: Optional[ReportConfig] = None,
) -> InspectionReportData:
    """从设备巡检结果构建报告数据 (模板化报告)"""
    from .device_templates import DeviceType

    # 统计
    total = 0
    ok_count = 0
    warning_count = 0
    critical_count = 0
    error_count = 0
    skipped_count = 0

    for dr in device_results:
        for sec in dr.sections:
            for item in sec.items:
                total += 1
                status = item.status
                if status == "ok":
                    ok_count += 1
                elif status == "warning":
                    warning_count += 1
                elif status == "critical":
                    critical_count += 1
                elif status == "error":
                    error_count += 1
                elif status == "skipped":
                    skipped_count += 1

    # 健康度评分
    if total > 0:
        health_score = int((ok_count * 100 + warning_count * 50) / total)
    else:
        health_score = 100

    # 问题列表
    issues = []
    for dr in device_results:
        for sec in dr.sections:
            for item in sec.items:
                if item.status in ("warning", "critical", "error"):
                    issues.append({
                        "target_name": dr.device.name,
                        "item_name": item.name,
                        "category": sec.title,
                        "status": item.status,
                        "value": item.raw_value or item.result,
                        "threshold": item.threshold,
                        "suggestion": item.suggestion,
                    })

    # 摘要
    if critical_count > 0:
        summary = f"巡检发现 {critical_count} 个严重问题、{warning_count} 个警告，健康度评分 {health_score} 分。"
    elif warning_count > 0:
        summary = f"巡检发现 {warning_count} 个警告项，整体运行基本正常，健康度评分 {health_score} 分。"
    else:
        summary = f"所有巡检项均正常，系统运行良好，健康度评分 {health_score} 分。"

    # 建议
    recommendations = []
    for issue in issues[:5]:
        if issue.get("suggestion"):
            recommendations.append(f"[{issue['target_name']}] {issue['item_name']}: {issue['suggestion']}")

    targets = [
        {"name": dr.device.name, "type": dr.device.device_type.value, "brand": dr.device.brand}
        for dr in device_results
    ]

    return InspectionReportData(
        task_name=task_name,
        task_id=task_id,
        target_count=len(device_results),
        health_score=health_score,
        total_items=total,
        ok_count=ok_count,
        warning_count=warning_count,
        critical_count=critical_count,
        error_count=error_count,
        skipped_count=skipped_count,
        summary=summary,
        targets=targets,
        results=[],
        issues=issues,
        categories=[],
        recommendations=recommendations,
        config=config or ReportConfig(),
        device_results=device_results,
    )

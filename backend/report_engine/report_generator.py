"""
Acdante ITOps - 报告引擎主入口
统一调用接口，支持生成DOCX和PDF报告
"""

import os
import sys
from . import (
    InspectionReportData, ReportConfig, ReportGenerator,
    build_report_data_from_inspection, OUTPUT_DIR
)

# 暴露所有公共接口
__all__ = [
    'InspectionReportData',
    'ReportConfig',
    'ReportGenerator',
    'build_report_data_from_inspection',
    'generate_report',
    'generate_sample_reports',
    'OUTPUT_DIR',
]


def generate_report(
    task_name: str,
    task_id: str,
    targets: list,
    results: list,
    format: str = "all",
    config: dict = None,
) -> dict:
    """
    生成巡检报告的统一入口
    
    Args:
        task_name: 任务名称
        task_id: 任务ID
        targets: 巡检对象列表
        results: 巡检结果列表
        format: 输出格式 "html", "docx", "pdf", "all"
        config: 报告配置字典
        
    Returns:
        {"report_id": "...", "paths": {"docx": "...", "pdf": "..."}, "health_score": 85, ...}
    """
    # 构建配置
    report_config = ReportConfig()
    if config:
        for key, value in config.items():
            if hasattr(report_config, key):
                setattr(report_config, key, value)
    
    # 构建数据
    data = build_report_data_from_inspection(
        task_name=task_name,
        task_id=task_id,
        targets=targets,
        results=results,
        config=report_config,
    )
    
    # 生成报告
    gen = ReportGenerator(data)
    paths = {}
    
    if format in ("html", "all"):
        try:
            paths['html'] = gen.generate_html()
        except Exception as e:
            paths['html_error'] = str(e)
    
    if format in ("docx", "all"):
        try:
            paths['docx'] = gen.generate_docx()
        except Exception as e:
            paths['docx_error'] = str(e)
    
    if format in ("pdf", "all"):
        try:
            paths['pdf'] = gen.generate_pdf()
        except Exception as e:
            paths['pdf_error'] = str(e)
    
    return {
        "report_id": data.report_id,
        "task_name": data.task_name,
        "task_id": data.task_id,
        "health_score": data.health_score,
        "total_items": data.total_items,
        "ok_count": data.ok_count,
        "warning_count": data.warning_count,
        "critical_count": data.critical_count,
        "summary": data.summary,
        "generated_at": data.generated_at,
        "paths": paths,
        "issues": data.issues,
        "recommendations": data.recommendations,
    }


def generate_sample_reports() -> dict:
    """生成所有格式的示例报告"""
    from .docx_generator import generate_sample_report as gen_docx
    from .pdf_generator import generate_sample_pdf as gen_pdf
    
    paths = {}
    
    try:
        paths['docx'] = gen_docx()
    except Exception as e:
        paths['docx_error'] = str(e)
    
    try:
        paths['pdf'] = gen_pdf()
    except Exception as e:
        paths['pdf_error'] = str(e)
    
    return paths

"""
Acdante ITOps - DOCX 报告生成器
基于 python-docx 生成可编辑的 Word 巡检报告
"""

import os
import io
from datetime import datetime
from typing import Dict, List, Optional
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
from . import InspectionReportData, ReportConfig, OUTPUT_DIR


class DocxGenerator:
    """DOCX报告生成器"""
    
    # 颜色定义
    COLOR_PRIMARY = RGBColor(0x0E, 0x74, 0x9A)    # 青色主题色
    COLOR_DARK = RGBColor(0x1E, 0x29, 0x3B)        # 深色背景
    COLOR_OK = RGBColor(0x16, 0xA3, 0x4A)          # 绿色-正常
    COLOR_WARNING = RGBColor(0xE5, 0xA7, 0x00)      # 琥珀色-警告
    COLOR_CRITICAL = RGBColor(0xDC, 0x26, 0x26)     # 红色-严重
    COLOR_TEXT = RGBColor(0x33, 0x33, 0x33)          # 正文色
    COLOR_MUTED = RGBColor(0x6B, 0x72, 0x80)         # 次要色
    COLOR_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    COLOR_BG_LIGHT = RGBColor(0xF8, 0xFA, 0xFC)
    
    def __init__(self, data: InspectionReportData):
        self.data = data
        self.doc = Document()
        self._setup_styles()
    
    def _setup_styles(self):
        """设置文档样式"""
        style = self.doc.styles['Normal']
        style.font.name = '微软雅黑'
        style.font.size = Pt(10)
        style.font.color.rgb = self.COLOR_TEXT
        style.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
        
        # 设置页边距
        for section in self.doc.sections:
            section.top_margin = Cm(2.5)
            section.bottom_margin = Cm(2.0)
            section.left_margin = Cm(2.5)
            section.right_margin = Cm(2.5)
    
    def _add_heading(self, text: str, level: int = 1):
        """添加标题"""
        heading = self.doc.add_heading(text, level=level)
        for run in heading.runs:
            run.font.name = '微软雅黑'
            run.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
        return heading
    
    def _add_paragraph(self, text: str, bold: bool = False, size: int = 10, color=None, alignment=None):
        """添加段落"""
        para = self.doc.add_paragraph()
        run = para.add_run(text)
        run.font.name = '微软雅黑'
        run.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
        run.font.size = Pt(size)
        run.bold = bold
        if color:
            run.font.color.rgb = color
        if alignment is not None:
            para.alignment = alignment
        return para
    
    def _set_cell_shading(self, cell, color: str):
        """设置单元格背景色"""
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
        cell._tc.get_or_add_tcPr().append(shading_elm)
    
    def _add_table(self, headers: List[str], rows: List[List], col_widths: List = None):
        """添加表格"""
        table = self.doc.add_table(rows=1 + len(rows), cols=len(headers))
        table.style = 'Light Grid Accent 1'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # 表头
        header_cells = table.rows[0].cells
        for i, header in enumerate(headers):
            header_cells[i].text = header
            for para in header_cells[i].paragraphs:
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in para.runs:
                    run.font.bold = True
                    run.font.size = Pt(9)
                    run.font.name = '微软雅黑'
                    run.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
        
        # 数据行
        for r, row in enumerate(rows):
            row_cells = table.rows[r + 1].cells
            for c, val in enumerate(row):
                row_cells[c].text = str(val) if val is not None else ''
                for para in row_cells[c].paragraphs:
                    for run in para.runs:
                        run.font.size = Pt(8)
                        run.font.name = '微软雅黑'
                        run.element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
        
        self.doc.add_paragraph()
        return table
    
    def _generate_cover(self):
        """生成封面页"""
        # 空行调整
        for _ in range(4):
            self.doc.add_paragraph()
        
        # 平台名称
        self._add_paragraph(
            self.data.config.platform_name,
            bold=True, size=14, color=self.COLOR_PRIMARY,
            alignment=WD_ALIGN_PARAGRAPH.CENTER
        )
        
        self.doc.add_paragraph()
        
        # 报告标题
        self._add_paragraph(
            self.data.config.title,
            bold=True, size=26, color=self.COLOR_DARK,
            alignment=WD_ALIGN_PARAGRAPH.CENTER
        )
        
        if self.data.config.subtitle:
            self._add_paragraph(
                self.data.config.subtitle,
                size=14, color=self.COLOR_MUTED,
                alignment=WD_ALIGN_PARAGRAPH.CENTER
            )
        
        self.doc.add_paragraph()
        
        # 分隔线
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run('━' * 40)
        run.font.color.rgb = self.COLOR_PRIMARY
        run.font.size = Pt(10)
        
        self.doc.add_paragraph()
        
        # 报告信息
        info_items = [
            f"巡检任务：{self.data.task_name}",
            f"巡检对象数：{self.data.target_count}",
            f"生成时间：{self.data.generated_at}",
            f"报告编号：{self.data.report_id}",
        ]
        if self.data.config.inspector:
            info_items.insert(2, f"巡检人员：{self.data.config.inspector}")
        if self.data.config.company_name:
            info_items.insert(0, f"单位名称：{self.data.config.company_name}")
        
        for item in info_items:
            self._add_paragraph(
                item, size=11, color=self.COLOR_MUTED,
                alignment=WD_ALIGN_PARAGRAPH.CENTER
            )
        
        # 分页
        self.doc.add_page_break()
    
    def _generate_summary(self):
        """生成摘要页"""
        self._add_heading("巡检概览", level=1)
        
        # 健康度仪表盘
        health_level = "优秀" if self.data.health_score >= 90 else \
                       "良好" if self.data.health_score >= 75 else \
                       "一般" if self.data.health_score >= 60 else "较差"
        health_color = self.COLOR_OK if self.data.health_score >= 90 else \
                       self.COLOR_PRIMARY if self.data.health_score >= 75 else \
                       self.COLOR_WARNING if self.data.health_score >= 60 else self.COLOR_CRITICAL
        
        self._add_paragraph(
            f"健康度评分：{self.data.health_score} / 100  [{health_level}]",
            bold=True, size=14, color=health_color,
            alignment=WD_ALIGN_PARAGRAPH.CENTER
        )
        
        self.doc.add_paragraph()
        
        # 统计卡片
        stats_headers = ["指标", "数值"]
        stats_rows = [
            ["总检查项", str(self.data.total_items)],
            ["✅ 正常", str(self.data.ok_count)],
            ["⚠️ 警告", str(self.data.warning_count)],
            ["🔴 严重", str(self.data.critical_count)],
            ["⏭️ 跳过", str(self.data.skipped_count)],
            ["巡检对象", str(self.data.target_count)],
        ]
        self._add_table(stats_headers, stats_rows)
        
        # 摘要
        self._add_heading("巡检摘要", level=2)
        self._add_paragraph(self.data.summary, size=10)
        
        # 分类统计
        if self.data.categories:
            self._add_heading("分类统计", level=2)
            cat_headers = ["分类", "总数", "正常", "警告", "严重"]
            cat_rows = []
            for cat in self.data.categories:
                cat_rows.append([
                    cat.get("category", ""),
                    str(cat.get("total", 0)),
                    str(cat.get("ok", 0)),
                    str(cat.get("warning", 0)),
                    str(cat.get("critical", 0)),
                ])
            self._add_table(cat_headers, cat_rows)
        
        self.doc.add_page_break()
    
    def _generate_issues(self):
        """生成问题汇总"""
        if not self.data.issues:
            self._add_heading("问题汇总", level=1)
            self._add_paragraph("✅ 未发现任何问题，所有巡检项均正常。", size=11, color=self.COLOR_OK)
            return
        
        self._add_heading("问题汇总", level=1)
        self._add_paragraph(
            f"共发现 {len(self.data.issues)} 个问题（严重: {self.data.critical_count}, 警告: {self.data.warning_count}）",
            size=10, color=self.COLOR_MUTED
        )
        
        # 严重问题优先
        critical_issues = [i for i in self.data.issues if i.get("status") == "critical"]
        warning_issues = [i for i in self.data.issues if i.get("status") == "warning"]
        
        if critical_issues:
            self._add_heading("🔴 严重问题", level=2)
            issue_headers = ["对象", "检查项", "分类", "当前值", "阈值", "建议"]
            issue_rows = []
            for issue in critical_issues:
                issue_rows.append([
                    issue.get("target_name", ""),
                    issue.get("item_name", ""),
                    issue.get("category", ""),
                    issue.get("value", ""),
                    issue.get("threshold", ""),
                    issue.get("suggestion", ""),
                ])
            self._add_table(issue_headers, issue_rows)
        
        if warning_issues:
            self._add_heading("⚠️ 警告问题", level=2)
            issue_headers = ["对象", "检查项", "分类", "当前值", "阈值", "建议"]
            issue_rows = []
            for issue in warning_issues:
                issue_rows.append([
                    issue.get("target_name", ""),
                    issue.get("item_name", ""),
                    issue.get("category", ""),
                    issue.get("value", ""),
                    issue.get("threshold", ""),
                    issue.get("suggestion", ""),
                ])
            self._add_table(issue_headers, issue_rows)
        
        # 建议措施
        if self.data.recommendations:
            self._add_heading("建议措施", level=2)
            for i, rec in enumerate(self.data.recommendations, 1):
                self._add_paragraph(f"{i}. {rec}", size=10)
        
        self.doc.add_page_break()
    
    def _generate_details(self):
        """生成详细结果"""
        self._add_heading("巡检详细结果", level=1)
        
        if not self.data.results:
            self._add_paragraph("暂无详细巡检结果数据。", color=self.COLOR_MUTED)
            return
        
        # 按巡检对象分组
        target_results = {}
        for result in self.data.results:
            target_name = result.get("target_name", "未知")
            if target_name not in target_results:
                target_results[target_name] = []
            target_results[target_name].append(result)
        
        for target_name, results in target_results.items():
            self._add_heading(f"对象：{target_name}", level=2)
            
            detail_headers = ["序号", "检查项", "分类", "原始值", "状态", "建议"]
            detail_rows = []
            for i, r in enumerate(results, 1):
                status = r.get("status", "ok")
                status_label = {"ok": "✅ 正常", "warning": "⚠️ 警告", "critical": "🔴 严重",
                               "error": "❌ 错误", "skipped": "⏭️ 跳过"}.get(status, status)
                detail_rows.append([
                    str(i),
                    r.get("item_name", r.get("name", "")),
                    r.get("category", ""),
                    str(r.get("raw_value", r.get("value", "")))[:80],
                    status_label,
                    r.get("suggestion", "-"),
                ])
            self._add_table(detail_headers, detail_rows)
        
        self.doc.add_page_break()
    
    def _generate_appendix(self):
        """生成附录"""
        self._add_heading("附录", level=1)
        
        self._add_heading("报告信息", level=2)
        app_headers = ["项目", "内容"]
        app_rows = [
            ["报告编号", self.data.report_id],
            ["任务名称", self.data.task_name],
            ["任务ID", self.data.task_id],
            ["生成时间", self.data.generated_at],
            ["平台", self.data.config.platform_name],
            ["报告格式", "DOCX (可编辑)"],
            ["巡检对象数", str(self.data.target_count)],
            ["总检查项", str(self.data.total_items)],
            ["健康度评分", f"{self.data.health_score}/100"],
        ]
        self._add_table(app_headers, app_rows)
        
        # 页脚
        self.doc.add_paragraph()
        self._add_paragraph(
            f"— 本报告由 {self.data.config.platform_name} 自动生成 —",
            size=8, color=self.COLOR_MUTED,
            alignment=WD_ALIGN_PARAGRAPH.CENTER
        )
    
    def generate(self, output_path: str = None) -> str:
        """生成DOCX报告"""
        if not output_path:
            output_path = os.path.join(OUTPUT_DIR, f"{self.data.report_id}.docx")
        
        # 生成封面
        if self.data.config.include_cover:
            self._generate_cover()
        
        # 生成摘要
        self._generate_summary()
        
        # 生成问题汇总
        self._generate_issues()
        
        # 生成详细结果
        self._generate_details()
        
        # 生成附录
        if self.data.config.include_appendix:
            self._generate_appendix()
        
        # 保存
        self.doc.save(output_path)
        return output_path


def generate_sample_report() -> str:
    """生成示例报告用于测试"""
    from . import InspectionReportData, ReportConfig, build_report_data_from_inspection
    
    # 构建模拟数据
    targets = [
        {"name": "生产核心交换机-A", "type": "network", "brand": "华为"},
        {"name": "ORACLE-PROD-DB1", "type": "oracle", "brand": "Oracle"},
        {"name": "APP-SERVER-01", "type": "linux", "brand": "Dell"},
    ]
    
    results = [
        {"target_name": "生产核心交换机-A", "item_name": "CPU使用率", "category": "CPU",
         "raw_value": "15%", "value": 15, "status": "ok", "weight": 20, "threshold": ">70%告警", "suggestion": ""},
        {"target_name": "生产核心交换机-A", "item_name": "内存使用率", "category": "内存",
         "raw_value": "62%", "value": 62, "status": "ok", "weight": 20, "threshold": ">70%告警", "suggestion": ""},
        {"target_name": "生产核心交换机-A", "item_name": "设备温度", "category": "硬件",
         "raw_value": "68°C", "value": 68, "status": "warning", "weight": 10, "threshold": ">60°C告警",
         "suggestion": "检查机房空调，关注设备散热"},
        {"target_name": "ORACLE-PROD-DB1", "item_name": "数据库实例状态", "category": "实例",
         "raw_value": "OPEN/ACTIVE", "value": "OPEN", "status": "ok", "weight": 20, "threshold": "", "suggestion": ""},
        {"target_name": "ORACLE-PROD-DB1", "item_name": "表空间使用率", "category": "存储",
         "raw_value": "USERS: 92.5%", "value": 92.5, "status": "warning", "weight": 20, "threshold": ">85%告警",
         "suggestion": "USERS表空间使用率偏高，建议扩容或清理数据"},
        {"target_name": "ORACLE-PROD-DB1", "item_name": "锁阻塞检测", "category": "锁",
         "raw_value": "SID 156阻塞3个会话", "value": "1个阻塞源", "status": "critical", "weight": 20,
         "threshold": ">0告警", "suggestion": "检查SID 156会话，必要时Kill该会话"},
        {"target_name": "APP-SERVER-01", "item_name": "CPU使用率", "category": "CPU",
         "raw_value": "45.2%", "value": 45.2, "status": "ok", "weight": 20, "threshold": ">70%告警", "suggestion": ""},
        {"target_name": "APP-SERVER-01", "item_name": "磁盘使用率", "category": "磁盘",
         "raw_value": "/data 91%", "value": 91, "status": "warning", "weight": 20, "threshold": ">80%告警",
         "suggestion": "/data分区使用率91%，建议清理或扩容"},
        {"target_name": "APP-SERVER-01", "item_name": "内存使用率", "category": "内存",
         "raw_value": "72%", "value": 72, "status": "ok", "weight": 20, "threshold": ">80%告警", "suggestion": ""},
        {"target_name": "APP-SERVER-01", "item_name": "系统日志错误", "category": "安全",
         "raw_value": "3条错误", "value": 3, "status": "ok", "weight": 10, "threshold": "", "suggestion": ""},
    ]
    
    config = ReportConfig(
        title="每日IT基础设施巡检报告",
        subtitle="2024年Q4巡检季报",
        company_name="XX科技有限公司",
        inspector="系统管理员",
    )
    
    data = build_report_data_from_inspection(
        task_name="每日综合巡检",
        task_id="task-daily-001",
        targets=targets,
        results=results,
        config=config,
    )
    
    gen = DocxGenerator(data)
    return gen.generate()

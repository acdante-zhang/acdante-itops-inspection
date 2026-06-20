"""
Acdante ITOps - PDF 报告生成器
基于 WeasyPrint + Jinja2 模板引擎生成PDF巡检报告
"""

import os
import io
from datetime import datetime
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import InspectionReportData, ReportConfig, OUTPUT_DIR, TEMPLATES_DIR


# ============================================================
# HTML/CSS 报告模板（内联版本，无需外部文件）
# ============================================================

REPORT_CSS = """
@page {
  size: A4;
  margin: 2cm 2.2cm;
  @top-center {
    content: string(title);
    font-size: 9px;
    color: #94a3b8;
    font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  }
  @bottom-center {
    content: counter(page);
    font-size: 9px;
    color: #94a3b8;
    font-family: 'Microsoft YaHei', '微软雅黑', sans-serif;
  }
}
@page cover {
  @top-center { content: none; }
  @bottom-center { content: none; }
  margin: 0;
}

body {
  font-family: 'Microsoft YaHei', '微软雅黑', 'Noto Sans CJK SC', 'SimHei', sans-serif;
  font-size: 10pt;
  line-height: 1.6;
  color: #333;
}

.cover-page {
  page: cover;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #0f172a 100%);
  color: #fff;
  text-align: center;
  padding: 4cm 2cm;
}
.cover-platform {
  font-size: 14pt;
  color: #22d3ee;
  margin-bottom: 20px;
  letter-spacing: 4px;
  text-transform: uppercase;
}
.cover-title {
  font-size: 28pt;
  font-weight: bold;
  margin-bottom: 10px;
  color: #f1f5f9;
}
.cover-subtitle {
  font-size: 14pt;
  color: #94a3b8;
  margin-bottom: 30px;
}
.cover-divider {
  width: 200px;
  height: 2px;
  background: #22d3ee;
  margin: 20px auto;
}
.cover-info {
  font-size: 10pt;
  color: #cbd5e1;
  line-height: 2;
  margin-top: 30px;
}
.cover-footer {
  position: absolute;
  bottom: 2cm;
  font-size: 8pt;
  color: #64748b;
}

h1 {
  font-size: 18pt;
  color: #1e293b;
  border-bottom: 2px solid #22d3ee;
  padding-bottom: 8px;
  margin-top: 30px;
  string-set: title content();
}
h2 {
  font-size: 14pt;
  color: #334155;
  margin-top: 20px;
  padding-left: 10px;
  border-left: 4px solid #22d3ee;
}
h3 {
  font-size: 12pt;
  color: #475569;
  margin-top: 15px;
}

.health-score {
  text-align: center;
  padding: 20px;
  margin: 20px 0;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
.health-score .score {
  font-size: 48pt;
  font-weight: bold;
}
.health-score .level {
  font-size: 14pt;
  margin-top: 5px;
}

.stats-grid {
  display: flex;
  gap: 12px;
  margin: 16px 0;
  flex-wrap: wrap;
}
.stat-card {
  flex: 1;
  min-width: 100px;
  padding: 12px;
  border-radius: 6px;
  text-align: center;
  border: 1px solid #e2e8f0;
}
.stat-card .value {
  font-size: 20pt;
  font-weight: bold;
}
.stat-card .label {
  font-size: 8pt;
  color: #64748b;
  margin-top: 4px;
}
.stat-ok { background: #f0fdf4; border-color: #bbf7d0; }
.stat-ok .value { color: #16a34a; }
.stat-warning { background: #fffbeb; border-color: #fde68a; }
.stat-warning .value { color: #e5a700; }
.stat-critical { background: #fef2f2; border-color: #fecaca; }
.stat-critical .value { color: #dc2626; }
.stat-info { background: #f0f9ff; border-color: #bae6fd; }
.stat-info .value { color: #0e749a; }

table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  font-size: 9pt;
}
th {
  background: #f1f5f9;
  padding: 8px 6px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #cbd5e1;
  color: #475569;
}
td {
  padding: 6px;
  border-bottom: 1px solid #e2e8f0;
}
tr:nth-child(even) {
  background: #f8fafc;
}

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 7pt;
  font-weight: bold;
}
.badge-ok { background: #dcfce7; color: #166534; }
.badge-warning { background: #fef3c7; color: #92400e; }
.badge-critical { background: #fecaca; color: #991b1b; }
.badge-error { background: #fee2e2; color: #991b1b; }
.badge-skipped { background: #f1f5f9; color: #64748b; }

.issue-card {
  padding: 12px;
  margin: 8px 0;
  border-radius: 6px;
  border-left: 4px solid;
}
.issue-critical { background: #fef2f2; border-color: #dc2626; }
.issue-warning { background: #fffbeb; border-color: #eab308; }
.issue-title { font-weight: bold; font-size: 10pt; margin-bottom: 4px; }
.issue-detail { font-size: 8pt; color: #64748b; }
.issue-suggestion { color: #0e749a; font-size: 8pt; margin-top: 4px; }

.summary-box {
  padding: 16px;
  background: #f8fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  margin: 12px 0;
  font-size: 10pt;
}

.recommendation {
  padding: 8px 12px;
  margin: 4px 0;
  background: #f0f9ff;
  border-radius: 4px;
  font-size: 9pt;
}

.page-break {
  page-break-before: always;
}

.footer-note {
  text-align: center;
  color: #94a3b8;
  font-size: 8pt;
  margin-top: 30px;
  padding-top: 15px;
  border-top: 1px solid #e2e8f0;
}
"""

REPORT_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{{ config.title }}</title>
<style>{{ css }}</style>
</head>
<body>

<!-- 封面 -->
<section class="cover-page">
  <div class="cover-platform">{{ config.platform_name }}</div>
  <div class="cover-title">{{ config.title }}</div>
  {% if config.subtitle %}
  <div class="cover-subtitle">{{ config.subtitle }}</div>
  {% endif %}
  <div class="cover-divider"></div>
  <div class="cover-info">
    {% if config.company_name %}<div>单位名称：{{ config.company_name }}</div>{% endif %}
    <div>巡检任务：{{ task_name }}</div>
    <div>巡检对象数：{{ target_count }}</div>
    {% if config.inspector %}<div>巡检人员：{{ config.inspector }}</div>{% endif %}
    <div>生成时间：{{ generated_at }}</div>
    <div>报告编号：{{ report_id }}</div>
  </div>
  <div class="cover-footer">{{ config.platform_name }} &copy; {{ generated_at[:4] }}</div>
</section>

<!-- 摘要 -->
<div class="page-break"></div>
<h1>巡检概览</h1>

<div class="health-score">
  <div class="score" style="color: {{ health_color }}">{{ health_score }}</div>
  <div class="level" style="color: {{ health_color }}">健康度评分 / 100 [{{ health_level }}]</div>
</div>

<div class="stats-grid">
  <div class="stat-card stat-ok">
    <div class="value">{{ ok_count }}</div>
    <div class="label">✅ 正常</div>
  </div>
  <div class="stat-card stat-warning">
    <div class="value">{{ warning_count }}</div>
    <div class="label">⚠️ 警告</div>
  </div>
  <div class="stat-card stat-critical">
    <div class="value">{{ critical_count }}</div>
    <div class="label">🔴 严重</div>
  </div>
  <div class="stat-card stat-info">
    <div class="value">{{ total_items }}</div>
    <div class="label">总检查项</div>
  </div>
</div>

<h2>巡检摘要</h2>
<div class="summary-box">{{ summary }}</div>

{% if categories %}
<h2>分类统计</h2>
<table>
  <tr><th>分类</th><th>总数</th><th>正常</th><th>警告</th><th>严重</th></tr>
  {% for cat in categories %}
  <tr>
    <td>{{ cat.category }}</td>
    <td>{{ cat.total }}</td>
    <td>{{ cat.ok }}</td>
    <td>{{ cat.warning }}</td>
    <td>{{ cat.critical }}</td>
  </tr>
  {% endfor %}
</table>
{% endif %}

<!-- 问题汇总 -->
<div class="page-break"></div>
<h1>问题汇总</h1>

{% if issues %}
<p style="color:#64748b">共发现 {{ issues|length }} 个问题（严重: {{ critical_count }}, 警告: {{ warning_count }}）</p>

{% set critical_issues = issues|selectattr("status", "equalto", "critical")|list %}
{% if critical_issues %}
<h2>🔴 严重问题</h2>
{% for issue in critical_issues %}
<div class="issue-card issue-critical">
  <div class="issue-title">{{ issue.target_name }} — {{ issue.item_name }}</div>
  <div class="issue-detail">当前值: {{ issue.value }} | 阈值: {{ issue.threshold }} | 分类: {{ issue.category }}</div>
  {% if issue.suggestion %}<div class="issue-suggestion">💡 建议: {{ issue.suggestion }}</div>{% endif %}
</div>
{% endfor %}
{% endif %}

{% set warning_issues = issues|selectattr("status", "equalto", "warning")|list %}
{% if warning_issues %}
<h2>⚠️ 警告问题</h2>
{% for issue in warning_issues %}
<div class="issue-card issue-warning">
  <div class="issue-title">{{ issue.target_name }} — {{ issue.item_name }}</div>
  <div class="issue-detail">当前值: {{ issue.value }} | 阈值: {{ issue.threshold }} | 分类: {{ issue.category }}</div>
  {% if issue.suggestion %}<div class="issue-suggestion">💡 建议: {{ issue.suggestion }}</div>{% endif %}
</div>
{% endfor %}
{% endif %}

{% if recommendations %}
<h2>建议措施</h2>
{% for rec in recommendations %}
<div class="recommendation">{{ loop.index }}. {{ rec }}</div>
{% endfor %}
{% endif %}

{% else %}
<div class="summary-box" style="color:#16a34a">✅ 未发现任何问题，所有巡检项均正常。</div>
{% endif %}

<!-- 详细结果 -->
<div class="page-break"></div>
<h1>巡检详细结果</h1>

{% for target_name, target_results in target_groups.items() %}
<h2>对象：{{ target_name }}</h2>
<table>
  <tr><th>#</th><th>检查项</th><th>分类</th><th>原始值</th><th>状态</th><th>建议</th></tr>
  {% for r in target_results %}
  <tr>
    <td>{{ loop.index }}</td>
    <td>{{ r.item_name or r.name }}</td>
    <td>{{ r.category }}</td>
    <td style="font-family:monospace;font-size:8pt">{{ (r.raw_value or r.value)|string|truncate(60) }}</td>
    <td><span class="badge badge-{{ r.status }}">{{ status_labels[r.status] }}</span></td>
    <td style="font-size:8pt">{{ r.suggestion or '-' }}</td>
  </tr>
  {% endfor %}
</table>
{% endfor %}

<!-- 附录 -->
{% if config.include_appendix %}
<div class="page-break"></div>
<h1>附录</h1>
<h2>报告信息</h2>
<table>
  <tr><td style="width:30%">报告编号</td><td>{{ report_id }}</td></tr>
  <tr><td>任务名称</td><td>{{ task_name }}</td></tr>
  <tr><td>任务ID</td><td>{{ task_id }}</td></tr>
  <tr><td>生成时间</td><td>{{ generated_at }}</td></tr>
  <tr><td>平台</td><td>{{ config.platform_name }}</td></tr>
  <tr><td>报告格式</td><td>PDF</td></tr>
  <tr><td>巡检对象数</td><td>{{ target_count }}</td></tr>
  <tr><td>总检查项</td><td>{{ total_items }}</td></tr>
  <tr><td>健康度评分</td><td>{{ health_score }}/100</td></tr>
</table>

<div class="footer-note">— 本报告由 {{ config.platform_name }} 自动生成 —</div>
{% endif %}

</body>
</html>"""


class PDFGenerator:
    """PDF报告生成器"""
    
    def __init__(self, data: InspectionReportData):
        self.data = data
    
    def _get_status_labels(self) -> Dict[str, str]:
        return {
            "ok": "✅ 正常",
            "warning": "⚠️ 警告",
            "critical": "🔴 严重",
            "error": "❌ 错误",
            "skipped": "⏭️ 跳过",
        }
    
    def _get_health_info(self) -> tuple:
        """获取健康度信息和颜色"""
        score = self.data.health_score
        if score >= 90:
            return "优秀", "#22c55e"
        elif score >= 75:
            return "良好", "#3b82f6"
        elif score >= 60:
            return "一般", "#eab308"
        else:
            return "较差", "#ef4444"
    
    def _group_results_by_target(self) -> Dict[str, List[Dict]]:
        """按巡检对象分组结果"""
        groups = {}
        for result in self.data.results:
            target_name = result.get("target_name", "未知")
            if target_name not in groups:
                groups[target_name] = []
            groups[target_name].append(result)
        return groups
    
    def render_html(self) -> str:
        """渲染HTML报告"""
        from jinja2 import Template
        
        health_level, health_color = self._get_health_info()
        target_groups = self._group_results_by_target()
        
        template = Template(REPORT_HTML_TEMPLATE)
        return template.render(
            css=REPORT_CSS,
            config=self.data.config,
            task_name=self.data.task_name,
            task_id=self.data.task_id,
            target_count=self.data.target_count,
            health_score=self.data.health_score,
            health_level=health_level,
            health_color=health_color,
            total_items=self.data.total_items,
            ok_count=self.data.ok_count,
            warning_count=self.data.warning_count,
            critical_count=self.data.critical_count,
            skipped_count=self.data.skipped_count,
            summary=self.data.summary,
            generated_at=self.data.generated_at,
            report_id=self.data.report_id,
            targets=self.data.targets,
            results=self.data.results,
            issues=self.data.issues,
            categories=self.data.categories,
            recommendations=self.data.recommendations,
            target_groups=target_groups,
            status_labels=self._get_status_labels(),
        )
    
    def generate(self, output_path: str = None) -> str:
        """生成PDF报告"""
        if not output_path:
            output_path = os.path.join(OUTPUT_DIR, f"{self.data.report_id}.pdf")
        
        html_content = self.render_html()
        
        try:
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(output_path)
        except Exception as e:
            # 如果weasyprint不可用，保存HTML文件作为备选
            html_path = output_path.replace('.pdf', '.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            raise RuntimeError(f"PDF生成失败(已保存HTML备选): {str(e)}")
        
        return output_path


def generate_sample_pdf() -> str:
    """生成示例PDF报告"""
    from . import InspectionReportData, ReportConfig, build_report_data_from_inspection
    
    targets = [
        {"name": "生产核心交换机-A", "type": "network", "brand": "华为"},
        {"name": "ORACLE-PROD-DB1", "type": "oracle", "brand": "Oracle"},
        {"name": "APP-SERVER-01", "type": "linux", "brand": "Dell"},
        {"name": "SAN-SWITCH-A", "type": "san_switch", "brand": "Brocade"},
    ]
    
    results = [
        {"target_name": "生产核心交换机-A", "item_name": "CPU使用率", "category": "CPU",
         "raw_value": "15%", "value": 15, "status": "ok", "weight": 20, "threshold": ">70%告警", "suggestion": ""},
        {"target_name": "生产核心交换机-A", "item_name": "内存使用率", "category": "内存",
         "raw_value": "62%", "value": 62, "status": "ok", "weight": 20, "threshold": ">70%告警", "suggestion": ""},
        {"target_name": "生产核心交换机-A", "item_name": "设备温度", "category": "硬件",
         "raw_value": "68°C", "value": 68, "status": "warning", "weight": 10, "threshold": ">60°C告警",
         "suggestion": "检查机房空调，关注设备散热"},
        {"target_name": "生产核心交换机-A", "item_name": "风扇状态", "category": "硬件",
         "raw_value": "正常", "value": "OK", "status": "ok", "weight": 10, "threshold": "", "suggestion": ""},
        {"target_name": "ORACLE-PROD-DB1", "item_name": "数据库实例状态", "category": "实例",
         "raw_value": "OPEN/ACTIVE", "value": "OPEN", "status": "ok", "weight": 20, "threshold": "", "suggestion": ""},
        {"target_name": "ORACLE-PROD-DB1", "item_name": "表空间使用率", "category": "存储",
         "raw_value": "USERS: 92.5%", "value": 92.5, "status": "warning", "weight": 20, "threshold": ">85%告警",
         "suggestion": "USERS表空间使用率偏高，建议扩容或清理数据"},
        {"target_name": "ORACLE-PROD-DB1", "item_name": "锁阻塞检测", "category": "锁",
         "raw_value": "SID 156阻塞3个会话，持锁时间600s", "value": "1个阻塞源", "status": "critical", "weight": 20,
         "threshold": ">0即告警", "suggestion": "检查SID 156会话是否正常，必要时Kill该会话"},
        {"target_name": "ORACLE-PROD-DB1", "item_name": "活跃会话数", "category": "会话",
         "raw_value": "245", "value": 245, "status": "ok", "weight": 10, "threshold": ">300告警", "suggestion": ""},
        {"target_name": "APP-SERVER-01", "item_name": "CPU使用率", "category": "CPU",
         "raw_value": "45.2%", "value": 45.2, "status": "ok", "weight": 20, "threshold": ">70%告警", "suggestion": ""},
        {"target_name": "APP-SERVER-01", "item_name": "磁盘使用率", "category": "磁盘",
         "raw_value": "/data 91%", "value": 91, "status": "warning", "weight": 20, "threshold": ">80%告警",
         "suggestion": "/data分区使用率91%，建议清理或扩容"},
        {"target_name": "APP-SERVER-01", "item_name": "内存使用率", "category": "内存",
         "raw_value": "72%", "value": 72, "status": "ok", "weight": 20, "threshold": ">80%告警", "suggestion": ""},
        {"target_name": "SAN-SWITCH-A", "item_name": "交换机状态", "category": "系统",
         "raw_value": "HEALTHY", "value": "HEALTHY", "status": "ok", "weight": 10, "threshold": "", "suggestion": ""},
        {"target_name": "SAN-SWITCH-A", "item_name": "端口CRC错误", "category": "端口",
         "raw_value": "0", "value": 0, "status": "ok", "weight": 20, "threshold": ">10告警", "suggestion": ""},
        {"target_name": "SAN-SWITCH-A", "item_name": "SFP模块状态", "category": "硬件",
         "raw_value": "全部正常", "value": "OK", "status": "ok", "weight": 15, "threshold": "", "suggestion": ""},
    ]
    
    config = ReportConfig(
        title="每日IT基础设施巡检报告",
        subtitle="2024年度第四季度综合巡检",
        company_name="XX科技有限公司",
        inspector="运维管理员",
    )
    
    data = build_report_data_from_inspection(
        task_name="每日综合巡检",
        task_id="task-daily-001",
        targets=targets,
        results=results,
        config=config,
    )
    
    gen = PDFGenerator(data)
    return gen.generate()

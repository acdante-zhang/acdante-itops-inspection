"""
Acdante ITOps - 巡检结果分析器
自动分析巡检结果，生成建议
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """分析结果"""
    summary: str
    health_score: int
    issues: List[Dict]
    recommendations: List[str]
    risk_level: str  # low, medium, high, critical


class ResultAnalyzer:
    """巡检结果分析器"""

    # 问题严重性权重
    SEVERITY_WEIGHTS = {
        "critical": 0,
        "warning": 60,
        "error": 50,
        "ok": 100,
    }

    # 常见问题解决方案
    SOLUTIONS = {
        "cpu_usage": {
            "critical": [
                "检查占用CPU最高的进程: top -bn1 | head -20",
                "分析进程是否存在异常: ps aux --sort=-%cpu | head -10",
                "考虑优化应用代码或增加CPU资源",
            ],
            "warning": [
                "监控CPU使用趋势",
                "检查是否有定时任务在运行",
            ],
        },
        "mem_usage": {
            "critical": [
                "检查内存占用最高的进程: ps aux --sort=-%mem | head -10",
                "检查是否存在内存泄漏",
                "考虑增加物理内存或优化应用",
            ],
            "warning": [
                "监控内存使用趋势",
                "检查Swap使用情况",
            ],
        },
        "disk_usage": {
            "critical": [
                "定位大文件: du -sh /* | sort -rh | head -10",
                "清理旧日志: find /var/log -name '*.gz' -delete",
                "清理临时文件: rm -rf /tmp/*",
                "考虑扩容磁盘",
            ],
            "warning": [
                "设置日志轮转",
                "定期清理临时文件",
            ],
        },
        "gpu_usage": {
            "critical": [
                "检查GPU进程: nvidia-smi",
                "清理僵尸进程: kill -9 <pid>",
                "降低推理batch_size",
            ],
            "warning": [
                "监控GPU使用趋势",
                "检查是否有任务排队",
            ],
        },
        "gpu_memory": {
            "critical": [
                "检查显存泄漏: nvidia-smi --query-compute-apps=pid,used_memory",
                "重启推理服务",
                "降低模型精度(FP16→INT8)",
            ],
            "warning": [
                "监控显存使用趋势",
                "检查是否有并发请求过多",
            ],
        },
        "gpu_temperature": {
            "critical": [
                "检查机房环境温度",
                "检查服务器风扇状态",
                "降低GPU功耗限制",
            ],
            "warning": [
                "监控温度趋势",
                "检查散热系统",
            ],
        },
    }

    def analyze(self, results: List[Dict]) -> AnalysisResult:
        """分析巡检结果"""
        if not results:
            return AnalysisResult(
                summary="无巡检结果",
                health_score=100,
                issues=[],
                recommendations=[],
                risk_level="low",
            )

        # 统计
        total = len(results)
        ok_count = sum(1 for r in results if r.get("status") == "ok")
        warning_count = sum(1 for r in results if r.get("status") == "warning")
        critical_count = sum(1 for r in results if r.get("status") == "critical")
        error_count = sum(1 for r in results if r.get("status") == "error")

        # 计算健康分数
        health_score = self._calculate_health_score(results)

        # 提取问题
        issues = []
        for r in results:
            if r.get("status") in ("warning", "critical"):
                issues.append({
                    "item_name": r.get("item_name", ""),
                    "category": r.get("category", ""),
                    "status": r.get("status"),
                    "value": str(r.get("raw_value", ""))[:100],
                    "suggestion": r.get("suggestion", ""),
                })

        # 生成建议
        recommendations = self._generate_recommendations(results)

        # 确定风险级别
        if critical_count > 0:
            risk_level = "critical"
        elif warning_count > 3:
            risk_level = "high"
        elif warning_count > 0:
            risk_level = "medium"
        else:
            risk_level = "low"

        # 生成摘要
        if critical_count > 0:
            summary = f"发现 {critical_count} 个严重问题，需立即处理"
        elif warning_count > 0:
            summary = f"发现 {warning_count} 个警告，建议关注"
        elif error_count > 0:
            summary = f"有 {error_count} 个巡检项执行失败"
        else:
            summary = "巡检正常，未发现异常"

        return AnalysisResult(
            summary=summary,
            health_score=health_score,
            issues=issues,
            recommendations=recommendations,
            risk_level=risk_level,
        )

    def _calculate_health_score(self, results: List[Dict]) -> int:
        """计算健康分数"""
        if not results:
            return 100

        total_weight = 0
        weighted_score = 0

        for r in results:
            weight = r.get("weight", 10)
            status = r.get("status", "ok")
            score = self.SEVERITY_WEIGHTS.get(status, 50)
            weighted_score += weight * score
            total_weight += weight

        if total_weight == 0:
            return 100

        return int(weighted_score / total_weight)

    def _generate_recommendations(self, results: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []

        for r in results:
            if r.get("status") not in ("warning", "critical"):
                continue

            item_name = r.get("item_name", "").lower()
            status = r.get("status")

            # 匹配常见问题
            for key, solutions in self.SOLUTIONS.items():
                if key in item_name or key.replace("_", " ") in item_name:
                    if status in solutions:
                        recommendations.extend(solutions[status])
                        break

            # 使用模板建议
            if r.get("suggestion") and r["suggestion"] not in recommendations:
                recommendations.append(r["suggestion"])

        # 去重
        return list(dict.fromkeys(recommendations))[:10]


# 全局分析器
result_analyzer = ResultAnalyzer()

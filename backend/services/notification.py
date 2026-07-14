"""
Acdante ITOps - 通知服务
支持邮件/Webhook通知
"""

import logging
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NotificationConfig:
    """通知配置"""
    email_enabled: bool = False
    email_smtp_host: str = ""
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_from: str = ""
    webhook_enabled: bool = False
    webhook_url: str = ""


class NotificationService:
    """通知服务"""

    def __init__(self, config: NotificationConfig = None):
        self.config = config or NotificationConfig()

    def send_email(self, to: List[str], subject: str, body: str) -> bool:
        """发送邮件通知"""
        if not self.config.email_enabled:
            logger.info("邮件通知未启用")
            return False

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg["From"] = self.config.email_from
            msg["To"] = ", ".join(to)
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(self.config.email_smtp_host, self.config.email_smtp_port) as server:
                server.starttls()
                server.login(self.config.email_username, self.config.email_password)
                server.sendmail(self.config.email_from, to, msg.as_string())

            logger.info(f"邮件已发送: {to}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False

    def send_webhook(self, data: Dict) -> bool:
        """发送Webhook通知"""
        if not self.config.webhook_enabled:
            logger.info("Webhook通知未启用")
            return False

        try:
            import httpx
            with httpx.Client(timeout=10) as client:
                resp = client.post(
                    self.config.webhook_url,
                    json=data,
                    headers={"Content-Type": "application/json"},
                )
                if resp.status_code < 300:
                    logger.info(f"Webhook已发送: {self.config.webhook_url}")
                    return True
                else:
                    logger.warning(f"Webhook响应异常: {resp.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Webhook发送失败: {e}")
            return False

    def notify_inspection_result(self, task_name: str, result: Dict, recipients: List[str]):
        """发送巡检结果通知"""
        health_score = result.get("health_score", 0)
        critical = result.get("critical_count", 0)
        warning = result.get("warning_count", 0)

        if critical > 0:
            level = "🔴 严重"
            color = "#ef4444"
        elif warning > 0:
            level = "🟡 警告"
            color = "#f59e0b"
        else:
            level = "🟢 正常"
            color = "#22c55e"

        subject = f"[Acdante ITOps] {level} - {task_name} 巡检报告"

        html_body = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: {color}; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                <h2 style="margin: 0;">{level} {task_name}</h2>
            </div>
            <div style="padding: 20px; border: 1px solid #e2e8f0; border-radius: 0 0 8px 8px;">
                <p><strong>健康分数:</strong> {health_score}/100</p>
                <p><strong>严重问题:</strong> {critical} 个</p>
                <p><strong>警告:</strong> {warning} 个</p>
                <p><strong>正常:</strong> {result.get('ok_count', 0)} 个</p>
                <hr style="border: none; border-top: 1px solid #e2e8f0;">
                <p style="color: #64748b; font-size: 12px;">
                    Acdante ITOps Inspection Platform
                </p>
            </div>
        </div>
        """

        # 发送邮件
        if recipients:
            self.send_email(recipients, subject, html_body)

        # 发送Webhook
        self.send_webhook({
            "event": "inspection_completed",
            "task_name": task_name,
            "health_score": health_score,
            "critical_count": critical,
            "warning_count": warning,
            "ok_count": result.get("ok_count", 0),
        })


# 全局通知服务
notification_service = NotificationService()

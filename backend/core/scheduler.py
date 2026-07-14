"""
Acdante ITOps - 巡检任务调度器
基于 APScheduler 实现定时巡检任务
"""

import logging
import time
from typing import Dict, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

logger = logging.getLogger(__name__)


class TaskScheduler:
    """巡检任务调度器"""

    SCHEDULE_MAP = {
        "hourly": {"trigger": "interval", "hours": 1},
        "daily": {"trigger": "cron", "hour": 8, "minute": 0},
        "weekly": {"trigger": "cron", "day_of_week": "mon", "hour": 8, "minute": 0},
        "monthly": {"trigger": "cron", "day": 1, "hour": 8, "minute": 0},
        "every_5min": {"trigger": "interval", "minutes": 5},
        "every_30min": {"trigger": "interval", "minutes": 30},
        "every_6h": {"trigger": "interval", "hours": 6},
    }

    def __init__(self):
        self._scheduler = BackgroundScheduler(
            job_defaults={"coalesce": True, "max_instances": 1}
        )
        self._running = False

    def start(self):
        """启动调度器"""
        if not self._running:
            self._scheduler.start()
            self._running = True
            logger.info("巡检任务调度器已启动")

    def stop(self):
        """停止调度器"""
        if self._running:
            self._scheduler.shutdown(wait=False)
            self._running = False
            logger.info("巡检任务调度器已停止")

    def add_task(self, task_id: str, schedule_type: str, callback, **kwargs):
        """
        添加定时任务
        schedule_type: hourly, daily, weekly, monthly, every_5min, every_30min, every_6h, manual, once
        """
        # 先移除已有任务
        self.remove_task(task_id)

        if schedule_type == "manual":
            logger.info(f"任务 {task_id} 为手动触发，不注册调度")
            return

        if schedule_type == "once":
            # 一次性任务，立即执行
            self._scheduler.add_job(
                callback, trigger="date",
                run_date=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                id=task_id, kwargs={"task_id": task_id, **kwargs}
            )
            logger.info(f"任务 {task_id} 已注册为一次性执行")
            return

        schedule_cfg = self.SCHEDULE_MAP.get(schedule_type)
        if not schedule_cfg:
            logger.warning(f"未知调度类型: {schedule_type}")
            return

        trigger_type = schedule_cfg["trigger"]
        if trigger_type == "interval":
            trigger = IntervalTrigger(
                hours=schedule_cfg.get("hours", 0),
                minutes=schedule_cfg.get("minutes", 0),
            )
        elif trigger_type == "cron":
            trigger = CronTrigger(
                hour=schedule_cfg.get("hour"),
                minute=schedule_cfg.get("minute"),
                day_of_week=schedule_cfg.get("day_of_week"),
                day=schedule_cfg.get("day"),
            )
        else:
            logger.warning(f"未知触发器类型: {trigger_type}")
            return

        self._scheduler.add_job(
            callback, trigger=trigger, id=task_id,
            kwargs={"task_id": task_id, **kwargs},
            replace_existing=True,
        )
        logger.info(f"任务 {task_id} 已注册调度: {schedule_type}")

    def remove_task(self, task_id: str):
        """移除任务"""
        try:
            self._scheduler.remove_job(task_id)
        except Exception:
            pass

    def run_task_now(self, task_id: str, callback, **kwargs):
        """立即执行任务"""
        self._scheduler.add_job(
            callback, trigger="date",
            run_date=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            id=f"{task_id}-manual-{int(time.time())}",
            kwargs={"task_id": task_id, **kwargs},
        )
        logger.info(f"任务 {task_id} 已触发立即执行")

    def get_jobs(self):
        """获取所有调度任务"""
        jobs = []
        for job in self._scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "next_run_time": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
        return jobs


# 全局调度器实例
task_scheduler = TaskScheduler()

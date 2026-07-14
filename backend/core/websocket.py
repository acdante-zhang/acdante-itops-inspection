"""
Acdante ITOps - 实时巡检进度 WebSocket 支持
"""

import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}  # task_id -> set of websockets
        self._global: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, task_id: str = None):
        await websocket.accept()
        if task_id:
            if task_id not in self._connections:
                self._connections[task_id] = set()
            self._connections[task_id].add(websocket)
        else:
            self._global.add(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str = None):
        if task_id and task_id in self._connections:
            self._connections[task_id].discard(websocket)
        self._global.discard(websocket)

    async def broadcast_task_progress(self, task_id: str, data: dict):
        """广播任务进度"""
        message = json.dumps(data, ensure_ascii=False)
        targets = self._connections.get(task_id, set()) | self._global
        disconnected = set()
        for ws in targets:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.add(ws)
        for ws in disconnected:
            self.disconnect(ws, task_id)

    async def broadcast_alert(self, alert: dict):
        """广播告警"""
        message = json.dumps(alert, ensure_ascii=False)
        disconnected = set()
        for ws in self._global:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.add(ws)
        for ws in disconnected:
            self._global.discard(ws)


# 全局连接管理器
ws_manager = ConnectionManager()

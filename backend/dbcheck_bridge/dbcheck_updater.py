"""
Acdante ITOps — DBCheck 版本更新管理器
支持检查更新、自动更新、版本回退
"""

import os
import json
import subprocess
from datetime import datetime
from typing import Dict, Optional

from .dbcheck_config import DBCHECK_BASE_PATH


class DBCheckUpdater:
    """DBCheck版本更新管理器"""
    
    def __init__(self, dbcheck_path: str = None):
        self.dbcheck_path = dbcheck_path or DBCHECK_BASE_PATH
        self._git_available = os.path.exists(os.path.join(self.dbcheck_path, ".git"))
    
    def get_current_version(self) -> str:
        """获取当前安装的DBCheck版本"""
        version_file = os.path.join(self.dbcheck_path, "version.json")
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                data = json.load(f)
                return data.get("version", "unknown")
        
        try:
            from version import __version__
            return __version__
        except ImportError:
            pass
        
        return "unknown"
    
    def get_current_commit(self) -> str:
        """获取当前git commit"""
        if not self._git_available:
            return "unknown (非git安装)"
        
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.dbcheck_path,
                capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"
    
    def check_for_updates(self) -> Dict:
        """检查是否有可用更新"""
        if not self._git_available:
            return {
                "update_available": False,
                "reason": "非git安装模式，无法自动检查更新",
                "current_version": self.get_current_version(),
                "latest_version": "unknown",
                "checked_at": datetime.now().isoformat(),
            }
        
        try:
            # 获取远程更新
            subprocess.run(
                ["git", "fetch", "origin"],
                cwd=self.dbcheck_path,
                capture_output=True, text=True, timeout=30
            )
            
            current_commit = self.get_current_commit()
            
            # 检查是否有新commit
            result = subprocess.run(
                ["git", "rev-parse", "--short", "origin/main"],
                cwd=self.dbcheck_path,
                capture_output=True, text=True, timeout=10
            )
            latest_commit = result.stdout.strip()
            
            has_update = latest_commit and latest_commit != current_commit
            
            return {
                "update_available": has_update,
                "current_version": self.get_current_version(),
                "current_commit": current_commit,
                "latest_commit": latest_commit,
                "checked_at": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "update_available": False,
                "error": str(e),
                "current_version": self.get_current_version(),
                "checked_at": datetime.now().isoformat(),
            }
    
    def update(self) -> Dict:
        """更新到最新版本"""
        if not self._git_available:
            return {
                "success": False,
                "message": "非git安装模式，请手动下载最新版本替换 vendor/dbcheck/ 目录",
            }
        
        try:
            # 记录更新前版本
            old_version = self.get_current_version()
            old_commit = self.get_current_commit()
            
            # 拉取最新代码
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.dbcheck_path,
                capture_output=True, text=True, timeout=60
            )
            
            new_version = self.get_current_version()
            new_commit = self.get_current_commit()
            
            success = new_commit != old_commit
            
            return {
                "success": success,
                "old_version": old_version,
                "new_version": new_version,
                "old_commit": old_commit,
                "new_commit": new_commit,
                "output": result.stdout[:500],
                "message": f"已从 {old_version} 更新到 {new_version}" if success else "已是最新版本",
                "updated_at": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"更新失败: {str(e)}",
                "error": str(e),
            }
    
    def rollback(self, target: str = "HEAD~1") -> Dict:
        """回退到指定版本"""
        if not self._git_available:
            return {
                "success": False,
                "message": "非git安装模式，不支持版本回退",
            }
        
        try:
            old_version = self.get_current_version()
            
            result = subprocess.run(
                ["git", "checkout", target],
                cwd=self.dbcheck_path,
                capture_output=True, text=True, timeout=30
            )
            
            new_version = self.get_current_version()
            
            return {
                "success": True,
                "old_version": old_version,
                "new_version": new_version,
                "message": f"已回退到 {new_version}",
                "rolled_back_at": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"回退失败: {str(e)}",
            }
    
    def get_changelog(self) -> str:
        """获取CHANGELOG"""
        changelog_path = os.path.join(self.dbcheck_path, "CHANGELOG.md")
        if os.path.exists(changelog_path):
            with open(changelog_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "CHANGELOG.md 不存在"
    
    def get_update_instructions(self) -> str:
        """获取更新说明"""
        if self._git_available:
            return """## DBCheck 更新方法

### 自动更新（推荐）
1. 在ITOps管理界面点击"检查更新"
2. 如有新版本，点击"更新"按钮
3. 系统自动执行 git pull 并重载模板

### 手动更新
```bash
cd vendor/dbcheck
git pull origin main
```

### 版本锁定
如需锁定特定版本：
```bash
cd vendor/dbcheck
git checkout v2.5.0  # 替换为目标版本号
```
"""
        else:
            return """## DBCheck 更新方法

当前为非git安装模式。要更新DBCheck：
1. 从 https://github.com/fiyo/DBCheck 下载最新版本
2. 替换 vendor/dbcheck/ 目录
3. 重启ITOps平台服务
"""

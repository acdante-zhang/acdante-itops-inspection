"""
Acdante ITOps - 数据库初始化脚本
用于首次部署时初始化数据库和内置数据
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import init_db, seed_builtin_templates, get_db, get_targets, get_templates


def main():
    print("Acdante ITOps - 数据库初始化")
    print("=" * 40)

    # 初始化表结构
    print("\n[1] 初始化数据库表结构...")
    init_db()
    print("  ✅ 表结构已创建")

    # 写入内置模板
    print("\n[2] 写入内置巡检模板...")
    seed_builtin_templates()
    templates = get_templates()
    print(f"  ✅ {len(templates)} 个模板已加载:")
    for t in templates:
        items = t.get("items", [])
        print(f"     - {t['id']}: {t['name']} ({len(items)} 项)")

    # 验证
    print("\n[3] 验证数据库...")
    targets = get_targets()
    print(f"  巡检对象: {len(targets)} 个")
    print(f"  巡检模板: {len(templates)} 个")

    print("\n" + "=" * 40)
    print("✅ 数据库初始化完成!")
    print(f"数据库路径: {os.path.join(os.path.dirname(__file__), '..', 'backend', 'data', 'itops.db')}")


if __name__ == "__main__":
    main()

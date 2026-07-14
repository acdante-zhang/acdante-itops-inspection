"""
Acdante ITOps - SSH连接测试脚本
用于验证SSH巡检引擎是否正常工作
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.ssh_executor import SSHExecutor, SSHConfig, SSHAuthType, HAS_PARAMIKO


def test_ssh_connection(host, port=22, username="root", password=""):
    """测试SSH连接"""
    print(f"\n{'='*60}")
    print(f"SSH连接测试: {host}:{port}")
    print(f"paramiko可用: {HAS_PARAMIKO}")
    print(f"{'='*60}")

    config = SSHConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        timeout=10,
        device_type="linux",
    )

    executor = SSHExecutor(config)

    # 测试连接
    print("\n[1] 测试SSH连接...")
    result = executor.test_connection()
    if result["success"]:
        print(f"  ✅ 连接成功: {result['message']}")
        print(f"  耗时: {result['connect_time_ms']:.0f}ms")
        if result.get("system_info"):
            print(f"  系统信息: {result['system_info'][:100]}")
    else:
        print(f"  ❌ 连接失败: {result['message']}")
        return False

    # 测试命令执行
    print("\n[2] 测试命令执行...")
    commands = [
        {"command": "hostname", "name": "主机名", "timeout": 5},
        {"command": "uptime", "name": "运行时间", "timeout": 5},
        {"command": "free -m | head -2", "name": "内存信息", "timeout": 5},
        {"command": "nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader 2>/dev/null || echo 'No GPU'",
         "name": "GPU信息", "timeout": 10},
    ]

    inspect_result = executor.execute_batch(commands)

    print(f"\n  连接状态: {'✅ 已连接' if inspect_result.connected else '❌ 未连接'}")
    print(f"  总命令数: {inspect_result.total_commands}")
    print(f"  成功: {inspect_result.success_count}")
    print(f"  失败: {inspect_result.error_count}")
    print(f"  总耗时: {inspect_result.total_duration_ms:.0f}ms")

    for cmd in inspect_result.commands:
        status_icon = "✅" if cmd.status == "success" else "❌"
        print(f"\n  {status_icon} {cmd.command}:")
        if cmd.status == "success":
            for line in cmd.stdout.split("\n")[:5]:
                print(f"     {line}")
        else:
            print(f"     错误: {cmd.error_message}")

    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python test_ssh.py <host> [port] [username] [password]")
        print("示例: python test_ssh.py 192.168.1.100 22 root mypassword")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 22
    username = sys.argv[3] if len(sys.argv) > 3 else "root"
    password = sys.argv[4] if len(sys.argv) > 4 else ""

    test_ssh_connection(host, port, username, password)

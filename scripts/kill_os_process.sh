#!/bin/bash
# AcdanteSQLMon 系统级进程查杀脚本
# 当 ALTER SYSTEM KILL SESSION 失败时使用
# 用法: ./kill_os_process.sh <spid> [oracle_sid]

set -e

SPID=$1
ORACLE_SID=${2:-ORCL}

if [ -z "$SPID" ]; then
    echo "用法: $0 <spid> [oracle_sid]"
    echo ""
    echo "说明:"
    echo "  spid        - Oracle 服务进程 ID (从 GV\$PROCESS.SPID 获取)"
    echo "  oracle_sid  - Oracle 实例名 (默认: ORCL)"
    echo ""
    echo "安全检查:"
    echo "  1. 确认进程属于 oracle 用户"
    echo "  2. 先尝试 kill -15 (优雅终止)"
    echo "  3. 失败后使用 kill -9 (强制终止)"
    exit 1
fi

echo "=== AcdanteSQLMon 系统级进程查杀 ==="
echo "目标 SPID: $SPID"
echo "Oracle SID: $ORACLE_SID"
echo ""

# 验证进程是否存在
PROCESS_INFO=$(ps -p "$SPID" -o pid,user,comm,args 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "[ERROR] 进程 $SPID 不存在"
    exit 1
fi

echo "进程信息:"
echo "$PROCESS_INFO"
echo ""

# 安全检查: 确认是 oracle 进程
PROCESS_USER=$(ps -p "$SPID" -o user= 2>/dev/null)
if [[ "$PROCESS_USER" != "oracle" && "$PROCESS_USER" != "grid" ]]; then
    echo "[ERROR] 进程 $SPID 不属于 oracle/grid 用户 (属主: $PROCESS_USER)"
    echo "        为安全起见，拒绝查杀非 Oracle 进程"
    exit 1
fi

# 先尝试 kill -15 (graceful)
echo "尝试优雅终止 (kill -15)..."
kill -15 "$SPID" 2>/dev/null
sleep 3

# 检查是否还在
if ps -p "$SPID" > /dev/null 2>&1; then
    echo "[WARN] 进程仍在运行，尝试强制终止 (kill -9)..."
    kill -9 "$SPID" 2>/dev/null
    sleep 1

    if ps -p "$SPID" > /dev/null 2>&1; then
        echo "[ERROR] 无法终止进程 $SPID"
        exit 1
    else
        echo "[OK] 进程 $SPID 已强制终止"
    fi
else
    echo "[OK] 进程 $SPID 已优雅终止"
fi

echo ""
echo "注意: 系统级查杀后，Oracle 内部会话状态可能残留"
echo "      建议在数据库中执行: ALTER SYSTEM KILL SESSION 'sid,serial#,@inst_id' IMMEDIATE;"
echo "      以清理 PMON 进程残留"

#!/bin/bash
# AcdanteSQLMon 一键启动脚本
# 启动前端 + Go API 网关 + Rust 数据引擎

PROJECT_DIR="/workspace/projects"
LOG_DIR="/app/work/logs/bypass"
mkdir -p "$LOG_DIR"

echo "========================================="
echo "  AcdanteSQLMon 启动中..."
echo "========================================="

# 1. 启动 Rust 数据引擎 (端口 8081)
echo "[1/3] 启动 Rust 数据引擎..."
cd "$PROJECT_DIR/rust-engine"
if [ -f "target/release/acdante-sqlmon-engine" ]; then
    (nohup ./target/release/acdante-sqlmon-engine > "$LOG_DIR/rust-engine.log" 2>&1 &)
    echo "  Rust 引擎已启动 (release模式)"
elif [ -f "target/debug/acdante-sqlmon-engine" ]; then
    (nohup ./target/debug/acdante-sqlmon-engine > "$LOG_DIR/rust-engine.log" 2>&1 &)
    echo "  Rust 引擎已启动 (debug模式)"
else
    echo "  [WARN] Rust 引擎未编译，跳过"
    echo "  编译: cd rust-engine && cargo build --release"
fi

sleep 2

# 2. 启动 Go API 网关 (端口 8080)
echo "[2/3] 启动 Go API 网关..."
cd "$PROJECT_DIR/go-server"
if [ -f "acdante-sqlmon" ]; then
    (nohup ./acdante-sqlmon > "$LOG_DIR/go-api.log" 2>&1 &)
    echo "  Go API 网关已启动"
else
    echo "  [WARN] Go API 网关未编译，尝试 go run..."
    (nohup go run . > "$LOG_DIR/go-api.log" 2>&1 &)
    echo "  Go API 网关已启动 (go run模式)"
fi

sleep 2

# 3. 启动前端 (端口 5000) - 必须在前台运行，coze dev 依赖此进程
echo "[3/3] 启动前端开发服务器..."
cd "$PROJECT_DIR"
exec pnpm next dev -p 5000

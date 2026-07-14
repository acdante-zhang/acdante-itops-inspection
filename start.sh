#!/bin/bash
# Acdante ITOps Inspection Platform - 启动脚本
# 同时启动 Next.js 前端 + Python 后端

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ============================================================
# 配置
# ============================================================
PYTHON_PORT=${PYTHON_API_PORT:-8000}
NEXT_PORT=${NEXT_PORT:-5000}
PYTHON_API_URL="http://127.0.0.1:${PYTHON_PORT}"

# ============================================================
# 颜色
# ============================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============================================================
# 清理函数
# ============================================================
cleanup() {
    log_info "正在停止服务..."
    if [ -n "$PYTHON_PID" ]; then
        kill "$PYTHON_PID" 2>/dev/null || true
        log_info "Python后端已停止 (PID: $PYTHON_PID)"
    fi
    if [ -n "$NEXT_PID" ]; then
        kill "$NEXT_PID" 2>/dev/null || true
        log_info "Next.js前端已停止 (PID: $NEXT_PID)"
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# ============================================================
# 安装Python依赖
# ============================================================
install_python_deps() {
    log_info "检查Python依赖..."
    if ! python3 -c "import fastapi" 2>/dev/null; then
        log_warn "安装Python依赖..."
        pip install -r backend/requirements.txt 2>/dev/null || pip install --user -r backend/requirements.txt
    fi
    log_info "Python依赖已就绪"
}

# ============================================================
# 启动Python后端
# ============================================================
start_python_backend() {
    log_info "启动Python后端 (端口: $PYTHON_PORT)..."
    PYTHON_API_PORT=$PYTHON_PORT python3 -m backend.main &
    PYTHON_PID=$!
    log_info "Python后端已启动 (PID: $PYTHON_PID)"

    # 等待后端就绪
    for i in $(seq 1 30); do
        if curl -s "http://127.0.0.1:${PYTHON_PORT}/api/v1/health" >/dev/null 2>&1; then
            log_info "Python后端就绪 ✓"
            return 0
        fi
        sleep 1
    done
    log_warn "Python后端启动超时，继续启动前端..."
}

# ============================================================
# 启动Next.js前端
# ============================================================
start_nextjs_frontend() {
    log_info "启动Next.js前端 (端口: $NEXT_PORT)..."
    PYTHON_API_URL=$PYTHON_API_URL NEXT_PORT=$NEXT_PORT npx next dev -p $NEXT_PORT &
    NEXT_PID=$!
    log_info "Next.js前端已启动 (PID: $NEXT_PID)"
}

# ============================================================
# 主流程
# ============================================================
log_info "=========================================="
log_info " Acdante ITOps Inspection Platform"
log_info "=========================================="
log_info " Python后端: http://127.0.0.1:$PYTHON_PORT"
log_info " Next.js前端: http://127.0.0.1:$NEXT_PORT"
log_info "=========================================="

install_python_deps
start_python_backend
start_nextjs_frontend

log_info "所有服务已启动，按 Ctrl+C 停止"
wait

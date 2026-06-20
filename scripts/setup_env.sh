#!/bin/bash
# AcdanteSQLMon 环境检测与部署脚本
# 检测运行所需的所有依赖和环境配置

set -e

echo "========================================="
echo "  AcdanteSQLMon 环境检测"
echo "========================================="
echo ""

# 检查 Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "[OK] Python: $PYTHON_VERSION"
else
    echo "[ERROR] Python3 not found"
    exit 1
fi

# 检查 oracledb 模块
python3 -c "import oracledb; print(f'[OK] oracledb: {oracledb.__version__}')" 2>/dev/null || {
    echo "[WARN] oracledb not installed"
    echo "       Install: pip3 install oracledb"
}

# 检查 cx_Oracle
python3 -c "import cx_Oracle; print(f'[OK] cx_Oracle: {cx_Oracle.__version__}')" 2>/dev/null || {
    echo "[INFO] cx_Oracle not installed (optional, 10g/11g may need it)"
}

# 检查 Oracle Instant Client
check_instant_client() {
    local SEARCH_PATHS=(
        "/usr/lib/oracle"
        "/opt/oracle/instantclient"
        "/usr/local/lib"
        "$HOME/oracle/instantclient"
        "/opt/oracle/instantclient_19_8"
        "/opt/oracle/instantclient_11_2"
    )

    for path in "${SEARCH_PATHS[@]}"; do
        if [ -f "$path/libclntsh.so" ] || [ -d "$path" ] && find "$path" -name "libclntsh.so" -print -quit 2>/dev/null | grep -q .; then
            echo "[OK] Instant Client found: $path"
            return 0
        fi
    done

    echo "[WARN] Oracle Instant Client not found"
    echo "       Required for Oracle 10g/11g connections"
    echo "       Download: https://www.oracle.com/database/technologies/instant-client/downloads.html"
    return 1
}

check_instant_client || true

# 检查 Go 环境
if command -v go &> /dev/null; then
    echo "[OK] Go: $(go version)"
else
    echo "[ERROR] Go not found"
fi

# 检查 Rust 环境
if command -v cargo &> /dev/null; then
    echo "[OK] Rust: $(cargo --version)"
else
    echo "[ERROR] Rust not found"
fi

# 检查 Node.js
if command -v node &> /dev/null; then
    echo "[OK] Node.js: $(node --version)"
else
    echo "[ERROR] Node.js not found"
fi

# 检查端口占用
echo ""
echo "--- 端口检测 ---"
for port in 5000 8080 8081; do
    if ss -tuln 2>/dev/null | grep -q ":$port "; then
        echo "[INFO] Port $port: 已占用"
    else
        echo "[INFO] Port $port: 可用"
    fi
done

echo ""
echo "========================================="
echo "  环境检测完成"
echo "========================================="

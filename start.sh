#!/bin/bash

echo "========================================"
echo "NewAPI 健康监控服务启动脚本"
echo "========================================"

cd "$(dirname "$0")"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3"
    exit 1
fi

# 安装依赖
echo "[1/3] 安装依赖..."
pip3 install -q -r requirements.txt

# 创建数据目录
mkdir -p data

# 启动监控 Agent
echo "[2/3] 启动监控 Agent..."
nohup python3 -m monitor.agent --config config.yaml --daemon > monitor.log 2>&1 &
AGENT_PID=$!
echo "Agent PID: $AGENT_PID"

# 等待 Agent 启动
sleep 2

# 启动 Web 服务
echo "[3/3] 启动 Web 看板服务..."
nohup python3 -m web.app > web.log 2>&1 &
WEB_PID=$!
echo "Web PID: $WEB_PID"

echo ""
echo "========================================"
echo "服务已启动！"
echo "  - 监控 Agent: 每3分钟测试一次 (8:00-18:00)"
echo "  - Web 看板: http://localhost:5000"
echo ""
echo "日志文件: monitor.log, web.log"
echo "========================================"

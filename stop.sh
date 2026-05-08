#!/bin/bash

echo "========================================"
echo "NewAPI 健康监控服务停止脚本"
echo "========================================"

pkill -f "python3 -m monitor.agent" 2>/dev/null
pkill -f "python3 -m web.app" 2>/dev/null

echo "已停止所有服务进程"

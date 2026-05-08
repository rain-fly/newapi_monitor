@echo off
chcp 65001 > nul
echo ========================================
echo NewAPI 健康监控服务停止脚本
echo ========================================

taskkill /F /IM python.exe > nul 2>&1

echo 已停止所有 Python 进程
pause

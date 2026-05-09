@echo off
chcp 65001 > nul
echo ========================================
echo NewAPI 健康监控服务停止脚本
echo ========================================

cd /d "%~dp0"
python run.py stop
pause

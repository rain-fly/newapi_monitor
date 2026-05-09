@echo off
chcp 65001 > nul
echo ========================================
echo NewAPI 健康监控服务启动脚本
echo ========================================

cd /d "%~dp0"

python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

python run.py start
pause

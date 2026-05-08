@echo off
chcp 65001 > nul
echo ========================================
echo NewAPI 健康监控服务启动脚本
echo ========================================

cd /d "%~dp0"

REM 检查 Python 是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

REM 安装依赖
echo [1/3] 安装依赖...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

REM 创建数据目录
if not exist "data" mkdir data

REM 启动监控 Agent
echo [2/3] 启动监控 Agent (守护进程模式)...
start /B cmd /c "python -m monitor.agent --config config.yaml --daemon > monitor.log 2>&1"

REM 等待 Agent 启动
timeout /t 2 /nobreak > nul

REM 启动 Web 服务
echo [3/3] 启动 Web 看板服务...
start /B cmd /c "python -c \"import os, sys; sys.path.insert(0, os.getcwd()); from web.app import app; app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)\" > web.log 2>&1"

echo.
echo ========================================
echo 服务已启动！
echo   - 监控 Agent: 每3分钟测试一次 (8:00-18:00)
echo   - Web 看板: http://localhost:5000
echo.
echo 日志文件: monitor.log, web.log
echo ========================================

pause

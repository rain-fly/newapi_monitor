#!/usr/bin/env python
"""
调试启动脚本 - 直接在当前进程运行，方便 PyCharm 调试
用法:
  python debug.py        同时启动 Agent 和 Web
  python debug.py agent  仅启动监控 Agent
  python debug.py web    仅启动 Web 看板
"""
import os
import sys
import threading
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def run_agent():
    """运行监控 Agent"""
    os.chdir(BASE_DIR)
    # 通过 sys.argv 传递参数，并跳过信号注册
    sys.argv = ["monitor.agent", "--config", "config.yaml", "--no-signal"]
    from monitor.agent import main
    main()


def run_web():
    """运行 Web 看板"""
    os.chdir(BASE_DIR)
    from web.app import app, load_config
    cfg = load_config()
    port = cfg.get("web", {}).get("port", 5000)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    # 安装依赖
    print("[1/2] 检查依赖...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])

    os.makedirs("data", exist_ok=True)

    if cmd == "agent":
        print("[2/2] 启动监控 Agent (调试模式)...")
        run_agent()
    elif cmd == "web":
        print("[2/2] 启动 Web 看板 (调试模式)...")
        run_web()
    elif cmd == "all":
        print("[2/2] 同时启动 Agent 和 Web (调试模式)...")
        # Web 在后台线程运行（因为 Flask 会阻塞）
        web_thread = threading.Thread(target=run_web, daemon=True)
        web_thread.start()
        time.sleep(1)  # 等 Web 启动
        # Agent 在主线程运行（需要注册信号）
        run_agent()
    else:
        print(f"用法: python debug.py [agent|web|all]")
        sys.exit(1)


if __name__ == "__main__":
    main()

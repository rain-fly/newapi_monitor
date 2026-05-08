#!/usr/bin/env python
"""
NewAPI Monitor 启动入口
同时启动 Web 看板服务和健康监控 Agent
"""
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monitor.config import load_config
from monitor.database import Database
from monitor.adapter import NewAPIAdapter
from monitor.agent import HealthMonitor


def main():
    config_path = os.environ.get("CONFIG_PATH", "config.yaml")
    config = load_config(config_path)

    # 启动健康监控 Agent（后台线程）
    monitor = HealthMonitor(config_path)
    monitor.start()

    # 启动 Flask Web 服务（主线程阻塞）
    from web.app import app

    web_config = config.web
    host = web_config.get("host", "0.0.0.0")
    port = web_config.get("port", 5000)
    print(f"启动 Web 看板服务 on {host}:{port}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()

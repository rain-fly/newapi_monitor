import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify
from datetime import datetime

from monitor.config import load_config
from monitor.database import Database

# 获取 web 目录的绝对路径
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=os.path.join(WEB_DIR, 'templates'))
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# 加载配置
config_path = os.environ.get("CONFIG_PATH", "config.yaml")
config = load_config(config_path)
db = Database(config.database.get("path", "data/monitor.db"))


def calculate_availability(records):
    """计算可用性百分比"""
    if not records:
        return 0.0
    available_count = sum(1 for r in records if r["available"])
    return (available_count / len(records)) * 100


@app.route("/")
def index():
    """看板主页"""
    return render_template("index.html")


@app.route("/api/models")
def api_models():
    """获取所有模型及其最新状态，按可用性↑和延迟↑排序"""
    latest_by_model = db.get_latest_record_by_model()

    # 获取所有历史模型
    all_models = db.get_all_models()

    model_list = []
    for model in all_models:
        if model in latest_by_model:
            record = latest_by_model[model]
            model_list.append({
                "model": model,
                "available": record["available"],
                "latency_ms": record["latency_ms"],
                "timestamp": record["timestamp"],
                "error": record["error_message"]
            })
        else:
            model_list.append({
                "model": model,
                "available": None,
                "latency_ms": None,
                "timestamp": None,
                "error": "暂无数据"
            })

    # 排序：可用性降序（True排前面），延迟升序（低的排前面）
    model_list.sort(key=lambda x: (
        x["available"] is not True,  # False/None 排后面
        x["latency_ms"] if x["latency_ms"] is not None else float('inf')
    ))

    return jsonify({
        "models": model_list,
        "count": len(model_list)
    })


@app.route("/api/status")
def api_status():
    """实时状态 API - 返回所有模型的最新状态"""
    latest_by_model = db.get_latest_record_by_model()

    result = {}
    for model, record in latest_by_model.items():
        result[model] = {
            "available": record["available"],
            "latency_ms": record["latency_ms"],
            "timestamp": record["timestamp"],
            "error": record["error_message"]
        }

    return jsonify(result)


@app.route("/api/models/<model_name>/availability")
def api_model_availability(model_name):
    """获取指定模型的各时间窗口可用性"""
    windows = {
        "3min": 3,
        "30min": 30,
        "3h": 180,
        "6h": 360,
        "12h": 720,
        "24h": 1440
    }

    result = {}
    for name, minutes in windows.items():
        records = db.get_recent_records(minutes, model_name)
        result[name] = {
            "availability": calculate_availability(records),
            "record_count": len(records)
        }

    return jsonify(result)


@app.route("/api/models/<model_name>/history")
def api_model_history(model_name):
    """获取指定模型的历史数据"""
    records = db.get_all_recent_records(24, model_name)
    return jsonify({
        "model": model_name,
        "records": records,
        "count": len(records)
    })


@app.route("/api/availability")
def api_availability():
    """多时间窗口可用性 API - 按模型分组"""
    windows = {
        "3min": 3,
        "30min": 30,
        "3h": 180,
        "6h": 360,
        "12h": 720,
        "24h": 1440
    }

    all_models = db.get_all_models()

    result = {}
    for model in all_models:
        model_stats = {}
        for name, minutes in windows.items():
            records = db.get_recent_records(minutes, model)
            model_stats[name] = {
                "availability": calculate_availability(records),
                "record_count": len(records)
            }
        result[model] = model_stats

    return jsonify(result)


@app.route("/api/history")
def api_history():
    """历史数据 API - 返回过去24小时的数据（按模型分组）"""
    all_models = db.get_all_models()

    result = {}
    for model in all_models:
        records = db.get_all_recent_records(24, model)
        result[model] = {
            "records": records,
            "count": len(records)
        }

    return jsonify(result)


def main():
    web_config = config.web
    host = web_config.get("host", "0.0.0.0")
    port = web_config.get("port", 5000)
    print(f"启动 Web 看板服务 on {host}:{port}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()

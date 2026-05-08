import os
import sys
import time

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify, request
from datetime import datetime
import json
import requests as http_requests

from monitor.config import load_config
from monitor.database import Database

# 获取 web 目录的绝对路径
WEB_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
           template_folder=os.path.join(WEB_DIR, 'templates'),
           static_folder=os.path.join(WEB_DIR, 'static'),
           static_url_path='/static')
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


def _parse_tags(tags_data):
    """解析模型标签数据"""
    if not tags_data:
        return None
    return {
        "vendor": tags_data.get("vendor"),
        "use_cases": json.loads(tags_data.get("use_cases", "[]")) if tags_data.get("use_cases") else [],
        "language_strengths": json.loads(tags_data.get("language_strengths", "[]")) if tags_data.get("language_strengths") else []
    }


def _tag_matches(tags, vendor=None, use_case=None, lang=None):
    """检查标签是否匹配过滤条件"""
    if not tags:
        return False
    if vendor and tags.get("vendor", "").lower() != vendor.lower():
        return False
    if use_case and use_case.lower() not in [u.lower() for u in tags.get("use_cases", [])]:
        return False
    if lang and lang.lower() not in [l.lower() for l in tags.get("language_strengths", [])]:
        return False
    return True


@app.route("/api/models")
def api_models():
    """获取所有模型及其最新状态，按可用性↑和延迟↑排序"""
    vendor_filter = request.args.get("vendor")
    use_case_filter = request.args.get("use_case")
    lang_filter = request.args.get("lang")
    has_tag_filter = vendor_filter or use_case_filter or lang_filter

    latest_by_model = db.get_latest_record_by_model()
    all_models = db.get_all_models()

    model_list = []
    for model in all_models:
        tags_data = db.get_model_tags(model)
        tags = _parse_tags(tags_data)

        if has_tag_filter and not _tag_matches(tags, vendor_filter, use_case_filter, lang_filter):
            continue

        item = {}
        if model.lower() in latest_by_model:
            record = latest_by_model[model.lower()]
            item = {
                "model": record["model"],  # 保留原始大小写
                "available": record["available"],
                "latency_ms": record["latency_ms"],
                "timestamp": record["timestamp"],
                "error": record["error_message"],
                "tags": tags
            }
        else:
            item = {
                "model": model,  # 保留原始大小写
                "available": None,
                "latency_ms": None,
                "timestamp": None,
                "error": "暂无数据",
                "tags": tags
            }
        model_list.append(item)

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
        tags_data = db.get_model_tags(model)
        tags = _parse_tags(tags_data)
        result[model] = {
            "available": record["available"],
            "latency_ms": record["latency_ms"],
            "timestamp": record["timestamp"],
            "error": record["error_message"],
            "tags": tags
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


@app.route("/api/tags")
def api_tags():
    """标签云 API - 返回所有唯一标签及计数"""
    return jsonify(db.get_all_tags())


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


@app.route("/api/models/<model_name>/test", methods=["POST"])
def api_model_test(model_name):
    """即时测试指定模型，直接返回原始响应"""
    endpoint = config.newapi["endpoint"].rstrip("/")
    api_key = config.newapi["api_key"]
    timeout = min(config.newapi.get("timeout", 10), 30)

    start_time = time.time()
    try:
        response = http_requests.post(
            f"{endpoint}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model_name, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 50},
            timeout=timeout
        )
        latency_ms = (time.time() - start_time) * 1000

        try:
            raw = response.json()
        except Exception:
            raw = response.text[:500]

        return jsonify({
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "latency_ms": round(latency_ms, 1),
            "raw": raw
        })
    except http_requests.Timeout:
        return jsonify({"success": False, "latency_ms": None, "raw": f"请求超时 ({timeout}s)"})
    except Exception as e:
        return jsonify({"success": False, "latency_ms": None, "raw": str(e)})


def main():
    web_config = config.web
    host = web_config.get("host", "0.0.0.0")
    port = web_config.get("port", 5000)
    print(f"启动 Web 看板服务 on {host}:{port}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()

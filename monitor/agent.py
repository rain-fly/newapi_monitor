import schedule
import time
import threading
import signal
import sys
from datetime import datetime
from typing import Optional, List

from monitor.config import load_config
from monitor.database import Database
from monitor.adapter import NewAPIAdapter


class HealthMonitor:
    """健康监控 Agent"""

    def __init__(self, config_path: str = None):
        self.config = load_config(config_path)
        self.db = Database(self.config.database.get("path", "data/monitor.db"))
        self.adapter = NewAPIAdapter(
            endpoint=self.config.newapi.get("endpoint"),
            api_key=self.config.newapi.get("api_key"),
            timeout=self.config.newapi.get("timeout", 10)
        )
        self.interval_minutes = self.config.scheduler.get("interval_minutes", 3)
        self.start_hour = self.config.scheduler.get("time_window", {}).get("start_hour", 8)
        self.end_hour = self.config.scheduler.get("time_window", {}).get("end_hour", 18)
        self.retention_days = self.config.retention.get("days", 30)
        self._running = False
        self._thread = None
        self._models: Optional[List[str]] = None
        self._failed_consecutive: int = 0
        self._classify_lock = threading.Lock()
        self._classifier_model = self.config.classifier.get("model")

    def is_within_time_window(self) -> bool:
        """检查当前时间是否在工作时间窗口内"""
        current_hour = datetime.now().hour
        return self.start_hour <= current_hour < self.end_hour

    def cleanup_old_data(self):
        """清理旧数据"""
        deleted = self.db.cleanup_old_records(self.retention_days)
        if deleted > 0:
            print(f"[{datetime.now().isoformat()}] 清理了 {deleted} 条超过 {self.retention_days} 天的旧记录")

    def get_models(self) -> List[str]:
        """获取模型列表，从 API 获取并与数据库历史合并"""
        # 从 API 获取最新模型列表
        api_models = set(self.adapter.get_available_models())

        # 合并数据库历史模型（确保新模型被添加）
        db_models = set(self.db.get_all_models())

        all_models = list(api_models | db_models)
        return sorted(all_models)

    def refresh_models(self):
        """强制刷新模型列表"""
        self._models = None
        self._models = self.get_models()
        self._failed_consecutive = 0

    def run_test(self):
        """执行一次 API 可用性测试"""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] 开始执行 API 可用性测试...")

        if not self.is_within_time_window():
            print(f"[{timestamp}] 当前时间不在工作时间窗口内（{self.start_hour}:00-{self.end_hour}:00），跳过测试")
            return

        # 获取模型列表（每次测试都刷新）
        self._models = self.get_models()
        print(f"[{timestamp}] 获取到 {len(self._models)} 个模型: {', '.join(self._models)}")

        if not self._models:
            print(f"[{timestamp}] 未找到任何模型，跳过测试")
            return

        # 遍历每个模型进行测试
        for model in self._models:
            test_timestamp = datetime.now().isoformat()
            print(f"[{test_timestamp}] 测试模型: {model}")

            available, latency_ms, error_msg, retry_count = self.adapter.test_connection(model)

            if available:
                print(f"[{test_timestamp}] {model} 测试成功 - 延迟: {latency_ms:.2f}ms")
            else:
                print(f"[{test_timestamp}] {model} 测试失败 - 错误: {error_msg}")

                # 如果是 model_not_found，增加连续失败计数
                if error_msg and "model_not_found" in error_msg:
                    self._failed_consecutive += 1
                    if self._failed_consecutive >= 3:
                        print(f"[{test_timestamp}] 连续失败次数过多，刷新模型列表...")
                        self.refresh_models()

            # 记录测试结果
            self.db.insert_record(available, latency_ms, error_msg, retry_count, model)

        # 分类未标记的模型
        self._classify_uncategorized_models()

    def _classify_uncategorized_models(self):
        """对未分类的模型进行 AI 分类"""
        if not self._classifier_model:
            return

        uncategorized = self.db.get_uncategorized_models()
        if not uncategorized:
            return

        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] 发现 {len(uncategorized)} 个未分类模型，开始 AI 分类...")

        for model in uncategorized:
            if not self._classify_lock.acquire(blocking=False):
                print(f"[{timestamp}] 分类锁已被占用，跳过本轮分类")
                return
            try:
                # 再次检查，防止并发重复分类
                if self.db.get_model_tags(model):
                    continue

                classify_ts = datetime.now().isoformat()
                print(f"[{classify_ts}] 正在分类模型: {model} (使用 {self._classifier_model})")

                result = self.adapter.classify_model(model, self._classifier_model)
                self.db.upsert_model_tags(
                    model=model,
                    vendor=result["vendor"],
                    use_cases=result["use_cases"],
                    language_strengths=result["language_strengths"],
                    raw_response=result["raw_response"]
                )
                print(f"[{classify_ts}] {model} 分类完成: vendor={result['vendor']}")
            except Exception as e:
                print(f"[{datetime.now().isoformat()}] 分类 {model} 失败: {e}")
            finally:
                self._classify_lock.release()

    def start(self):
        """启动监控服务"""
        print(f"[{datetime.now().isoformat()}] 启动健康监控服务...")
        print(f"  - 测试间隔: {self.interval_minutes} 分钟")
        print(f"  - 工作时间: {self.start_hour}:00 - {self.end_hour}:00")
        print(f"  - 数据保留: {self.retention_days} 天")

        # 启动时清理旧数据
        self.cleanup_old_data()

        # 获取初始模型列表
        self._models = self.get_models()
        if self._models:
            print(f"  - 发现 {len(self._models)} 个模型: {', '.join(self._models)}")
        else:
            print("  - 未找到任何模型")

        # 立即执行一次测试
        self.run_test()

        # 设置定时调度
        schedule.every(self.interval_minutes).minutes.do(self.run_test)

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        print(f"[{datetime.now().isoformat()}] 监控服务已启动，等待下次调度...")

    def _run_loop(self):
        """调度循环"""
        while self._running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        """停止监控服务"""
        print(f"[{datetime.now().isoformat()}] 停止健康监控服务...")
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print(f"[{datetime.now().isoformat()}] 监控服务已停止")

    def run_once(self):
        """手动执行一次测试（用于非守护模式）"""
        self.run_test()


def main():
    """主入口"""
    import argparse
    parser = argparse.ArgumentParser(description="NewAPI 健康监控服务")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--daemon", action="store_true", help="守护进程模式运行")
    args = parser.parse_args()

    monitor = HealthMonitor(args.config)

    def signal_handler(sig, frame):
        monitor.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.daemon:
        monitor.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop()
    else:
        monitor.run_once()


if __name__ == "__main__":
    main()

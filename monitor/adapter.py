import time
import requests
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime


class NewAPIAdapter:
    """NewAPI 适配器"""

    def __init__(self, endpoint: str, api_key: str, timeout: int = 10):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.chat_endpoint = f"{self.endpoint}/chat/completions"
        self.models_endpoint = f"{self.endpoint}/models"
        self._models = None

    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        try:
            response = requests.get(
                self.models_endpoint,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    return [m.get("id", "") for m in data["data"] if m.get("id")]
            return []
        except requests.RequestException:
            return []

    def _test_model(self, model: str) -> Tuple[bool, Optional[float], Optional[str]]:
        """测试单个模型是否可用，返回 (可用, 延迟ms, 错误信息)"""
        start_time = time.time()
        try:
            response = requests.post(
                self.chat_endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": "Hi"}],
                    "max_tokens": 5
                },
                timeout=5
            )
            latency_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                return True, latency_ms, None
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                return False, latency_ms, error_msg

        except requests.Timeout:
            return False, None, f"Request timeout after 5s"
        except requests.RequestException as e:
            return False, None, f"Request error: {str(e)}"

    def test_connection(self, model: str = None, retry_count: int = 3, retry_interval: int = 10) -> Tuple[bool, Optional[float], Optional[str], int]:
        """
        测试 API 可用性

        Args:
            model: 要测试的模型名称，如果为 None 则自动选择一个可用模型

        Returns:
            Tuple[可用, 延迟ms, 错误信息, 重试次数]
        """
        if model is None:
            model = self._find_working_model()
            if model is None:
                return False, None, "No available model found", 0

        actual_retry = 0

        for attempt in range(retry_count):
            actual_retry = attempt
            start_time = time.time()
            try:
                response = requests.post(
                    self.chat_endpoint,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": "Hi"}],
                        "max_tokens": 10
                    },
                    timeout=self.timeout
                )

                latency_ms = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    return True, latency_ms, None, actual_retry
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"

                    # 如果是 model_not_found，标记模型不可用
                    if "model_not_found" in response.text:
                        return False, latency_ms, error_msg, actual_retry

                    if attempt < retry_count - 1:
                        time.sleep(retry_interval)
                    else:
                        return False, latency_ms, error_msg, actual_retry

            except requests.Timeout:
                error_msg = f"Request timeout after {self.timeout}s"
                if attempt < retry_count - 1:
                    time.sleep(retry_interval)
            except requests.RequestException as e:
                error_msg = f"Request error: {str(e)}"
                if attempt < retry_count - 1:
                    time.sleep(retry_interval)

        return False, None, error_msg, actual_retry

    def _find_working_model(self) -> Optional[str]:
        """尝试找到一个可用的模型"""
        models = self.get_available_models()
        if not models:
            return None

        for model in models:
            available, _, _ = self._test_model(model)
            if available:
                return model
        return None

    def get_status(self, model: str = None) -> Dict[str, Any]:
        """获取 API 状态信息"""
        available, latency, error, retries = self.test_connection(model)
        return {
            "available": available,
            "latency_ms": latency,
            "error": error,
            "model": model,
            "timestamp": datetime.now().isoformat()
        }

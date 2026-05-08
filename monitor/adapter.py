import time
import json
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

    def classify_model(self, model_name: str, classifier_model: str) -> Dict[str, Any]:
        """使用配置的分类模型对指定模型进行 AI 分类"""
        prompt = f"""请根据模型名称 "{model_name}" 判断该 AI 模型的分类信息，仅返回 JSON，不要其他内容。

返回格式：
{{"vendor": "厂商名", "use_cases": ["使用场景1", "使用场景2"], "language_strengths": ["语言能力1", "语言能力2"]}}

字段说明：
- vendor: 厂商或项目名（如 "OpenAI", "DeepSeek", "Google", "Anthropic", "智谱", "MiniMax", "字节跳动", "月之暗面" 等）
- use_cases: 擅长的使用场景，可选值：["编程", "聊天", "写文档", "推理", "数学", "翻译", "创意写作", "图像生成", "代码审查"]
- language_strengths: 擅长的语言，可选值：["中文", "英文", "代码"]

如果无法识别，vendor 填 "unknown"，use_cases 和 language_strengths 填空数组。"""

        try:
            response = requests.post(
                self.chat_endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": classifier_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200,
                    "temperature": 0.1
                },
                timeout=30
            )

            raw_text = response.text

            if response.status_code != 200:
                return {"vendor": "unknown", "use_cases": "[]", "language_strengths": "[]", "raw_response": raw_text[:500]}

            data = response.json()
            # 兼容不同返回格式：OpenAI 标准和 NewAPI 扩展
            choices = data.get("choices", [])
            content = ""
            if choices:
                msg = choices[0].get("message", {})
                content = msg.get("content", "") or msg.get("reasoning_content", "") or ""

            # 提取 JSON 部分
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                parsed = json.loads(json_str)
                vendor = parsed.get("vendor", "unknown")
                use_cases = json.dumps(parsed.get("use_cases", []), ensure_ascii=False)
                language_strengths = json.dumps(parsed.get("language_strengths", []), ensure_ascii=False)
                return {
                    "vendor": vendor,
                    "use_cases": use_cases,
                    "language_strengths": language_strengths,
                    "raw_response": content
                }

            return {"vendor": "unknown", "use_cases": "[]", "language_strengths": "[]", "raw_response": content[:500]}

        except (requests.RequestException, json.JSONDecodeError, KeyError, IndexError) as e:
            return {"vendor": "unknown", "use_cases": "[]", "language_strengths": "[]", "raw_response": str(e)}

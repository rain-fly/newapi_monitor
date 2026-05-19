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

    def _is_body_error(self, response) -> Tuple[bool, Optional[str]]:
        """检查 HTTP 200 响应体中的隐性错误（如 MiniMax 限额仍返回 200）"""
        try:
            data = response.json()
        except (ValueError, TypeError):
            return False, None

        # MiniMax 特有：base_resp.status_code != 0 表示业务错误
        base = data.get("base_resp")
        if base and isinstance(base, dict):
            status_code = base.get("status_code", 0)
            if status_code != 0:
                msg = base.get("status_msg", f"base_resp status_code={status_code}")
                return True, f"HTTP 200 body error: {msg}"

        # 通用：choices 为 null 且有 error 字段
        if data.get("choices") is None and data.get("error"):
            err = data["error"]
            err_msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
            return True, f"HTTP 200 body error: {err_msg}"

        return False, None

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
                body_error, body_msg = self._is_body_error(response)
                if body_error:
                    return False, latency_ms, body_msg
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
                    body_error, body_msg = self._is_body_error(response)
                    if body_error:
                        return False, latency_ms, body_msg, actual_retry
                    return True, latency_ms, None, actual_retry
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"

                    # 429 限额，不重试直接返回
                    if response.status_code == 429 or "usage limit exceeded" in response.text:
                        return False, latency_ms, error_msg, actual_retry

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


# 模型关键词匹配规则表
MODEL_RULES = [
    # OpenAI
    {"keywords": ["gpt-", "o1-", "o3-", "o4-", "codex"], "vendor": "OpenAI", "use_cases": ["编程", "聊天", "写文档", "推理"], "language_strengths": ["英文", "代码"]},
    {"keywords": ["dall-e", "dalle"], "vendor": "OpenAI", "use_cases": ["图像生成"], "language_strengths": []},
    # Anthropic
    {"keywords": ["claude"], "vendor": "Anthropic", "use_cases": ["编程", "聊天", "写文档", "推理"], "language_strengths": ["英文", "代码"]},
    # Google
    {"keywords": ["gemini"], "vendor": "Google", "use_cases": ["编程", "聊天", "推理", "翻译"], "language_strengths": ["英文", "中文", "代码"]},
    # DeepSeek
    {"keywords": ["deepseek"], "vendor": "DeepSeek", "use_cases": ["编程", "推理", "数学"], "language_strengths": ["中文", "英文", "代码"]},
    # 智谱 / GLM
    {"keywords": ["glm", "chatglm", "cogview"], "vendor": "智谱", "use_cases": ["聊天", "写文档", "编程"], "language_strengths": ["中文", "英文", "代码"]},
    # MiniMax
    {"keywords": ["minimax", "minmax"], "vendor": "MiniMax", "use_cases": ["聊天", "写文档"], "language_strengths": ["中文", "英文"]},
    # 美团 / LongCat
    {"keywords": ["longcat"], "vendor": "美团", "use_cases": ["聊天", "写文档", "推理"], "language_strengths": ["中文", "英文", "代码"]},
    # 字节跳动 / 豆包
    {"keywords": ["doubao", "seed-1"], "vendor": "字节跳动", "use_cases": ["聊天", "编程", "翻译"], "language_strengths": ["中文", "英文", "代码"]},
    # 月之暗面 / Kimi
    {"keywords": ["kimi", "moonshot"], "vendor": "月之暗面", "use_cases": ["聊天", "写文档", "编程"], "language_strengths": ["中文", "英文", "代码"]},
    # 阿里 / 通义千问
    {"keywords": ["qwen"], "vendor": "千问", "use_cases": ["编程", "聊天", "推理", "翻译"], "language_strengths": ["中文", "英文", "代码"]},
    # xAI / Grok
    {"keywords": ["grok"], "vendor": "xAI", "use_cases": ["聊天", "推理", "创意写作"], "language_strengths": ["英文", "代码"]},
    # Mistral
    {"keywords": ["mistral", "mixtral", "codestral"], "vendor": "Mistral", "use_cases": ["编程", "聊天"], "language_strengths": ["英文", "代码"]},
    # Meta / Llama
    {"keywords": ["llama"], "vendor": "Meta", "use_cases": ["聊天", "编程", "推理"], "language_strengths": ["英文", "代码"]},
    # NVIDIA
    {"keywords": ["nemotron"], "vendor": "NVIDIA", "use_cases": ["聊天", "推理"], "language_strengths": ["英文", "代码"]},
    # 联发科 / Dimos / Mimo
    {"keywords": ["mimo"], "vendor": "小米", "use_cases": ["推理", "编程"], "language_strengths": ["中文", "英文", "代码"]},
]


def classify_model_by_name(model_name: str) -> Dict[str, Any]:
    """根据模型名称关键词匹配分类，不调用 AI"""
    name_lower = model_name.lower()
    for rule in MODEL_RULES:
        for kw in rule["keywords"]:
            if kw in name_lower:
                return {
                    "vendor": rule["vendor"],
                    "use_cases": json.dumps(rule["use_cases"], ensure_ascii=False),
                    "language_strengths": json.dumps(rule["language_strengths"], ensure_ascii=False),
                    "raw_response": f"matched keyword: {kw}"
                }
    return {
        "vendor": "unknown",
        "use_cases": "[]",
        "language_strengths": "[]",
        "raw_response": "no keyword matched"
    }

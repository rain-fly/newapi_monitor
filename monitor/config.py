import os
import yaml
from typing import Dict, Any


class Config:
    """配置管理类"""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, config_path: str = None):
        """加载配置文件"""
        if config_path is None:
            config_path = os.environ.get("CONFIG_PATH", "config.yaml")

        with open(config_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f)
        return self

    @property
    def newapi(self) -> Dict[str, Any]:
        config = self._config.get("newapi", {})
        # 环境变量覆盖配置
        if "NEWAPI_ENDPOINT" in os.environ:
            config["endpoint"] = os.environ["NEWAPI_ENDPOINT"]
        if "NEWAPI_API_KEY" in os.environ:
            config["api_key"] = os.environ["NEWAPI_API_KEY"]
        return config

    @property
    def scheduler(self) -> Dict[str, Any]:
        return self._config.get("scheduler", {})

    @property
    def database(self) -> Dict[str, Any]:
        return self._config.get("database", {})

    @property
    def retention(self) -> Dict[str, Any]:
        return self._config.get("retention", {})

    @property
    def web(self) -> Dict[str, Any]:
        return self._config.get("web", {})

    def get(self, key: str, default=None):
        return self._config.get(key, default) if self._config else default


def load_config(config_path: str = None) -> Config:
    """加载配置并返回Config实例"""
    return Config().load(config_path)

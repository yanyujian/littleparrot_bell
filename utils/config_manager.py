import json
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "window_position": {"x": 100, "y": 100},
            "always_on_top": False,
            "opacity": 1.0,
            "language": "en"  # 添加默认语言设置
        }
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return {**self.default_config, **json.load(f)}
            except:
                return self.default_config
        return self.default_config

    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except:
            pass

    def get(self, key: str) -> Any:
        """获取配置项"""
        return self.config.get(key, self.default_config.get(key))

    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        self.config[key] = value
        self.save_config() 
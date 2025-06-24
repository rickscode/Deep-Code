import os
import yaml
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path.home() / ".ai-code" / "config.yaml"

DEFAULT_CONFIG = {
    "api": {
        "provider": "groq",
        "key": os.environ.get("GROQ_API_KEY", ""),
        "default_model": "deepseek-r1-distill-llama-70b",
        "fallback_models": [
            "llama-3.3-70b-versatile",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "meta-llama/llama-4-scout-17b-16e-instruct"
        ]
    },
    "editor": {
        "auto_save": True,
        "backup_count": 5,
        "syntax_highlighting": True
    },
    "git": {
        "auto_commit": False,
        "commit_prefix": "ai-code:",
        "push_after_commit": False
    },
    "privacy": {
        "local_mode": False,
        "data_retention_days": 30,
        "audit_logging": True
    }
}

def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
    return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(config, f)

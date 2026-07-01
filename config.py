"""配置读写：目标语言、翻译源、快捷键等。"""
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".screen_translator"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "target_lang": "zh-CN",   # 译文目标语言
    "source_lang": "auto",    # 原文语言（auto = 自动检测）
    "translator": "google",   # google / mymemory
    "hotkey": "<alt>+q",      # pynput 格式的全局快捷键
    "show_notification": True,
}


def load_config() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = dict(DEFAULT_CONFIG)
        merged.update(data or {})
        return merged
    except Exception:
        return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

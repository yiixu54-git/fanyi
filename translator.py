"""翻译模块：封装 deep-translator，支持 Google / MyMemory。"""
from __future__ import annotations

# MyMemory 语言代码映射（部分需要转换）
_MYMEMORY_MAP = {
    "zh-CN": "zh-CN",
    "zh-TW": "zh-TW",
    "en": "en-US",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "fr": "fr-FR",
    "de": "de-DE",
    "es": "es-ES",
    "ru": "ru-RU",
}


def translate(
    text: str,
    target: str = "zh-CN",
    source: str = "auto",
    provider: str = "google",
) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    try:
        if provider == "mymemory":
            from deep_translator import MyMemoryTranslator

            src = _MYMEMORY_MAP.get(source, "en-US") if source != "auto" else "en-US"
            tgt = _MYMEMORY_MAP.get(target, target)
            return MyMemoryTranslator(source=src, target=tgt).translate(text)

        # 默认 Google
        from deep_translator import GoogleTranslator

        return GoogleTranslator(source=source, target=target).translate(text)
    except Exception as e:  # noqa: BLE001
        return f"[翻译失败] {e}"

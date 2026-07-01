"""OCR 引擎：RapidOCR（基于 ONNXRuntime，轻量、免安装外部依赖）。

首次导入时会自动下载模型文件（约 20MB，只下一次）。
"""
from __future__ import annotations

import numpy as np
from PIL import Image

_ocr = None
_load_error: Exception | None = None


def _get_ocr():
    global _ocr, _load_error
    if _ocr is not None:
        return _ocr
    if _load_error is not None:
        raise _load_error
    try:
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR()
        return _ocr
    except Exception as e:  # noqa: BLE001
        _load_error = e
        raise


def recognize(pil_image: Image.Image) -> str:
    """对 PIL 图像做 OCR 识别，返回按行拼接的文字。"""
    try:
        ocr = _get_ocr()
    except Exception as e:  # noqa: BLE001
        return f"[OCR 初始化失败] {e}"

    try:
        img = np.array(pil_image.convert("RGB"))
        result, _ = ocr(img)
    except Exception as e:  # noqa: BLE001
        return f"[OCR 识别失败] {e}"

    if not result:
        return ""

    lines: list[str] = []
    for item in result:
        # item 通常是 [box, text, score]
        try:
            text = item[1]
        except Exception:  # noqa: BLE001
            continue
        if text:
            lines.append(str(text))
    return "\n".join(lines)

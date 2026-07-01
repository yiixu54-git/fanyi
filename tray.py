"""托盘 + 主控制器：注册热键、启动框选、驱动 OCR & 翻译。"""
from __future__ import annotations

import mss
from PIL import Image
from PyQt5.QtCore import QObject, QPoint, QRect, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QActionGroup,
    QApplication,
    QMenu,
    QMessageBox,
    QSystemTrayIcon,
)

from config import load_config, save_config
from ocr_engine import recognize
from overlay import OverlayWindow
from result_window import ResultWindow
from translator import translate

# 支持的目标语言列表
LANGS = [
    ("中文（简体）", "zh-CN"),
    ("中文（繁体）", "zh-TW"),
    ("英语 English", "en"),
    ("日语 日本語", "ja"),
    ("韩语 한국어", "ko"),
    ("法语 Français", "fr"),
    ("德语 Deutsch", "de"),
    ("西班牙语 Español", "es"),
    ("俄语 Русский", "ru"),
]

PROVIDERS = [
    ("Google 翻译", "google"),
    ("MyMemory（备用）", "mymemory"),
]


def _make_icon() -> QIcon:
    """程序化生成一个圆角"译"字图标，无需外部资源。"""
    pm = QPixmap(64, 64)
    pm.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(59, 130, 246))
    painter.setPen(QColor(0, 0, 0, 0))
    painter.drawRoundedRect(2, 2, 60, 60, 14, 14)
    font = QFont("Microsoft YaHei", 30)
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor("white"))
    painter.drawText(pm.rect(), 0x0004 | 0x0080, "译")  # AlignHCenter | AlignVCenter
    painter.end()
    return QIcon(pm)


class TranslateWorker(QThread):
    """后台线程：OCR + 翻译。"""

    finished_signal = pyqtSignal(str, str, QPoint, str)

    def __init__(
        self,
        image: Image.Image,
        target: str,
        source: str,
        provider: str,
        pos: QPoint,
    ) -> None:
        super().__init__()
        self.image = image
        self.target = target
        self.source = source
        self.provider = provider
        self.pos = pos

    def run(self) -> None:
        original = recognize(self.image)
        if original and not original.startswith("[OCR"):
            translated = translate(
                original, self.target, self.source, self.provider
            )
        elif original.startswith("[OCR"):
            translated = ""
        else:
            translated = ""
        info = f"→ {self.target}  |  {self.provider}"
        self.finished_signal.emit(original, translated, self.pos, info)


class TrayApp(QObject):
    _hotkey_triggered = pyqtSignal()

    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self.config = load_config()

        self.tray = QSystemTrayIcon(_make_icon())
        self.tray.setToolTip("屏幕翻译 — 单击开始框选（Alt+Q）")

        self.overlay = OverlayWindow()
        self.overlay.selection_finished.connect(self._on_selection)

        self.result_window = ResultWindow()
        self.worker: TranslateWorker | None = None

        self._build_menu()
        self.tray.activated.connect(self._on_tray_activated)

        # 全局热键要在 GUI 线程触发框选
        self._hotkey_triggered.connect(self.start_capture)
        self._setup_hotkey()

    # ----------------------------------------------------------- 菜单
    def _build_menu(self) -> None:
        menu = QMenu()

        cap_action = QAction("🎯  开始框选翻译", menu)
        cap_action.triggered.connect(self.start_capture)
        cap_action.setShortcut("Alt+Q")
        menu.addAction(cap_action)

        menu.addSeparator()

        # 目标语言
        lang_menu = menu.addMenu("目标语言")
        lang_group = QActionGroup(lang_menu)
        lang_group.setExclusive(True)
        for name, code in LANGS:
            act = QAction(name, lang_menu)
            act.setCheckable(True)
            act.setChecked(self.config.get("target_lang") == code)
            act.triggered.connect(
                lambda checked, c=code: self._set_config("target_lang", c)
            )
            lang_group.addAction(act)
            lang_menu.addAction(act)

        # 翻译源
        prov_menu = menu.addMenu("翻译源")
        prov_group = QActionGroup(prov_menu)
        prov_group.setExclusive(True)
        for name, code in PROVIDERS:
            act = QAction(name, prov_menu)
            act.setCheckable(True)
            act.setChecked(self.config.get("translator") == code)
            act.triggered.connect(
                lambda checked, c=code: self._set_config("translator", c)
            )
            prov_group.addAction(act)
            prov_menu.addAction(act)

        menu.addSeparator()

        about_action = QAction("关于 / 使用说明", menu)
        about_action.triggered.connect(self._about)
        menu.addAction(about_action)

        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)

    def _set_config(self, key: str, value) -> None:
        self.config[key] = value
        save_config(self.config)
        self._build_menu()  # 重建以刷新勾选状态

    def _about(self) -> None:
        QMessageBox.information(
            None,
            "屏幕翻译 - 使用说明",
            (
                "🎯  操作方式：\n"
                "  • 单击托盘图标 或 按 Alt+Q 开始框选\n"
                "  • 用鼠标拖动画出一个矩形，松开鼠标\n"
                "  • 程序会自动 OCR 识别 + 翻译（支持图片文字）\n"
                "  • Esc 或 右键 取消框选\n"
                "\n"
                "⚙️  设置：\n"
                "  • 右键托盘图标可切换『目标语言』和『翻译源』\n"
                "\n"
                "📁  配置文件：\n"
                f"  {load_config.__globals__['CONFIG_FILE']}\n"
                "\n"
                "💡  首次使用会自动下载 OCR 模型（约 20MB，只下一次）。"
            ),
        )

    # ----------------------------------------------------------- 托盘
    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.Trigger:  # 左键单击
            self.start_capture()

    def show(self) -> None:
        self.tray.show()
        if self.config.get("show_notification", True):
            self.tray.showMessage(
                "屏幕翻译已启动",
                "单击托盘图标 或 按 Alt+Q 开始框选\n右键托盘可切换目标语言",
                QSystemTrayIcon.Information,
                3000,
            )

    def _quit(self) -> None:
        try:
            if hasattr(self, "_listener") and self._listener is not None:
                self._listener.stop()
        except Exception:  # noqa: BLE001
            pass
        self.app.quit()

    # ----------------------------------------------------------- 快捷键
    def _setup_hotkey(self) -> None:
        try:
            from pynput import keyboard as kb

            def _cb() -> None:
                self._hotkey_triggered.emit()

            hk = self.config.get("hotkey", "<alt>+q")
            self._listener = kb.GlobalHotKeys({hk: _cb})
            self._listener.daemon = True
            self._listener.start()
        except Exception as e:  # noqa: BLE001
            print(f"[热键] 注册失败：{e}")
            self._listener = None

    # ----------------------------------------------------------- 框选流程
    def start_capture(self) -> None:
        self.result_window.hide()
        # 稍微延迟以避免菜单/托盘遮挡
        QTimer.singleShot(120, self.overlay.start)

    def _on_selection(self, rect: QRect) -> None:
        if rect.width() <= 0 or rect.height() <= 0:
            return
        try:
            with mss.mss() as sct:
                monitor = {
                    "left": int(rect.left()),
                    "top": int(rect.top()),
                    "width": int(rect.width()),
                    "height": int(rect.height()),
                }
                sct_img = sct.grab(monitor)
                img = Image.frombytes(
                    "RGB", sct_img.size, sct_img.bgra, "raw", "BGRX"
                )
        except Exception as e:  # noqa: BLE001
            QMessageBox.warning(None, "截图失败", str(e))
            return

        # 结果窗口初始位置：选区左下方
        pos = QPoint(rect.left(), rect.bottom() + 12)

        self.result_window.show_result(
            "识别中...", "翻译中...", pos,
            info=f"→ {self.config.get('target_lang')}"
        )

        self.worker = TranslateWorker(
            img,
            self.config.get("target_lang", "zh-CN"),
            self.config.get("source_lang", "auto"),
            self.config.get("translator", "google"),
            pos,
        )
        self.worker.finished_signal.connect(self._on_translate_done)
        self.worker.start()

    def _on_translate_done(
        self, original: str, translated: str, pos: QPoint, info: str
    ) -> None:
        if not original.strip():
            original = "(未识别到文字)"
        self.result_window.show_result(original, translated, pos, info=info)

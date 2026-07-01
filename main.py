"""屏幕框选翻译工具 - 主入口。

功能：
  * 系统托盘常驻
  * 快捷键 Alt+Q 或 单击托盘 开启框选
  * 松开鼠标后自动 OCR + 翻译
  * Esc 取消框选
"""
import sys


def _enable_dpi_awareness() -> None:
    """让进程成为 Per-Monitor DPI aware，确保 Qt 坐标与屏幕物理像素一致。"""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        # 2 = PROCESS_PER_MONITOR_DPI_AWARE
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main() -> int:
    _enable_dpi_awareness()

    # 必须在导入 QApplication 之前设置 DPI 感知
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import Qt

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("ScreenTranslator")

    # 检查系统托盘
    from PyQt5.QtWidgets import QSystemTrayIcon
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "错误", "当前系统不支持系统托盘。")
        return 1

    from tray import TrayApp

    tray_app = TrayApp(app)
    tray_app.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())

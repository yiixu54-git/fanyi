"""屏幕框选覆盖层。

使用一个覆盖整个虚拟桌面（含多屏）的半透明窗口，
让用户用鼠标拖出一个矩形；松开鼠标后发出 selection_finished 信号。
"""
from PyQt5.QtCore import QPoint, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import QApplication, QWidget


class OverlayWindow(QWidget):
    selection_finished = pyqtSignal(QRect)
    selection_cancelled = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._start: QPoint | None = None
        self._end: QPoint | None = None
        self._selecting: bool = False

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)

    # ----------------------------------------------------------- 事件
    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # 半透明遮罩铺满全屏
        painter.fillRect(self.rect(), QColor(0, 0, 0, 110))

        if self._start and self._end:
            rect = QRect(self._start, self._end).normalized()
            # 抠出选区（透明）
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

            # 蓝色描边
            pen = QPen(QColor(64, 158, 255), 2)
            painter.setPen(pen)
            painter.drawRect(rect)

            # 右下角显示尺寸
            size_text = f"{rect.width()} × {rect.height()}"
            painter.setPen(QColor(255, 255, 255))
            painter.setBrush(QColor(0, 0, 0, 160))
            text_rect = QRect(rect.right() - 90, rect.bottom() + 6, 90, 22)
            if text_rect.bottom() > self.height():
                text_rect.moveTop(rect.bottom() - 26)
            painter.drawRoundedRect(text_rect, 4, 4)
            painter.drawText(text_rect, Qt.AlignCenter, size_text)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._start = event.pos()
            self._end = event.pos()
            self._selecting = True
            self.update()
        elif event.button() == Qt.RightButton:
            self._cancel()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._selecting:
            self._end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton and self._selecting:
            self._selecting = False
            rect = QRect(self._start, self._end).normalized()
            self.hide()
            if rect.width() >= 5 and rect.height() >= 5:
                # 转换为屏幕的绝对物理像素坐标
                abs_rect = QRect(
                    rect.left() + self.geometry().left(),
                    rect.top() + self.geometry().top(),
                    rect.width(),
                    rect.height(),
                )
                self.selection_finished.emit(abs_rect)
            else:
                self.selection_cancelled.emit()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key_Escape:
            self._cancel()

    # ----------------------------------------------------------- API
    def _cancel(self) -> None:
        self._selecting = False
        self._start = None
        self._end = None
        self.hide()
        self.selection_cancelled.emit()

    def start(self) -> None:
        """显示覆盖层，覆盖整个虚拟桌面。"""
        self._start = None
        self._end = None
        self._selecting = False

        # 用虚拟桌面几何（含所有显示器）
        virt = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(virt)
        self.show()
        self.activateWindow()
        self.raise_()
        self.setFocus(Qt.OtherFocusReason)

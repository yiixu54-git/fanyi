"""翻译结果弹窗：原文 + 译文，可拖拽 / 复制 / 关闭。"""
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ResultWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_pos: QPoint | None = None
        self._build_ui()

    # ----------------------------------------------------------- UI
    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(
            """
            #card {
                background: rgba(28, 30, 40, 240);
                border-radius: 14px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
            QLabel { color: #9aa5b1; font-size: 12px; }
            QLabel#title { color: #ffffff; font-weight: 600; font-size: 13px; }
            QTextEdit {
                background: rgba(255, 255, 255, 0.04);
                color: #f2f3f5;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 8px;
                padding: 6px 8px;
                font-size: 14px;
                selection-background-color: #3b82f6;
            }
            QPushButton#close {
                background: transparent;
                color: #9aa5b1;
                border: none;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton#close:hover { color: #ff5c5c; }
            QPushButton.action {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 6px 14px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton.action:hover { background: #2563eb; }
            QPushButton.ghost {
                background: transparent;
                color: #9aa5b1;
                border: 1px solid rgba(255,255,255,0.12);
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton.ghost:hover { color: #ffffff; border-color: rgba(255,255,255,0.24); }
            """
        )
        # 阴影效果（用简单方式：卡片外 margin 已经留出空间）
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # 顶栏：标题 + 关闭
        top = QHBoxLayout()
        top.setSpacing(6)
        title = QLabel("屏幕翻译")
        title.setObjectName("title")
        top.addWidget(title)
        self.info_label = QLabel("")
        top.addWidget(self.info_label)
        top.addStretch()
        close_btn = QPushButton("×")
        close_btn.setObjectName("close")
        close_btn.setFixedSize(22, 22)
        close_btn.clicked.connect(self.hide)
        top.addWidget(close_btn)
        layout.addLayout(top)

        # 原文
        layout.addWidget(QLabel("原文"))
        self.src_text = QTextEdit()
        self.src_text.setReadOnly(True)
        self.src_text.setMinimumHeight(60)
        self.src_text.setMaximumHeight(120)
        layout.addWidget(self.src_text)

        # 译文
        layout.addWidget(QLabel("译文"))
        self.tgt_text = QTextEdit()
        self.tgt_text.setReadOnly(True)
        self.tgt_text.setMinimumHeight(80)
        self.tgt_text.setMaximumHeight(180)
        layout.addWidget(self.tgt_text)

        # 底部按钮
        bottom = QHBoxLayout()
        bottom.addStretch()

        copy_src_btn = QPushButton("复制原文")
        copy_src_btn.setProperty("class", "ghost")
        copy_src_btn.setStyleSheet("")
        copy_src_btn.setObjectName("copySrc")
        # 用 class 属性触发 stylesheet
        copy_src_btn.setProperty("class", "ghost")
        bottom.addWidget(copy_src_btn)

        copy_tgt_btn = QPushButton("复制译文")
        copy_tgt_btn.setProperty("class", "action")
        bottom.addWidget(copy_tgt_btn)

        # 由于 property class 需要 polish 才生效，这里显式挂 style
        copy_src_btn.setStyleSheet(
            "background: transparent; color: #9aa5b1;"
            "border: 1px solid rgba(255,255,255,0.12);"
            "padding: 6px 12px; border-radius: 6px; font-size: 12px;"
        )
        copy_tgt_btn.setStyleSheet(
            "background: #3b82f6; color: white; border: none;"
            "padding: 6px 14px; border-radius: 6px; font-size: 12px;"
        )

        copy_src_btn.clicked.connect(
            lambda: QApplication.clipboard().setText(self.src_text.toPlainText())
        )
        copy_tgt_btn.clicked.connect(
            lambda: QApplication.clipboard().setText(self.tgt_text.toPlainText())
        )
        layout.addLayout(bottom)

        self.resize(460, 360)

    # ----------------------------------------------------------- API
    def show_result(
        self,
        original: str,
        translated: str,
        pos: QPoint | None = None,
        info: str = "",
    ) -> None:
        self.src_text.setPlainText(original or "")
        self.tgt_text.setPlainText(translated or "")
        self.info_label.setText(f"  {info}" if info else "")

        screen_geom = QApplication.primaryScreen().availableGeometry()
        if pos is None:
            pos = QPoint(
                screen_geom.right() - self.width() - 20,
                screen_geom.bottom() - self.height() - 40,
            )

        x = max(screen_geom.left() + 4, min(pos.x(), screen_geom.right() - self.width() - 4))
        y = max(screen_geom.top() + 4, min(pos.y(), screen_geom.bottom() - self.height() - 4))
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()

    # 无边框窗口拖动
    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._drag_pos = None

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key_Escape:
            self.hide()

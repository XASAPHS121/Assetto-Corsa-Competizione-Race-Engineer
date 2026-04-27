"""
ACC Race Engineer — Custom Toggle Switch Widget
A QCheckBox styled as a horizontal sliding toggle switch.
"""

from PyQt6.QtCore import Qt, QRect, QPoint, QPropertyAnimation, pyqtProperty, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
from PyQt6.QtWidgets import QCheckBox


class ToggleSwitch(QCheckBox):
    """A switch-style toggle that fits the dark racing theme."""

    TRACK_HEIGHT = 22
    TRACK_WIDTH = 44
    HANDLE_SIZE = 18
    PADDING = 2

    OFF_TRACK_COLOR = QColor("#2A3040")
    ON_TRACK_COLOR = QColor("#FF4A3D")
    HANDLE_COLOR = QColor("#E0E4EC")

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(self.TRACK_HEIGHT + 4)

        self._handle_pos = self.PADDING
        self._anim = QPropertyAnimation(self, b"handle_pos", self)
        self._anim.setDuration(140)
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        end_x = self.TRACK_WIDTH - self.HANDLE_SIZE - self.PADDING if checked else self.PADDING
        self._anim.stop()
        self._anim.setStartValue(self._handle_pos)
        self._anim.setEndValue(end_x)
        self._anim.start()

    @pyqtProperty(int)
    def handle_pos(self):
        return self._handle_pos

    @handle_pos.setter
    def handle_pos(self, value: int):
        self._handle_pos = value
        self.update()

    def hitButton(self, pos: QPoint) -> bool:
        # Make the entire widget clickable (track + label area)
        return self.contentsRect().contains(pos)

    def sizeHint(self) -> QSize:
        # Reserve space for the toggle plus the label
        fm = self.fontMetrics()
        text_w = fm.horizontalAdvance(self.text()) if self.text() else 0
        gap = 10 if self.text() else 0
        return QSize(self.TRACK_WIDTH + gap + text_w + 4, self.TRACK_HEIGHT + 4)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Track (rounded pill)
        track_rect = QRect(0, (self.height() - self.TRACK_HEIGHT) // 2,
                           self.TRACK_WIDTH, self.TRACK_HEIGHT)
        track_color = self.ON_TRACK_COLOR if self.isChecked() else self.OFF_TRACK_COLOR
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(track_color))
        painter.drawRoundedRect(track_rect, self.TRACK_HEIGHT // 2, self.TRACK_HEIGHT // 2)

        # Handle (circle)
        handle_y = (self.height() - self.HANDLE_SIZE) // 2
        handle_rect = QRect(self._handle_pos, handle_y, self.HANDLE_SIZE, self.HANDLE_SIZE)
        painter.setBrush(QBrush(self.HANDLE_COLOR))
        painter.drawEllipse(handle_rect)

        # Label text after the toggle
        if self.text():
            painter.setPen(QPen(QColor("#B0B8C8")))
            text_rect = QRect(self.TRACK_WIDTH + 10, 0,
                              self.width() - self.TRACK_WIDTH - 10, self.height())
            painter.drawText(text_rect,
                             Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                             self.text())

        painter.end()

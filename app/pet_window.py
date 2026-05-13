from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QAction, QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QPixmap, QRegion
from PySide6.QtWidgets import QFileDialog, QMenu, QMessageBox, QWidget

from .asset_store import INPUT_DIR, import_video
from .config import PetConfig, save_config


class PetWindow(QWidget):
    def __init__(self, config: PetConfig) -> None:
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.NoDropShadowWindowHint,
        )
        self.config = config
        self._drag_start: QPoint | None = None
        self._frames: list[QPixmap] = []
        self._frame_index = 0
        self._rendered_frame: QPixmap | None = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._next_frame)

        self.setWindowTitle("Cat Desktop Pet")
        self.setFixedSize(config.pet_size, config.pet_size)
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setStyleSheet("background: transparent; border: none;")

        if config.window_x is not None and config.window_y is not None:
            self.move(config.window_x, config.window_y)

        self._load_processed_frames()

    def paintEvent(self, event) -> None:  # noqa: N802
        del event

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

        if self._frames:
            if self._rendered_frame is not None:
                painter.drawPixmap(0, 0, self._rendered_frame)
            return

        rect = self.rect().adjusted(16, 16, -16, -16)
        body = QPainterPath()
        body.addEllipse(rect)

        painter.setBrush(QBrush(QColor(30, 30, 30, 190)))
        painter.setPen(QPen(QColor(255, 255, 255, 180), 2))
        painter.drawPath(body)

        ear_pen = QPen(QColor(255, 255, 255, 180), 2)
        painter.setPen(ear_pen)
        painter.setBrush(QBrush(QColor(30, 30, 30, 190)))
        painter.drawPolygon(
            [
                rect.topLeft() + QPoint(38, 18),
                rect.topLeft() + QPoint(76, -4),
                rect.topLeft() + QPoint(96, 48),
            ]
        )
        painter.drawPolygon(
            [
                rect.topRight() + QPoint(-38, 18),
                rect.topRight() + QPoint(-76, -4),
                rect.topRight() + QPoint(-96, 48),
            ]
        )

        painter.setBrush(QBrush(QColor(244, 205, 94)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(rect.center() + QPoint(-56, -28), 13, 18)
        painter.drawEllipse(rect.center() + QPoint(56, -28), 13, 18)

        painter.setBrush(QBrush(QColor(230, 120, 130)))
        painter.drawEllipse(rect.center() + QPoint(0, 22), 9, 6)

        painter.setPen(QPen(QColor(255, 255, 255, 210), 2))
        painter.drawLine(rect.center() + QPoint(-8, 32), rect.center() + QPoint(-38, 43))
        painter.drawLine(rect.center() + QPoint(8, 32), rect.center() + QPoint(38, 43))

        status = self._status_text()
        painter.setFont(QFont("Microsoft YaHei UI", 9))
        painter.setPen(QPen(QColor(255, 255, 255, 220)))
        painter.drawText(
            self.rect().adjusted(20, self.height() - 58, -20, -18),
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            status,
        )

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            return

        if event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag_start is None:
            return
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_start)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = None
            self.config.window_x = self.x()
            self.config.window_y = self.y()
            save_config(self.config)
            event.accept()

    def _show_context_menu(self, global_pos: QPoint) -> None:
        menu = QMenu(self)

        import_action = QAction("导入视频", self)
        import_action.triggered.connect(self._choose_video)
        menu.addAction(import_action)

        open_assets_action = QAction("打开素材目录", self)
        open_assets_action.triggered.connect(self._open_asset_dir)
        menu.addAction(open_assets_action)

        menu.addSeparator()

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.close)
        menu.addAction(quit_action)

        menu.exec(global_pos)

    def _choose_video(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择猫猫视频",
            str(Path.home()),
            "Video Files (*.mp4 *.mov *.mkv *.avi *.webm *.gif)",
        )
        if not file_path:
            return

        try:
            asset = import_video(Path(file_path))
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "导入失败", str(exc))
            return

        self.config.active_asset_path = str(asset.stored_path)
        self.config.active_asset_name = asset.display_name
        self.config.asset_status = "imported_pending_processing"
        self.config.processed_frames_dir = None
        save_config(self.config)
        self._load_processed_frames()
        self.update()

        QMessageBox.information(
            self,
            "导入完成",
            "视频已导入。下一步需要执行抠像处理，生成透明 PNG 序列或透明 WebM。",
        )

    def _open_asset_dir(self) -> None:
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        os.startfile(str(INPUT_DIR))

    def _status_text(self) -> str:
        if self.config.asset_status == "processed_transparent_frames":
            return f"播放中：{self.config.active_asset_name}"
        if self.config.active_asset_name:
            return f"已导入：{self.config.active_asset_name}\n等待抠像处理"
        return "右键导入猫猫视频"

    def _load_processed_frames(self) -> None:
        self._timer.stop()
        self._frames = []
        self._frame_index = 0

        if not self.config.processed_frames_dir:
            return

        frames_dir = Path(self.config.processed_frames_dir)
        if not frames_dir.exists():
            return

        frame_paths = sorted(frames_dir.glob("frame_*.png"))
        self._frames = [QPixmap(str(path)) for path in frame_paths]
        self._frames = [frame for frame in self._frames if not frame.isNull()]

        if self._frames:
            self._apply_frame()
            self._timer.start(self.config.frame_interval_ms)

    def _next_frame(self) -> None:
        if not self._frames:
            return
        self._frame_index = (self._frame_index + 1) % len(self._frames)
        self._apply_frame()
        self.update()

    def _apply_frame(self) -> None:
        frame = self._frames[self._frame_index]
        scaled = frame.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        rendered = QPixmap(self.size())
        rendered.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rendered)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        x = (self.width() - scaled.width()) // 2
        y = self.height() - scaled.height()
        painter.drawPixmap(x, y, scaled)
        painter.end()

        self._rendered_frame = rendered
        mask = rendered.mask()
        if mask.isNull():
            self.clearMask()
        else:
            self.setMask(QRegion(mask))

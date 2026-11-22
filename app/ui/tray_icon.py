"""
مدیریت آیکون سینی سیستم (System Tray Icon)
پشتیبانی از منوی سریع فارسی، کنترل حجم صدا، قطع/وصل و مدیریت پنجره اصلی
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu

from app.core.audio_manager import AudioManager
from app.models.audio import SinkDevice


class AppTrayIcon(QSystemTrayIcon):
    """آیکون سینی سیستم برای دسترسی سریع به عملکردهای صوتی."""

    show_window_requested = Signal()
    toggle_window_requested = Signal()
    quit_requested = Signal()

    def __init__(self, audio_mgr: AudioManager, icon: QIcon, parent=None):
        super().__init__(icon, parent)
        self.audio_mgr = audio_mgr
        self._current_sink: Optional[SinkDevice] = None
        self._init_menu()
        self.activated.connect(self._on_activated)

    def _init_menu(self):
        self.menu = QMenu()
        self.menu.setLayoutDirection(Qt.RightToLeft)

        # عنوان هدر
        self.action_header = QAction("مدیریت صدای AM", self.menu)
        self.action_header.setEnabled(False)
        self.menu.addAction(self.action_header)

        # نام خروجی فعال
        self.action_sink = QAction("خروجی: در حال بررسی...", self.menu)
        self.action_sink.setEnabled(False)
        self.menu.addAction(self.action_sink)

        self.menu.addSeparator()

        # کنترل‌های سریع صدا
        self.action_mute = QAction("🔊 قطع / وصل صدا", self.menu)
        self.action_mute.triggered.connect(self._toggle_mute)
        self.menu.addAction(self.action_mute)

        self.action_vol_up = QAction("▲ افزایش صدا (+۵٪)", self.menu)
        self.action_vol_up.triggered.connect(self._vol_up)
        self.menu.addAction(self.action_vol_up)

        self.action_vol_down = QAction("▼ کاهش صدا (-۵٪)", self.menu)
        self.action_vol_down.triggered.connect(self._vol_down)
        self.menu.addAction(self.action_vol_down)

        self.menu.addSeparator()

        # مدیریت پنجره
        self.action_toggle_win = QAction("نمایش / پنهان‌سازی پنجره اصلی", self.menu)
        self.action_toggle_win.triggered.connect(self.toggle_window_requested.emit)
        self.menu.addAction(self.action_toggle_win)

        self.menu.addSeparator()

        # خروج واقعی
        self.action_quit = QAction("خروج از برنامه", self.menu)
        self.action_quit.triggered.connect(self.quit_requested.emit)
        self.menu.addAction(self.action_quit)

        self.setContextMenu(self.menu)

    def update_status(self, sink: Optional[SinkDevice]):
        """به‌روزرسانی اطلاعات منوی سینی سیستم بر اساس خروجی فعال."""
        self._current_sink = sink
        if sink:
            self.action_sink.setText(f"خروجی: {sink.display_name}")
            vol_text = f"{sink.volume_percent}٪"
            mute_icon = "🔇" if sink.mute else "🔊"
            self.setToolTip(f"PipeOra\n{sink.display_name} ({vol_text})")
            self.action_mute.setText(f"قطع / وصل صدا ({vol_text})")
        else:
            self.action_sink.setText("خروجی: یافت نشد")
            self.setToolTip("PipeOra\nبدون خروجی صوتی فعال")

    def _on_activated(self, reason):
        # با کلیک چپ یا فعال‌سازی تری، پنجره نمایش داده یا پنهان می‌شود
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.toggle_window_requested.emit()

    def _toggle_mute(self):
        if self._current_sink:
            self.audio_mgr.toggle_mute(self._current_sink.name)

    def _vol_up(self):
        if self._current_sink:
            self.audio_mgr.change_volume(self._current_sink.name, 5)

    def _vol_down(self):
        if self._current_sink:
            self.audio_mgr.change_volume(self._current_sink.name, -5)

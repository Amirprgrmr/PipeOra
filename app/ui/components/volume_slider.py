"""
کامپوننت اسلایدر کنترل صدا (VolumeSlider)
با محافظت در برابر حلقه بازخورد رویدادها (Feedback Loop Prevention) و دکمه‌های گام سریع
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QSlider, QLabel, QPushButton
)


class VolumeSlider(QWidget):
    """اسلایدر پیشرفته کنترل صدا با دکمه Mute، درصد زنده و کلیدهای تنظیم گام."""

    volume_changed = Signal(int)    # ارسال درصد تغییریافته صدا (۰ تا ۱۰۰) توسط کاربر
    mute_toggled = Signal(bool)     # ارسال رویداد قطع/وصل صدا

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_updating_ui = False
        self._is_muted = False
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # دکمه بی‌صدا (Mute Toggle)
        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setToolTip("قطع/وصل صدا")
        self.btn_mute.setProperty("icon_btn", "true")
        self.btn_mute.setFixedSize(36, 36)
        self.btn_mute.clicked.connect(self._on_mute_clicked)
        layout.addWidget(self.btn_mute)

        # دکمه کاهش گامی (-5%)
        self.btn_minus = QPushButton("−")
        self.btn_minus.setToolTip("کاهش ۵ درصد")
        self.btn_minus.setFixedSize(28, 28)
        self.btn_minus.clicked.connect(self._decrease_step)
        layout.addWidget(self.btn_minus)

        # اسلایدر حجم صدا
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(70)
        self.slider.setTracking(True)
        self.slider.valueChanged.connect(self._on_slider_value_changed)
        layout.addWidget(self.slider, 1)

        # دکمه افزایش گامی (+5%)
        self.btn_plus = QPushButton("+")
        self.btn_plus.setToolTip("افزایش ۵ درصد")
        self.btn_plus.setFixedSize(28, 28)
        self.btn_plus.clicked.connect(self._increase_step)
        layout.addWidget(self.btn_plus)

        # برچسب درصد صدا
        self.lbl_percent = QLabel("70%")
        self.lbl_percent.setFixedWidth(44)
        self.lbl_percent.setAlignment(Qt.AlignCenter)
        self.lbl_percent.setStyleSheet("font-weight: bold; color: #F2F4F8;")
        layout.addWidget(self.lbl_percent)

    def _on_slider_value_changed(self, value: int):
        self.lbl_percent.setText(f"{value}%")
        self._update_mute_icon()
        if not self._is_updating_ui:
            self.volume_changed.emit(value)

    def _on_mute_clicked(self):
        new_mute = not self._is_muted
        self.set_muted(new_mute)
        self.mute_toggled.emit(new_mute)

    def _decrease_step(self):
        val = max(0, self.slider.value() - 5)
        self.slider.setValue(val)

    def _increase_step(self):
        val = min(100, self.slider.value() + 5)
        self.slider.setValue(val)

    def _update_mute_icon(self):
        if self._is_muted:
            self.btn_mute.setText("🔇")
            self.btn_mute.setStyleSheet("color: #EB7777;")
        else:
            val = self.slider.value()
            if val == 0:
                self.btn_mute.setText("🔈")
            elif val < 50:
                self.btn_mute.setText("🔉")
            else:
                self.btn_mute.setText("🔊")
            self.btn_mute.setStyleSheet("")

    def set_volume(self, value: int):
        """تنظیم ولوم از منابع خارجی بدون بازخورد مکرر رویداد."""
        clamped = max(0, min(100, int(value)))
        if self.slider.value() == clamped:
            return

        self._is_updating_ui = True
        try:
            self.slider.setValue(clamped)
            self.lbl_percent.setText(f"{clamped}%")
            self._update_mute_icon()
        finally:
            self._is_updating_ui = False

    def set_muted(self, muted: bool):
        """تنظیم وضعیت بصری بی‌صدا از منابع خارجی."""
        self._is_muted = bool(muted)
        self._update_mute_icon()
        self.slider.setEnabled(not self._is_muted)

"""
کارت نمایش دستگاه خروجی صوتی یا دستگاه بلوتوث (DeviceCard)
با طراحی کارت یکپارچه Graphite Dark، برچسب‌های وضعیت و چیدمان واکنش‌گرا بدون سرریز
"""

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy
)

from app.models.audio import SinkDevice
from app.models.bluetooth import BTDevice
from app.ui.components.status_badge import StatusBadge
from app.ui.styles.icon_helper import IconHelper


class DeviceCard(QFrame):
    """کارت نمایش وضعیت و مدیریت خروجی صوتی یا هدفون بلوتوث."""

    set_default_clicked = Signal(str)      # ارسال نام یا شناسه سینک برای پیش‌فرض شدن
    connect_clicked = Signal(str)          # ارسال MAC برای اتصال بلوتوث
    disconnect_clicked = Signal(str)       # ارسال MAC برای قطع بلوتوث
    favorite_toggled = Signal(str, bool)   # ارسال شناسه و وضعیت علاقه‌مندی

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("card", "true")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._target_id: str = ""
        self._action_mode: str = ""
        self._is_favorite = False
        self._init_ui()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(14)

        # آیکون وکتور دستگاه
        self.lbl_icon = QLabel()
        self.lbl_icon.setFixedSize(42, 42)
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.lbl_icon.setStyleSheet("""
            QLabel {
                background-color: #222936;
                border-radius: 21px;
                padding: 6px;
            }
        """)
        main_layout.addWidget(self.lbl_icon)

        # اطلاعات دستگاه (نام، آدرس و بج‌های وضعیت)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)

        title_badge_layout = QHBoxLayout()
        title_badge_layout.setSpacing(8)

        self.lbl_name = QLabel("نام دستگاه")
        self.lbl_name.setStyleSheet("font-size: 14px; font-weight: bold; color: #F2F4F8;")
        self.lbl_name.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        title_badge_layout.addWidget(self.lbl_name)

        self.badge_status = StatusBadge("متصل", variant="success")
        self.badge_status.setVisible(False)
        title_badge_layout.addWidget(self.badge_status)

        self.badge_default = StatusBadge("پیش‌فرض", variant="primary")
        self.badge_default.setVisible(False)
        title_badge_layout.addWidget(self.badge_default)

        self.badge_battery = StatusBadge("باتری: ۱۰۰٪", variant="neutral")
        self.badge_battery.setVisible(False)
        title_badge_layout.addWidget(self.badge_battery)

        title_badge_layout.addStretch()
        info_layout.addLayout(title_badge_layout)

        self.lbl_desc = QLabel("توضیحات دستگاه")
        self.lbl_desc.setStyleSheet("color: #A6AFBD; font-size: 12px;")
        self.lbl_desc.setWordWrap(True)
        info_layout.addWidget(self.lbl_desc)

        main_layout.addLayout(info_layout, 1)

        # بخش دکمه‌های عملیاتی
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)

        # دکمه نشان علاقه‌مندی (ستاره وکتور SVG)
        self.btn_fav = QPushButton()
        self.btn_fav.setProperty("icon_btn", "true")
        self.btn_fav.setCursor(Qt.PointingHandCursor)
        self.btn_fav.setToolTip("افزودن یا حذف از دستگاه‌های محبوب")
        self.btn_fav.setFixedSize(34, 34)
        self.btn_fav.setIconSize(QSize(18, 18))
        self.btn_fav.clicked.connect(self._toggle_favorite)
        action_layout.addWidget(self.btn_fav)

        # دکمه اصلی (انتخاب به عنوان خروجی پیش‌فرض یا اتصال/قطع)
        self.btn_action = QPushButton("انتخاب خروجی")
        self.btn_action.setCursor(Qt.PointingHandCursor)
        self.btn_action.setProperty("primary", "true")
        self.btn_action.setMinimumHeight(34)
        self.btn_action.clicked.connect(self._on_action_clicked)
        action_layout.addWidget(self.btn_action)

        main_layout.addLayout(action_layout)

    def set_sink_device(self, device: SinkDevice, is_favorite: bool = False):
        """تنظیم داده‌های کارت از روی مدل SinkDevice پایپ‌وایر."""
        self._target_id = device.name
        self._is_favorite = is_favorite
        self._update_favorite_icon()

        self.lbl_name.setText(device.display_name)
        mute_note = " | بی‌صدا" if device.mute else ""
        self.lbl_desc.setText(f"حجم صدا: {device.volume_percent}٪{mute_note}  •  {device.port_display_name}")

        if device.is_bluetooth:
            self.lbl_icon.setPixmap(IconHelper.get_pixmap("headphones", 24))
        elif "hdmi" in device.name.lower():
            self.lbl_icon.setPixmap(IconHelper.get_pixmap("display-hdmi", 24))
        else:
            self.lbl_icon.setPixmap(IconHelper.get_pixmap("speaker-high", 24))

        self.badge_default.setVisible(device.is_default)
        self.badge_status.setVisible(False)
        self.badge_battery.setVisible(False)

        if device.is_default:
            self._action_mode = ""
            self.btn_action.setText("خروجی فعال")
            self.btn_action.setEnabled(False)
            self.btn_action.setProperty("primary", "false")
            self.btn_action.setProperty("danger", "false")
        else:
            self._action_mode = "set_default"
            self.btn_action.setText("انتخاب خروجی")
            self.btn_action.setEnabled(True)
            self.btn_action.setProperty("primary", "true")
            self.btn_action.setProperty("danger", "false")

        self.btn_action.style().unpolish(self.btn_action)
        self.btn_action.style().polish(self.btn_action)

    def set_bluetooth_device(self, device: BTDevice, is_favorite: bool = False):
        """تنظیم داده‌های کارت از روی مدل BTDevice بلوتوث."""
        self._target_id = device.mac_address
        self._is_favorite = is_favorite
        self._update_favorite_icon()

        self.lbl_name.setText(device.display_name)
        # جهت آدرس MAC همیشه LTR است تا خوانا بماند
        self.lbl_desc.setText(f"آدرس سخت‌افزاری: <span dir='ltr'>{device.mac_address}</span>")

        if device.is_headset:
            self.lbl_icon.setPixmap(IconHelper.get_pixmap("headphones", 24))
        else:
            self.lbl_icon.setPixmap(IconHelper.get_pixmap("bluetooth", 24))

        self.badge_default.setVisible(False)

        if device.connected:
            self._action_mode = "disconnect"
            self.badge_status.set_variant("success", "متصل")
            self.badge_status.setVisible(True)
            self.btn_action.setText("قطع اتصال")
            self.btn_action.setProperty("danger", "true")
            self.btn_action.setProperty("primary", "false")
        else:
            self._action_mode = "connect"
            self.badge_status.set_variant("neutral", "قطع")
            self.badge_status.setVisible(True)
            self.btn_action.setText("اتصال")
            self.btn_action.setProperty("danger", "false")
            self.btn_action.setProperty("primary", "true")

        # نمایش باتری واقعی
        if device.battery_percentage is not None:
            self.badge_battery.set_variant("neutral", f"باتری: {device.battery_percentage}٪")
            self.badge_battery.setVisible(True)
        else:
            self.badge_battery.setVisible(False)

        self.btn_action.setEnabled(True)
        self.btn_action.style().unpolish(self.btn_action)
        self.btn_action.style().polish(self.btn_action)

    def _toggle_favorite(self):
        self._is_favorite = not self._is_favorite
        self._update_favorite_icon()
        self.favorite_toggled.emit(self._target_id, self._is_favorite)

    def _update_favorite_icon(self):
        self.btn_fav.setIcon(IconHelper.star_icon(self._is_favorite))
        self.btn_fav.setText("")

    def _on_action_clicked(self):
        if self._action_mode == "set_default":
            self.set_default_clicked.emit(self._target_id)
        elif self._action_mode == "connect":
            self.connect_clicked.emit(self._target_id)
        elif self._action_mode == "disconnect":
            self.disconnect_clicked.emit(self._target_id)

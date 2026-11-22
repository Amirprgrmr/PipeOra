"""
صفحه داشبورد اصلی AM Audio Control
نمایش وضعیت سرویس‌ها، کارت خروجی فعال، اسلایدر اصلی و سوئیچ سریع میان دستگاه‌ها
"""

from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QPushButton, QGridLayout
)

from app.core.audio_manager import AudioManager
from app.core.bluetooth_manager import BluetoothManager
from app.core.profile_manager import ProfileManager
from app.core.system_detector import SystemDetector
from app.core.config_manager import ConfigManager
from app.models.audio import SinkDevice
from app.models.bluetooth import BTDevice
from app.ui.components.volume_slider import VolumeSlider
from app.ui.components.status_badge import StatusBadge


class DashboardPage(QWidget):
    """صفحه اصلی و داشبورد مرکزی نرم‌افزار."""

    navigate_to_page = Signal(str)

    def __init__(
        self,
        audio_mgr: AudioManager,
        bt_mgr: BluetoothManager,
        profile_mgr: ProfileManager,
        detector: SystemDetector,
        config_mgr: ConfigManager,
        parent=None
    ):
        super().__init__(parent)
        self.audio_mgr = audio_mgr
        self.bt_mgr = bt_mgr
        self.profile_mgr = profile_mgr
        self.detector = detector
        self.config_mgr = config_mgr

        self._active_sink: Optional[SinkDevice] = None
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # ------------------ هدر داشبورد ------------------
        header_layout = QHBoxLayout()
        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(4)

        lbl_title = QLabel("داشبورد مدیریت صدا")
        lbl_title.setObjectName("pageTitle")
        header_text_layout.addWidget(lbl_title)

        lbl_subtitle = QLabel("وضعیت زنده خروجی صوتی و دستگاه‌های متصل")
        lbl_subtitle.setObjectName("mutedText")
        header_text_layout.addWidget(lbl_subtitle)

        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()

        # بج‌های وضعیت سرویس‌های سیستمی
        self.badge_pw = StatusBadge("PipeWire: فعال", variant="success")
        header_layout.addWidget(self.badge_pw)

        self.badge_bt = StatusBadge("بلوتوث: روشن", variant="success")
        header_layout.addWidget(self.badge_bt)

        main_layout.addLayout(header_layout)

        # اسکرول اریا برای محتوا
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(20)

        # ------------------ کارت برجسته خروجی فعال (Hero Card) ------------------
        self.hero_card = QFrame()
        self.hero_card.setProperty("card", "true")
        self.hero_card.setStyleSheet("""
            QFrame[card="true"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E2532, stop:1 #161A22);
                border: 1px solid #3B4559;
            }
        """)
        hero_layout = QVBoxLayout(self.hero_card)
        hero_layout.setContentsMargins(20, 20, 20, 20)
        hero_layout.setSpacing(16)

        # اطلاعات دستگاه فعال
        dev_info_layout = QHBoxLayout()

        self.hero_icon = QLabel("🔊")
        self.hero_icon.setFixedSize(52, 52)
        self.hero_icon.setAlignment(Qt.AlignCenter)
        self.hero_icon.setStyleSheet("""
            QLabel {
                background-color: rgba(103, 201, 243, 0.15);
                border: 1px solid rgba(103, 201, 243, 0.4);
                border-radius: 26px;
                font-size: 26px;
            }
        """)
        dev_info_layout.addWidget(self.hero_icon)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        name_badges_layout = QHBoxLayout()
        name_badges_layout.setSpacing(10)

        self.lbl_active_name = QLabel("بلندگوی داخلی (Built-in Audio)")
        self.lbl_active_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #F2F4F8;")
        name_badges_layout.addWidget(self.lbl_active_name)

        self.badge_active_type = StatusBadge("خروجی آنالوگ", variant="primary")
        name_badges_layout.addWidget(self.badge_active_type)

        self.badge_active_profile = StatusBadge("پخش باکیفیت", variant="success")
        name_badges_layout.addWidget(self.badge_active_profile)

        name_badges_layout.addStretch()
        title_layout.addLayout(name_badges_layout)

        self.lbl_active_desc = QLabel("خروجی پیش‌فرض صوتی سیستم لینوکس")
        self.lbl_active_desc.setObjectName("mutedText")
        title_layout.addWidget(self.lbl_active_desc)

        dev_info_layout.addLayout(title_layout, 1)
        hero_layout.addLayout(dev_info_layout)

        # اسلایدر اصلی کنترل ولوم
        slider_box = QVBoxLayout()
        slider_box.setSpacing(8)

        lbl_vol_title = QLabel("کنترل بلندی صدای خروجی:")
        lbl_vol_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #A6AFBD;")
        slider_box.addWidget(lbl_vol_title)

        self.main_volume_slider = VolumeSlider()
        self.main_volume_slider.volume_changed.connect(self._on_volume_changed)
        self.main_volume_slider.mute_toggled.connect(self._on_mute_toggled)
        slider_box.addWidget(self.main_volume_slider)

        hero_layout.addLayout(slider_box)
        container_layout.addWidget(self.hero_card)

        # ------------------ بخش سوئیچ سریع خروجی‌ها ------------------
        quick_switch_section = QVBoxLayout()
        quick_switch_section.setSpacing(10)

        lbl_quick_title = QLabel("سوئیچ سریع خروجی صدا")
        lbl_quick_title.setObjectName("sectionTitle")
        quick_switch_section.addWidget(lbl_quick_title)

        self.quick_buttons_layout = QHBoxLayout()
        self.quick_buttons_layout.setSpacing(12)
        quick_switch_section.addLayout(self.quick_buttons_layout)

        container_layout.addLayout(quick_switch_section)

        # ------------------ کارت دسترسی سریع هدفون بلوتوث ------------------
        bt_section = QVBoxLayout()
        bt_section.setSpacing(10)

        lbl_bt_title = QLabel("دستگاه‌های بلوتوث شناخته‌شده")
        lbl_bt_title.setObjectName("sectionTitle")
        bt_section.addWidget(lbl_bt_title)

        self.bt_quick_frame = QFrame()
        self.bt_quick_frame.setProperty("card", "true")
        self.bt_quick_layout = QVBoxLayout(self.bt_quick_frame)
        self.bt_quick_layout.setContentsMargins(14, 14, 14, 14)
        self.bt_quick_layout.setSpacing(10)

        bt_section.addWidget(self.bt_quick_frame)
        container_layout.addLayout(bt_section)

        container_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def refresh_data(self):
        """به‌روزرسانی داده‌های داشبورد بر اساس وضعیت واقعی سیستم."""
        # بررسی وضعیت سلامت سرویس‌ها
        pw_ok = self.detector.check_pipewire()
        self.badge_pw.set_variant("success" if pw_ok else "error", "PipeWire: فعال" if pw_ok else "PipeWire: قطع")

        bt_ok = self.bt_mgr.is_bluetooth_powered()
        self.badge_bt.set_variant("success" if bt_ok else "neutral", "بلوتوث: روشن" if bt_ok else "بلوتوث: خاموش")

        # خواندن خروجی فعال
        sinks = self.audio_mgr.get_output_sinks()
        default_sink = self.audio_mgr.get_default_sink()
        self._active_sink = default_sink

        if default_sink:
            self.lbl_active_name.setText(default_sink.display_name)
            self.main_volume_slider.set_volume(default_sink.volume_percent)
            self.main_volume_slider.set_muted(default_sink.mute)

            if default_sink.is_bluetooth:
                self.hero_icon.setText("🎧")
                self.badge_active_type.set_variant("primary", "هدفون بلوتوث")
                # بررسی پروفایل A2DP
                if default_sink.card_id:
                    profs = self.profile_mgr.get_card_profiles(str(default_sink.card_id))
                    active_p = next((p for p in profs if p.is_active), None)
                    if active_p:
                        self.badge_active_profile.set_variant("success", active_p.persian_name)
                    else:
                        self.badge_active_profile.set_variant("success", "پخش استریوی باکیفیت (A2DP)")
            elif "hdmi" in default_sink.name.lower():
                self.hero_icon.setText("🖥️")
                self.badge_active_type.set_variant("neutral", "خروجی دیجیتال HDMI")
                self.badge_active_profile.set_variant("neutral", "دیجیتال")
            else:
                self.hero_icon.setText("🔊")
                self.badge_active_type.set_variant("neutral", "بلندگوی داخلی لپ‌تاپ")
                self.badge_active_profile.set_variant("neutral", "استریو آنالوگ")
        else:
            self.lbl_active_name.setText("هیچ خروجی صوتی فعالی یافت نشد")
            self.badge_active_type.set_variant("error", "بدون خروجی")
            self.badge_active_profile.setVisible(False)

        # به‌روزرسانی کلیدهای سوئیچ سریع
        self._update_quick_sinks(sinks)

        # به‌روزرسانی کارت هدفون‌های شناخته‌شده
        self._update_bluetooth_summary()

    def _update_quick_sinks(self, sinks: List[SinkDevice]):
        """بازسازی کلیدهای سریع انتخاب خروجی."""
        while self.quick_buttons_layout.count():
            item = self.quick_buttons_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for s in sinks:
            btn = QPushButton()
            icon_char = "🎧" if s.is_bluetooth else ("🖥️" if "hdmi" in s.name.lower() else "🔊")
            btn.setText(f"{icon_char}  {s.display_name}")
            btn.setFixedHeight(44)

            if s.is_default:
                btn.setProperty("primary", "true")
            else:
                btn.setProperty("primary", "false")

            sink_target = s.name
            btn.clicked.connect(lambda checked=False, target=sink_target: self._switch_sink(target))
            self.quick_buttons_layout.addWidget(btn)

        self.quick_buttons_layout.addStretch()

    def _update_bluetooth_summary(self):
        """نمایش خلاصه دستگاه‌های بلوتوث جفت‌شده در داشبورد."""
        while self.bt_quick_layout.count():
            item = self.bt_quick_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        paired = self.bt_mgr.get_paired_devices(audio_only=True)
        if not paired:
            lbl_empty = QLabel("هیچ دستگاه صوتی بلوتوثی جفت نشده است.")
            lbl_empty.setObjectName("mutedText")
            self.bt_quick_layout.addWidget(lbl_empty)
            return

        for dev in paired:
            row = QHBoxLayout()
            row.setSpacing(12)

            lbl_icon = QLabel("🎧" if dev.is_headset else "📻")
            lbl_icon.setFixedSize(28, 28)
            lbl_icon.setAlignment(Qt.AlignCenter)
            row.addWidget(lbl_icon)

            lbl_name = QLabel(dev.display_name)
            lbl_name.setStyleSheet("font-weight: 600; color: #F2F4F8;")
            row.addWidget(lbl_name)

            if dev.connected:
                badge = StatusBadge("متصل", variant="success")
                row.addWidget(badge)
            else:
                badge = StatusBadge("قطع", variant="neutral")
                row.addWidget(badge)

            if dev.battery_percentage is not None:
                bat_badge = StatusBadge(f"{dev.battery_percentage}٪", variant="primary")
                row.addWidget(bat_badge)

            row.addStretch()

            btn_toggle = QPushButton("قطع اتصال" if dev.connected else "اتصال")
            if dev.connected:
                btn_toggle.setProperty("danger", "true")
            else:
                btn_toggle.setProperty("primary", "true")

            mac_target = dev.mac_address
            is_conn = dev.connected
            btn_toggle.clicked.connect(lambda checked=False, m=mac_target, c=is_conn: self._toggle_bt(m, c))
            row.addWidget(btn_toggle)

            self.bt_quick_layout.addLayout(row)

    def _on_volume_changed(self, volume: int):
        if self._active_sink:
            self.audio_mgr.set_volume(self._active_sink.name, volume)

    def _on_mute_toggled(self, muted: bool):
        if self._active_sink:
            self.audio_mgr.set_mute(self._active_sink.name, muted)

    def _switch_sink(self, sink_name: str):
        self.audio_mgr.set_default_sink(sink_name)
        self.refresh_data()

    def _toggle_bt(self, mac: str, currently_connected: bool):
        if currently_connected:
            self.bt_mgr.disconnect_device(mac)
        else:
            self.bt_mgr.connect_device(mac)
        self.refresh_data()

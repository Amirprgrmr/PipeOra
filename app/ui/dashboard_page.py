"""
صفحه داشبورد اصلی PipeOra
نمایش وضعیت سرویس‌ها، کارت خروجی فعال، اسلایدر اصلی، مدیریت حالت هدست و سوئیچ سریع میان دستگاه‌ها
"""

from typing import List, Optional
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QPushButton, QGridLayout, QSizePolicy, QLayout
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
from app.ui.components.headset_mode_card import HeadsetModeCard
from app.ui.styles.icon_helper import IconHelper
from app.ui.styles.layout_utils import clear_layout


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
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(18)

        # ------------------ هدر داشبورد ------------------
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(4)

        lbl_title = QLabel("داشبورد مدیریت صدا")
        lbl_title.setObjectName("pageTitle")
        header_text_layout.addWidget(lbl_title)

        lbl_subtitle = QLabel("وضعیت زنده خروجی صوتی و دستگاه‌های متصل")
        lbl_subtitle.setObjectName("mutedText")
        header_text_layout.addWidget(lbl_subtitle)

        header_layout.addLayout(header_text_layout, 1)

        # بج‌های وضعیت سرویس‌های سیستمی
        self.badge_pw = StatusBadge("PipeWire: فعال", variant="success")
        header_layout.addWidget(self.badge_pw)

        self.badge_bt = StatusBadge("بلوتوث: روشن", variant="success")
        header_layout.addWidget(self.badge_bt)

        main_layout.addLayout(header_layout)

        # اسکرول اریا برای محتوا
        scroll = QScrollArea()
        scroll.setObjectName("pageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        container.setObjectName("pageScrollContainer")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        container_layout = QVBoxLayout(container)
        container_layout.setSizeConstraint(QLayout.SetMinimumSize)
        container_layout.setContentsMargins(0, 0, 0, 6)
        container_layout.setSpacing(18)

        # ------------------ کارت برجسته خروجی فعال (Hero Card) ------------------
        self.hero_card = QFrame()
        self.hero_card.setObjectName("heroCard")
        self.hero_card.setProperty("card", "true")
        self.hero_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hero_card.setStyleSheet("""
            QFrame#heroCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E2532, stop:1 #161A22);
                border: 1px solid #3B4559;
                border-radius: 12px;
            }
        """)
        hero_layout = QVBoxLayout(self.hero_card)
        hero_layout.setContentsMargins(20, 18, 20, 18)
        hero_layout.setSpacing(14)

        # اطلاعات دستگاه فعال
        dev_info_layout = QHBoxLayout()
        dev_info_layout.setSpacing(14)

        self.hero_icon = QLabel()
        self.hero_icon.setFixedSize(50, 50)
        self.hero_icon.setAlignment(Qt.AlignCenter)
        self.hero_icon.setStyleSheet("""
            QLabel {
                background-color: rgba(103, 201, 243, 0.15);
                border: 1px solid rgba(103, 201, 243, 0.4);
                border-radius: 25px;
                padding: 8px;
            }
        """)
        dev_info_layout.addWidget(self.hero_icon)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(6)

        name_badges_layout = QHBoxLayout()
        name_badges_layout.setSpacing(8)

        self.lbl_active_name = QLabel("بلندگوی داخلی (Built-in Audio)")
        self.lbl_active_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #F2F4F8;")
        self.lbl_active_name.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        name_badges_layout.addWidget(self.lbl_active_name)

        self.badge_active_type = StatusBadge("خروجی آنالوگ", variant="primary")
        name_badges_layout.addWidget(self.badge_active_type)

        self.badge_active_profile = StatusBadge("پخش باکیفیت", variant="success")
        name_badges_layout.addWidget(self.badge_active_profile)

        self.badge_active_battery = StatusBadge("باتری: ۱۰۰٪", variant="neutral")
        self.badge_active_battery.setVisible(False)
        name_badges_layout.addWidget(self.badge_active_battery)

        name_badges_layout.addStretch()
        title_layout.addLayout(name_badges_layout)

        self.lbl_active_desc = QLabel("خروجی پیش‌فرض صوتی سیستم لینوکس")
        self.lbl_active_desc.setObjectName("mutedText")
        title_layout.addWidget(self.lbl_active_desc)

        dev_info_layout.addLayout(title_layout, 1)
        hero_layout.addLayout(dev_info_layout)

        # اسلایدر اصلی کنترل ولوم
        slider_box = QVBoxLayout()
        slider_box.setSpacing(6)

        lbl_vol_title = QLabel("کنترل بلندی صدای خروجی:")
        lbl_vol_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #A6AFBD;")
        slider_box.addWidget(lbl_vol_title)

        self.main_volume_slider = VolumeSlider()
        self.main_volume_slider.volume_changed.connect(self._on_volume_changed)
        self.main_volume_slider.mute_toggled.connect(self._on_mute_toggled)
        slider_box.addWidget(self.main_volume_slider)

        hero_layout.addLayout(slider_box)
        container_layout.addWidget(self.hero_card)

        # ------------------ کارت اختصاصی انتخاب حالت هدست بلوتوث (میکروفن / موسیقی) ------------------
        self.headset_mode_card = HeadsetModeCard(self.profile_mgr, self.config_mgr)
        self.headset_mode_card.mode_changed.connect(lambda mode: self.refresh_data())
        container_layout.addWidget(self.headset_mode_card)

        # ------------------ بخش سوئیچ سریع خروجی‌ها (گرید واکنش‌گرا) ------------------
        quick_switch_section = QVBoxLayout()
        quick_switch_section.setSpacing(10)

        lbl_quick_title = QLabel("سوئیچ سریع خروجی صدا")
        lbl_quick_title.setObjectName("sectionTitle")
        quick_switch_section.addWidget(lbl_quick_title)

        self.quick_buttons_layout = QGridLayout()
        self.quick_buttons_layout.setSpacing(10)
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
        self.bt_quick_layout.setContentsMargins(16, 14, 16, 14)
        self.bt_quick_layout.setSpacing(10)

        bt_section.addWidget(self.bt_quick_frame)
        container_layout.addLayout(bt_section)

        container_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def refresh_data(self):
        """به‌روزرسانی داده‌های داشبورد بر اساس وضعیت واقعی سیستم."""
        pw_ok = self.detector.check_pipewire()
        self.badge_pw.set_variant("success" if pw_ok else "error", "PipeWire: فعال" if pw_ok else "PipeWire: قطع")

        bt_ok = self.bt_mgr.is_bluetooth_powered()
        self.badge_bt.set_variant("success" if bt_ok else "neutral", "بلوتوث: روشن" if bt_ok else "بلوتوث: خاموش")

        paired = self.bt_mgr.get_paired_devices(audio_only=True)
        sinks = self.audio_mgr.get_output_sinks()
        default_sink = next((s for s in sinks if s.is_default), sinks[0] if sinks else None)
        self._active_sink = default_sink

        if default_sink:
            self.lbl_active_name.setText(default_sink.display_name)
            self.lbl_active_desc.setText(f"پورت فعال: {default_sink.port_display_name}")
            self.badge_active_profile.setVisible(True)
            self.badge_active_battery.setVisible(False)
            self.main_volume_slider.set_volume(default_sink.volume_percent)
            self.main_volume_slider.set_muted(default_sink.mute)

            if default_sink.is_bluetooth:
                self.hero_icon.setPixmap(IconHelper.get_pixmap("headphones", 28))
                self.badge_active_type.set_variant("primary", "هدفون بلوتوث")

                card_target = default_sink.card_name or (str(default_sink.card_id) if default_sink.card_id else None)
                self.headset_mode_card.set_target_card(card_target)

                mode = self.headset_mode_card._current_mode if card_target else "other"
                if mode == "a2dp":
                    self.badge_active_profile.set_variant("success", "استریو A2DP (میکروفن خاموش)")
                elif mode == "hfp":
                    self.badge_active_profile.set_variant("warning", "مکالمه HFP (میکروفن فعال)")
                else:
                    self.badge_active_profile.set_variant("success", "پخش باکیفیت")

                # نمایش باتری هدفون متصل در Hero Card
                for dev in paired:
                    if dev.connected and dev.battery_percentage is not None:
                        if dev.mac_address.lower().replace(":", "_") in default_sink.name.lower():
                            self.badge_active_battery.set_variant("neutral", f"باتری: {dev.battery_percentage}٪")
                            self.badge_active_battery.setVisible(True)
                            break

            elif "hdmi" in default_sink.name.lower():
                self.hero_icon.setPixmap(IconHelper.get_pixmap("display-hdmi", 28))
                self.badge_active_type.set_variant("neutral", "خروجی دیجیتال HDMI")
                self.badge_active_profile.set_variant("neutral", "دیجیتال")
                self.headset_mode_card.setVisible(False)
            else:
                self.hero_icon.setPixmap(IconHelper.get_pixmap("speaker-high", 28))
                self.badge_active_type.set_variant("neutral", "بلندگوی داخلی لپ‌تاپ")
                self.badge_active_profile.set_variant("neutral", "استریو آنالوگ")
                self.headset_mode_card.setVisible(False)
        else:
            self.hero_icon.setPixmap(IconHelper.get_pixmap("speaker-mute", 28))
            self.lbl_active_name.setText("هیچ خروجی صوتی فعالی یافت نشد")
            self.lbl_active_desc.setText("سرویس صوتی در دسترس نیست")
            self.badge_active_type.set_variant("error", "بدون خروجی")
            self.badge_active_profile.setVisible(False)
            self.badge_active_battery.setVisible(False)
            self.headset_mode_card.setVisible(False)

        self._update_quick_sinks(sinks)
        self._update_bluetooth_summary(paired)

    def _update_quick_sinks(self, sinks: List[SinkDevice]):
        """بازسازی گرید واکنش‌گرای کلیدهای انتخاب خروجی بدون سرریز افقی."""
        clear_layout(self.quick_buttons_layout)

        if not sinks:
            lbl = QLabel("خروجی صوتی‌ای برای سوئیچ سریع یافت نشد.")
            lbl.setObjectName("mutedText")
            self.quick_buttons_layout.addWidget(lbl, 0, 0)
            return

        cols = 2 if len(sinks) <= 4 else 3
        for idx, s in enumerate(sinks):
            btn = QPushButton()
            btn.setCursor(Qt.PointingHandCursor)
            icon_name = "headphones" if s.is_bluetooth else ("display-hdmi" if "hdmi" in s.name.lower() else "speaker-high")
            btn.setIcon(IconHelper.get_icon(icon_name))
            btn.setIconSize(QSize(18, 18))
            btn.setText(f"  {s.display_name}")
            btn.setFixedHeight(42)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            btn.setProperty("primary", "true" if s.is_default else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

            sink_target = s.name
            btn.clicked.connect(lambda checked=False, target=sink_target: self._switch_sink(target))
            self.quick_buttons_layout.addWidget(btn, idx // cols, idx % cols)

    def _update_bluetooth_summary(self, paired: List[BTDevice]):
        """نمایش خلاصه دستگاه‌های بلوتوث جفت‌شده بدون باقی ماندن ویجت یتیم."""
        clear_layout(self.bt_quick_layout)

        if not paired:
            lbl_empty = QLabel("هیچ دستگاه صوتی بلوتوثی جفت نشده است.")
            lbl_empty.setObjectName("mutedText")
            self.bt_quick_layout.addWidget(lbl_empty)
            return

        for dev in paired:
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(0, 2, 0, 2)
            row.setSpacing(12)

            lbl_icon = QLabel()
            icon_name = "headphones" if dev.is_headset else "bluetooth"
            lbl_icon.setPixmap(IconHelper.get_pixmap(icon_name, 22))
            lbl_icon.setFixedSize(28, 28)
            lbl_icon.setAlignment(Qt.AlignCenter)
            row.addWidget(lbl_icon)

            lbl_name = QLabel(dev.display_name)
            lbl_name.setStyleSheet("font-weight: 600; color: #F2F4F8;")
            row.addWidget(lbl_name)

            badge = StatusBadge("متصل" if dev.connected else "قطع", variant="success" if dev.connected else "neutral")
            row.addWidget(badge)

            if dev.battery_percentage is not None:
                bat_badge = StatusBadge(f"باتری: {dev.battery_percentage}٪", variant="primary")
                row.addWidget(bat_badge)

            row.addStretch()

            btn_toggle = QPushButton("قطع اتصال" if dev.connected else "اتصال")
            btn_toggle.setCursor(Qt.PointingHandCursor)
            btn_toggle.setMinimumHeight(32)
            if dev.connected:
                btn_toggle.setProperty("danger", "true")
                btn_toggle.setProperty("primary", "false")
            else:
                btn_toggle.setProperty("danger", "false")
                btn_toggle.setProperty("primary", "true")

            mac_target = dev.mac_address
            is_conn = dev.connected
            btn_toggle.clicked.connect(lambda checked=False, m=mac_target, c=is_conn: self._toggle_bt(m, c))
            row.addWidget(btn_toggle)

            self.bt_quick_layout.addWidget(row_widget)

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

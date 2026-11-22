"""
صفحه مدیریت دستگاه‌های صوتی و خروجی‌ها (DevicesPage)
فهرست کامل خروجی‌های صدا، مدیریت پروفایل‌های سخت‌افزاری A2DP و میکسر صدای برنامه‌ها
"""

from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QPushButton, QComboBox
)

from app.core.audio_manager import AudioManager
from app.core.profile_manager import ProfileManager
from app.core.config_manager import ConfigManager
from app.models.audio import SinkDevice, AppStream
from app.ui.components.device_card import DeviceCard
from app.ui.components.volume_slider import VolumeSlider
from app.ui.components.status_badge import StatusBadge
from app.ui.components.headset_mode_card import HeadsetModeCard
from app.ui.styles.icon_helper import IconHelper


class DevicesPage(QWidget):
    """صفحه مدیریت و تنظیم خروجی‌های صدا و استریم‌ها."""

    def __init__(
        self,
        audio_mgr: AudioManager,
        profile_mgr: ProfileManager,
        config_mgr: ConfigManager,
        parent=None
    ):
        super().__init__(parent)
        self.audio_mgr = audio_mgr
        self.profile_mgr = profile_mgr
        self.config_mgr = config_mgr

        self._active_sink: Optional[SinkDevice] = None
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # عنوان صفحه
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        lbl_title = QLabel("دستگاه‌های خروجی صدا")
        lbl_title.setObjectName("pageTitle")
        header_layout.addWidget(lbl_title)

        lbl_desc = QLabel("مدیریت خروجی‌های صوتی فعال، پروفایل‌های پخش و حجم صدای برنامه‌ها")
        lbl_desc.setObjectName("mutedText")
        header_layout.addWidget(lbl_desc)
        main_layout.addLayout(header_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        self.container_layout = QVBoxLayout(container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(24)

        # ------------------ بخش اول: خروجی‌های صوتی سیستم ------------------
        sinks_section = QVBoxLayout()
        sinks_section.setSpacing(12)

        lbl_sinks_title = QLabel("خروجی‌های صوتی شناسایی‌شده (Sinks)")
        lbl_sinks_title.setObjectName("sectionTitle")
        sinks_section.addWidget(lbl_sinks_title)

        self.sinks_container = QVBoxLayout()
        self.sinks_container.setSpacing(10)
        sinks_section.addLayout(self.sinks_container)

        self.container_layout.addLayout(sinks_section)

        # ------------------ بخش دوم: مدیریت حالت و پروفایل صوتی خروجی فعال ------------------
        self.headset_mode_card = HeadsetModeCard(self.profile_mgr)
        self.headset_mode_card.mode_changed.connect(lambda mode: self.refresh_data())
        self.container_layout.addWidget(self.headset_mode_card)

        self.profile_section = QFrame()
        self.profile_section.setProperty("card", "true")
        profile_layout = QVBoxLayout(self.profile_section)
        profile_layout.setSpacing(12)

        lbl_prof_title = QLabel("پروفایل صوتی خروجی فعال (اولویت با کیفیت استریو A2DP)")
        lbl_prof_title.setObjectName("sectionTitle")
        profile_layout.addWidget(lbl_prof_title)

        prof_row = QHBoxLayout()
        prof_row.setSpacing(12)

        lbl_prof_select = QLabel("انتخاب پروفایل پخش:")
        lbl_prof_select.setStyleSheet("color: #A6AFBD;")
        prof_row.addWidget(lbl_prof_select)

        self.combo_profiles = QComboBox()
        self.combo_profiles.currentIndexChanged.connect(self._on_profile_selected)
        prof_row.addWidget(self.combo_profiles, 1)

        self.btn_auto_a2dp = QPushButton("تنظیم خودکار A2DP")
        self.btn_auto_a2dp.setProperty("primary", "true")
        self.btn_auto_a2dp.clicked.connect(self._enforce_a2dp)
        prof_row.addWidget(self.btn_auto_a2dp)

        profile_layout.addLayout(prof_row)
        self.container_layout.addWidget(self.profile_section)

        # ------------------ بخش سوم: میکسر صدای برنامه‌ها ------------------
        apps_section = QVBoxLayout()
        apps_section.setSpacing(12)

        lbl_apps_title = QLabel("صدای برنامه‌های در حال پخش (App Mixer)")
        lbl_apps_title.setObjectName("sectionTitle")
        apps_section.addWidget(lbl_apps_title)

        self.apps_container = QVBoxLayout()
        self.apps_container.setSpacing(10)
        apps_section.addLayout(self.apps_container)

        self.container_layout.addLayout(apps_section)

        self.container_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def refresh_data(self):
        """بارگذاری مجدد اطلاعات خروجی‌ها و استریم‌ها."""
        sinks = self.audio_mgr.get_output_sinks()
        default_sink = self.audio_mgr.get_default_sink()
        self._active_sink = default_sink
        favorite_id = self.config_mgr.get_favorite_device()

        # بازسازی لیست سینک‌ها
        while self.sinks_container.count():
            item = self.sinks_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for s in sinks:
            card = DeviceCard()
            is_fav = (favorite_id == s.name)
            card.set_sink_device(s, is_favorite=is_fav)
            target_name = s.name
            card.set_default_clicked.connect(lambda target=target_name: self._set_default_sink(target))
            card.favorite_toggled.connect(self._on_favorite_toggled)
            self.sinks_container.addWidget(card)

        # به‌روزرسانی پروفایل‌های کارت فعال
        self._update_profiles(default_sink)

        # به‌روزرسانی صدای برنامه‌ها
        self._update_apps()

    def _update_profiles(self, default_sink: Optional[SinkDevice]):
        """به‌روزرسانی پروفایل‌های کارت صوتی فعال و کارت حالت هدست."""
        self.combo_profiles.blockSignals(True)
        self.combo_profiles.clear()

        card_target = default_sink.card_name or (str(default_sink.card_id) if default_sink and default_sink.card_id else None) if default_sink else None

        if not default_sink or not card_target:
            self.profile_section.setVisible(False)
            self.headset_mode_card.setVisible(False)
            self.combo_profiles.blockSignals(False)
            return

        # به‌روزرسانی کارت اختصاصی حالت هدست اگر هدفون بلوتوث باشد
        self.headset_mode_card.set_target_card(card_target)

        self.profile_section.setVisible(True)
        profiles = self.profile_mgr.get_card_profiles(card_target)

        active_idx = 0
        for i, p in enumerate(profiles):
            self.combo_profiles.addItem(p.persian_name, p.name)
            if p.is_active:
                active_idx = i

        self.combo_profiles.setCurrentIndex(active_idx)
        self.combo_profiles.blockSignals(False)

    def _update_apps(self):
        """به‌روزرسانی لیست برنامه‌های در حال پخش صدا."""
        while self.apps_container.count():
            item = self.apps_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        apps = self.audio_mgr.get_sink_inputs()
        if not apps:
            lbl_no_apps = QLabel("در حال حاضر هیچ برنامه‌ای صدا پخش نمی‌کند.")
            lbl_no_apps.setObjectName("mutedText")
            self.apps_container.addWidget(lbl_no_apps)
            return

        for app in apps:
            row_card = QFrame()
            row_card.setProperty("card", "true")
            row_layout = QHBoxLayout(row_card)
            row_layout.setContentsMargins(14, 12, 14, 12)
            row_layout.setSpacing(14)

            lbl_app_name = QLabel(app.name)
            lbl_app_name.setStyleSheet("font-weight: bold; color: #F2F4F8; min-width: 140px;")
            row_layout.addWidget(lbl_app_name)

            slider = VolumeSlider()
            slider.set_volume(app.volume_percent)
            slider.set_muted(app.mute)
            app_id = app.id
            slider.volume_changed.connect(lambda val, aid=app_id: self.audio_mgr.set_sink_input_volume(aid, val))
            row_layout.addWidget(slider, 1)

            self.apps_container.addWidget(row_card)

    def _set_default_sink(self, sink_name: str):
        self.audio_mgr.set_default_sink(sink_name)
        self.refresh_data()

    def _on_favorite_toggled(self, device_id: str, is_fav: bool):
        if is_fav:
            self.config_mgr.set_favorite_device(device_id)
        else:
            if self.config_mgr.get_favorite_device() == device_id:
                self.config_mgr.set_favorite_device(None)
        self.refresh_data()

    def _on_profile_selected(self, index: int):
        if index < 0 or not self._active_sink or not self._active_sink.card_id:
            return
        profile_name = self.combo_profiles.currentData()
        if profile_name:
            self.profile_mgr.set_card_profile(str(self._active_sink.card_id), profile_name)
            self.refresh_data()

    def _enforce_a2dp(self):
        if self._active_sink and self._active_sink.card_id:
            self.profile_mgr.switch_to_a2dp_if_possible(str(self._active_sink.card_id))
            self.refresh_data()

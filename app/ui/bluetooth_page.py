"""
صفحه مدیریت بلوتوث (BluetoothPage)
مدیریت اتصال هدفون‌ها و دستگاه‌های صوتی بلوتوث، مشاهده باتری واقعی و اسکن دستگاه‌ها
"""

from typing import List, Optional
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QPushButton
)

from app.core.bluetooth_manager import BluetoothManager
from app.core.profile_manager import ProfileManager
from app.core.config_manager import ConfigManager
from app.models.bluetooth import BTDevice
from app.ui.components.device_card import DeviceCard
from app.ui.components.status_badge import StatusBadge
from app.ui.components.headset_mode_card import HeadsetModeCard
from app.ui.styles.icon_helper import IconHelper


class BluetoothPage(QWidget):
    """صفحه اختصاصی مدیریت بلوتوث و تجهیزات صوتی وایرلس."""

    def __init__(
        self,
        bt_mgr: BluetoothManager,
        profile_mgr: ProfileManager,
        config_mgr: ConfigManager,
        parent=None
    ):
        super().__init__(parent)
        self.bt_mgr = bt_mgr
        self.profile_mgr = profile_mgr
        self.config_mgr = config_mgr
        self._is_scanning = False
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # ------------------ هدر بلوتوث و کنترل آداپتور ------------------
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(4)

        lbl_title = QLabel("مدیریت بلوتوث (Bluetooth)")
        lbl_title.setObjectName("pageTitle")
        header_text.addWidget(lbl_title)

        lbl_desc = QLabel("اتصال، قطع اتصال و بررسی وضعیت هدفون‌ها و اسپیکرهای وایرلس")
        lbl_desc.setObjectName("mutedText")
        header_text.addWidget(lbl_desc)

        header_layout.addLayout(header_text)
        header_layout.addStretch()

        # دکمه روشن/خاموش کردن بلوتوث
        self.btn_power = QPushButton("روشن کردن بلوتوث")
        self.btn_power.setIcon(IconHelper.get_icon("bluetooth"))
        self.btn_power.setIconSize(QSize(18, 18))
        self.btn_power.clicked.connect(self._toggle_power)
        header_layout.addWidget(self.btn_power)

        # دکمه اسکن دستگاه‌ها
        self.btn_scan = QPushButton("جستجوی دستگاه جدید")
        self.btn_scan.setIcon(IconHelper.get_icon("refresh"))
        self.btn_scan.setIconSize(QSize(16, 16))
        self.btn_scan.setProperty("primary", "true")
        self.btn_scan.clicked.connect(self._toggle_scan)
        header_layout.addWidget(self.btn_scan)

        main_layout.addLayout(header_layout)

        # اسکرول اریا
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(20)

        # کارت تعویض حالت هدست
        self.headset_mode_card = HeadsetModeCard(self.profile_mgr)
        self.headset_mode_card.mode_changed.connect(lambda mode: self.refresh_data())
        container_layout.addWidget(self.headset_mode_card)

        # فهرست دستگاه‌های جفت‌شده
        lbl_paired = QLabel("دستگاه‌های صوتی جفت‌شده (Paired Devices)")
        lbl_paired.setObjectName("sectionTitle")
        container_layout.addWidget(lbl_paired)

        self.devices_container = QVBoxLayout()
        self.devices_container.setSpacing(10)
        container_layout.addLayout(self.devices_container)

        container_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def refresh_data(self):
        """به‌روزرسانی فهرست دستگاه‌های بلوتوث."""
        powered = self.bt_mgr.is_bluetooth_powered()
        if powered:
            self.btn_power.setText("خاموش کردن بلوتوث")
            self.btn_power.setProperty("danger", "true")
            self.btn_scan.setEnabled(True)
        else:
            self.btn_power.setText("روشن کردن بلوتوث")
            self.btn_power.setProperty("danger", "false")
            self.btn_scan.setEnabled(False)

        self.btn_power.style().unpolish(self.btn_power)
        self.btn_power.style().polish(self.btn_power)

        # بازسازی کارت‌های دستگاه‌ها
        while self.devices_container.count():
            item = self.devices_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not powered:
            self.headset_mode_card.setVisible(False)
            lbl_off = QLabel("بلوتوث سیستم خاموش است. برای مشاهده دستگاه‌ها آن را روشن کنید.")
            lbl_off.setObjectName("mutedText")
            self.devices_container.addWidget(lbl_off)
            return

        devices = self.bt_mgr.get_paired_devices(audio_only=True)
        favorite_id = self.config_mgr.get_favorite_device()

        if not devices:
            self.headset_mode_card.setVisible(False)
            lbl_empty = QLabel("هیچ دستگاه صوتی جفت‌شده‌ای در سیستم یافت نشد.")
            lbl_empty.setObjectName("mutedText")
            self.devices_container.addWidget(lbl_empty)
            return

        # بررسی وجود هدست متصل برای فعال‌سازی کارت سوییچ پروفایل دوگانه
        active_headset_card = None
        for dev in devices:
            if dev.connected:
                card_target = f"bluez_card.{dev.mac_address.replace(':', '_')}"
                if self.profile_mgr.has_headset_modes(card_target):
                    active_headset_card = card_target
                    break

        if active_headset_card:
            self.headset_mode_card.set_target_card(active_headset_card)
        else:
            self.headset_mode_card.setVisible(False)

        for dev in devices:
            card = DeviceCard()
            is_fav = (favorite_id == dev.mac_address)
            card.set_bluetooth_device(dev, is_favorite=is_fav)

            mac_target = dev.mac_address
            card.connect_clicked.connect(lambda target=mac_target: self._connect_device(target))
            card.disconnect_clicked.connect(lambda target=mac_target: self._disconnect_device(target))
            card.favorite_toggled.connect(self._on_favorite_toggled)

            self.devices_container.addWidget(card)

    def _toggle_power(self):
        powered = self.bt_mgr.is_bluetooth_powered()
        self.bt_mgr.set_bluetooth_powered(not powered)
        QTimer.singleShot(500, self.refresh_data)

    def _toggle_scan(self):
        if self._is_scanning:
            self.bt_mgr.stop_discovery()
            self._is_scanning = False
            self.btn_scan.setText("جستجوی دستگاه جدید")
        else:
            self.bt_mgr.start_discovery()
            self._is_scanning = True
            self.btn_scan.setText("در حال جستجو... (توقف)")
            # توقف خودکار پس از ۱۵ ثانیه
            QTimer.singleShot(15000, self._auto_stop_scan)

    def _auto_stop_scan(self):
        if self._is_scanning:
            self.bt_mgr.stop_discovery()
            self._is_scanning = False
            self.btn_scan.setText("جستجوی دستگاه جدید")

    def _connect_device(self, mac: str):
        self.bt_mgr.connect_device(mac)
        QTimer.singleShot(1000, self.refresh_data)

    def _disconnect_device(self, mac: str):
        self.bt_mgr.disconnect_device(mac)
        QTimer.singleShot(500, self.refresh_data)

    def _on_favorite_toggled(self, mac: str, is_fav: bool):
        if is_fav:
            self.config_mgr.set_favorite_device(mac)
        else:
            if self.config_mgr.get_favorite_device() == mac:
                self.config_mgr.set_favorite_device(None)
        self.refresh_data()

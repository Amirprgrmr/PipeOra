"""
صفحه تنظیمات برنامه (SettingsPage)
پیکربندی اتصال خودکار هدفون، Autostart، ادغام با System Tray و ابزارهای تشخیصی
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QCheckBox, QComboBox, QPushButton
)

from app.core.config_manager import ConfigManager
from app.core.system_detector import SystemDetector
from app.core.bluetooth_manager import BluetoothManager
from app.services.autostart_service import AutostartService
from app.ui.components.status_badge import StatusBadge


class SettingsPage(QWidget):
    """صفحه تنظیمات و پیکربندی رفتار نرم‌افزار."""

    def __init__(
        self,
        config_mgr: ConfigManager,
        detector: SystemDetector,
        bt_mgr: BluetoothManager,
        autostart_svc: AutostartService,
        parent=None
    ):
        super().__init__(parent)
        self.config_mgr = config_mgr
        self.detector = detector
        self.bt_mgr = bt_mgr
        self.autostart_svc = autostart_svc
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # عنوان صفحه
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        lbl_title = QLabel("تنظیمات برنامه")
        lbl_title.setObjectName("pageTitle")
        header_layout.addWidget(lbl_title)

        lbl_desc = QLabel("پیکربندی اتصال هوشمند هدفون، اجرای خودکار و رفتارهای دسکتاپ")
        lbl_desc.setObjectName("mutedText")
        header_layout.addWidget(lbl_desc)
        main_layout.addLayout(header_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(20)

        # ------------------ گروه اول: رفتارهای هوشمند صوتی ------------------
        card_smart = QFrame()
        card_smart.setProperty("card", "true")
        smart_layout = QVBoxLayout(card_smart)
        smart_layout.setSpacing(14)

        lbl_smart_title = QLabel("رفتار هوشمند هدفون و صدا")
        lbl_smart_title.setObjectName("sectionTitle")
        smart_layout.addWidget(lbl_smart_title)

        self.chk_auto_connect = QCheckBox("اتصال و سوئیچ خودکار به هدفون محبوب هنگام روشن شدن")
        self.chk_auto_connect.setChecked(self.config_mgr.is_auto_connect_enabled())
        self.chk_auto_connect.toggled.connect(self._on_auto_connect_toggled)
        smart_layout.addWidget(self.chk_auto_connect)

        self.chk_prefer_a2dp = QCheckBox("اولویت قطعی با پروفایل استریوی باکیفیت (A2DP) و ممانعت از HFP")
        self.chk_prefer_a2dp.setChecked(self.config_mgr.is_prefer_a2dp_enabled())
        self.chk_prefer_a2dp.toggled.connect(self._on_prefer_a2dp_toggled)
        smart_layout.addWidget(self.chk_prefer_a2dp)

        fav_row = QHBoxLayout()
        fav_row.setSpacing(12)
        lbl_fav = QLabel("انتخاب دستگاه هدفون محبوب:")
        lbl_fav.setStyleSheet("color: #A6AFBD;")
        fav_row.addWidget(lbl_fav)

        self.combo_favorite = QComboBox()
        self.combo_favorite.currentIndexChanged.connect(self._on_favorite_selected)
        fav_row.addWidget(self.combo_favorite, 1)
        smart_layout.addLayout(fav_row)

        container_layout.addWidget(card_smart)

        # ------------------ گروه دوم: ادغام با سیستم و دسکتاپ ------------------
        card_system = QFrame()
        card_system.setProperty("card", "true")
        system_layout = QVBoxLayout(card_system)
        system_layout.setSpacing(14)

        lbl_sys_title = QLabel("ادغام با دسکتاپ لینوکس")
        lbl_sys_title.setObjectName("sectionTitle")
        system_layout.addWidget(lbl_sys_title)

        self.chk_autostart = QCheckBox("اجرای خودکار برنامه هنگام ورود به سیستم (Autostart)")
        self.chk_autostart.setChecked(self.autostart_svc.is_enabled())
        self.chk_autostart.toggled.connect(self._on_autostart_toggled)
        system_layout.addWidget(self.chk_autostart)

        self.chk_close_to_tray = QCheckBox("کوچک‌سازی به سینی سیستم (System Tray) هنگام بستن پنجره")
        self.chk_close_to_tray.setChecked(self.config_mgr.is_close_to_tray_enabled())
        self.chk_close_to_tray.toggled.connect(self._on_close_to_tray_toggled)
        system_layout.addWidget(self.chk_close_to_tray)

        container_layout.addWidget(card_system)

        # ------------------ گروه سوم: گزارش سلامت و عیب‌یابی ------------------
        card_diag = QFrame()
        card_diag.setProperty("card", "true")
        diag_layout = QVBoxLayout(card_diag)
        diag_layout.setSpacing(12)

        diag_header = QHBoxLayout()
        lbl_diag_title = QLabel("وضعیت زیرساخت صوتی و سرویس‌های سیستم")
        lbl_diag_title.setObjectName("sectionTitle")
        diag_header.addWidget(lbl_diag_title)
        diag_header.addStretch()

        btn_recheck = QPushButton("بررسی مجدد")
        btn_recheck.clicked.connect(self.refresh_data)
        diag_header.addWidget(btn_recheck)
        diag_layout.addLayout(diag_header)

        self.diag_info_layout = QVBoxLayout()
        self.diag_info_layout.setSpacing(8)
        diag_layout.addLayout(self.diag_info_layout)

        container_layout.addWidget(card_diag)

        container_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def refresh_data(self):
        """به‌روزرسانی داده‌های تشخیصی و کمبوباکس دستگاه محبوب."""
        # پر کردن کمبوباکس دستگاه‌های محبوب
        self.combo_favorite.blockSignals(True)
        self.combo_favorite.clear()
        self.combo_favorite.addItem("هیچ‌کدام (غیرفعال)", None)

        paired = self.bt_mgr.get_paired_devices(audio_only=True)
        fav_mac = self.config_mgr.get_favorite_device()
        selected_idx = 0

        for idx, dev in enumerate(paired, start=1):
            self.combo_favorite.addItem(f"{dev.display_name} ({dev.mac_address})", dev.mac_address)
            if fav_mac == dev.mac_address:
                selected_idx = idx

        self.combo_favorite.setCurrentIndex(selected_idx)
        self.combo_favorite.blockSignals(False)

        # به‌روزرسانی کارت سلامت
        while self.diag_info_layout.count():
            item = self.diag_info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        health = self.detector.get_system_health()
        items = [
            ("سرویس PipeWire:", "فعال" if health["pipewire"] else "غیرفعال", "success" if health["pipewire"] else "error"),
            ("مدیریت سشن WirePlumber:", "فعال" if health["wireplumber"] else "غیرفعال", "success" if health["wireplumber"] else "error"),
            ("سرویس pipewire-pulse:", "فعال" if health["pipewire_pulse"] else "غیرفعال", "success" if health["pipewire_pulse"] else "error"),
            ("سرویس بلوتوث BlueZ:", "فعال" if health["bluez"] else "غیرفعال", "success" if health["bluez"] else "error"),
            ("محیط نشست گرافیکی:", f"{health['desktop_session']} ({health['session_type']})", "primary"),
        ]

        for label_text, status_text, variant in items:
            row = QHBoxLayout()
            row.setSpacing(10)
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #F2F4F8;")
            row.addWidget(lbl)
            row.addStretch()
            badge = StatusBadge(status_text, variant=variant)
            row.addWidget(badge)
            self.diag_info_layout.addLayout(row)

    def _on_auto_connect_toggled(self, checked: bool):
        self.config_mgr.set_auto_connect_enabled(checked)

    def _on_prefer_a2dp_toggled(self, checked: bool):
        self.config_mgr.set_prefer_a2dp_enabled(checked)

    def _on_close_to_tray_toggled(self, checked: bool):
        self.config_mgr.set_close_to_tray_enabled(checked)

    def _on_autostart_toggled(self, checked: bool):
        self.config_mgr.set_autostart_enabled(checked)
        if checked:
            self.autostart_svc.enable()
        else:
            self.autostart_svc.disable()

    def _on_favorite_selected(self, index: int):
        data = self.combo_favorite.currentData()
        self.config_mgr.set_favorite_device(data)

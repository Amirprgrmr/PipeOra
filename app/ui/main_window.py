"""
پنجره اصلی نرم‌افزار AM Audio Control
شامل نوار کناری راست‌چین، ناوبری میان صفحات، اتصال رویدادهای زنده و ادغام با System Tray
"""

import logging
from typing import Optional
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon, QCloseEvent
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QLabel, QStackedWidget, QFrame, QMessageBox
)

from app.core.audio_manager import AudioManager
from app.core.bluetooth_manager import BluetoothManager
from app.core.profile_manager import ProfileManager
from app.core.system_detector import SystemDetector
from app.core.config_manager import ConfigManager
from app.services.autostart_service import AutostartService
from app.services.event_worker import EventWorker
from app.ui.tray_icon import AppTrayIcon
from app.ui.styles.icon_helper import IconHelper

from app.ui.dashboard_page import DashboardPage
from app.ui.devices_page import DevicesPage
from app.ui.bluetooth_page import BluetoothPage
from app.ui.settings_page import SettingsPage
from app.ui.about_page import AboutPage
from app.ui.components.status_badge import StatusBadge

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """پنجره اصلی دسکتاپ برنامه AM Audio Control."""

    def __init__(
        self,
        audio_mgr: AudioManager,
        bt_mgr: BluetoothManager,
        profile_mgr: ProfileManager,
        detector: SystemDetector,
        config_mgr: ConfigManager,
        autostart_svc: AutostartService,
        app_icon: QIcon,
        parent=None
    ):
        super().__init__(parent)
        self.audio_mgr = audio_mgr
        self.bt_mgr = bt_mgr
        self.profile_mgr = profile_mgr
        self.detector = detector
        self.config_mgr = config_mgr
        self.autostart_svc = autostart_svc
        self.app_icon = app_icon

        self._nav_buttons = []
        self._is_quitting = False

        # تایمر ضد جهش و تجمیع رویدادهای PipeWire (Event Coalescing Debounce)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(75)
        self._refresh_timer.timeout.connect(self._do_coalesced_refresh)

        self._init_window()
        self._init_ui()
        self._init_tray()
        self._init_event_worker()

        # بارگذاری اولیه داده‌ها
        QTimer.singleShot(100, self.refresh_all_pages)

    def _init_window(self):
        self.setWindowTitle("PipeOra | مدیریت پیشرفته صدای لینوکس")
        self.setWindowIcon(self.app_icon)
        self.resize(1000, 660)
        self.setMinimumSize(860, 560)
        self.setLayoutDirection(Qt.RightToLeft)

    def _init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ------------------ نوار کناری (Sidebar) ------------------
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 20, 14, 20)
        sidebar_layout.setSpacing(10)

        # برند و لوگوی نرم‌افزار
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(12)

        lbl_logo = QLabel()
        lbl_logo.setFixedSize(38, 38)
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setPixmap(IconHelper.get_pixmap("pipeora", 28))
        lbl_logo.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(103, 201, 243, 0.2), stop:1 rgba(37, 99, 235, 0.2));
                border: 1px solid rgba(103, 201, 243, 0.5);
                border-radius: 12px;
                padding: 4px;
            }
        """)
        brand_layout.addWidget(lbl_logo)

        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(2)

        lbl_brand_name = QLabel("PipeOra")
        lbl_brand_name.setStyleSheet("font-size: 15px; font-weight: bold; color: #F2F4F8; letter-spacing: 0.5px;")
        brand_text_layout.addWidget(lbl_brand_name)

        lbl_brand_sub = QLabel("مدیریت هوشمند صدا و بلوتوث")
        lbl_brand_sub.setStyleSheet("font-size: 10px; color: #67C9F3;")
        brand_text_layout.addWidget(lbl_brand_sub)

        brand_layout.addLayout(brand_text_layout)
        brand_layout.addStretch()
        sidebar_layout.addLayout(brand_layout)

        sidebar_layout.addSpacing(16)

        # دکمه‌های ناوبری با آیکون‌های وکتور SVG
        nav_items = [
            ("داشبورد", "nav-home", 0),
            ("دستگاه‌های صوتی", "nav-devices", 1),
            ("مدیریت بلوتوث", "nav-bluetooth", 2),
            ("تنظیمات", "nav-settings", 3),
            ("درباره برنامه", "nav-info", 4),
        ]

        for text, icon_name, idx in nav_items:
            btn = QPushButton(f"  {text}")
            btn.setIcon(IconHelper.get_icon(icon_name))
            btn.setIconSize(QSize(18, 18))
            btn.setProperty("nav", "true")
            btn.setFixedHeight(44)
            btn.clicked.connect(lambda checked=False, i=idx: self.switch_page(i))
            sidebar_layout.addWidget(btn)
            self._nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # بج نشانگر وضعیت زیرساخت در پایین سایدبار
        self.sidebar_status_badge = StatusBadge("PipeWire: فعال", variant="success")
        sidebar_layout.addWidget(self.sidebar_status_badge)

        layout.addWidget(sidebar)

        # ------------------ صفحات اصلی (Stacked Widget) ------------------
        self.stacked_widget = QStackedWidget()

        self.page_dashboard = DashboardPage(
            self.audio_mgr, self.bt_mgr, self.profile_mgr, self.detector, self.config_mgr
        )
        self.page_devices = DevicesPage(
            self.audio_mgr, self.profile_mgr, self.config_mgr
        )
        self.page_bluetooth = BluetoothPage(
            self.bt_mgr, self.profile_mgr, self.config_mgr
        )
        self.page_settings = SettingsPage(
            self.config_mgr, self.detector, self.bt_mgr, self.autostart_svc
        )
        self.page_about = AboutPage()

        self.stacked_widget.addWidget(self.page_dashboard)
        self.stacked_widget.addWidget(self.page_devices)
        self.stacked_widget.addWidget(self.page_bluetooth)
        self.stacked_widget.addWidget(self.page_settings)
        self.stacked_widget.addWidget(self.page_about)

        layout.addWidget(self.stacked_widget, 1)

        # تنظیم صفحه نخست
        self.switch_page(0)

    def _init_tray(self):
        """راه‌اندازی سینی سیستم (System Tray)."""
        self.tray_icon = AppTrayIcon(self.audio_mgr, self.app_icon, self)
        self.tray_icon.toggle_window_requested.connect(self.toggle_window)
        self.tray_icon.show_window_requested.connect(self.show_and_activate)
        self.tray_icon.quit_requested.connect(self.quit_application)
        self.tray_icon.show()

    def _init_event_worker(self):
        """راه‌اندازی ورکر پس‌زمینه شنود زنده رویدادهای PipeWire و بلوتوث."""
        self.event_worker = EventWorker(self)
        self.event_worker.sink_changed.connect(self._on_sink_event)
        self.event_worker.server_changed.connect(self._on_server_event)
        self.event_worker.stream_changed.connect(self._on_stream_event)
        self.event_worker.card_changed.connect(self._on_card_event)
        self.event_worker.bluetooth_changed.connect(self._on_bluetooth_event)
        self.event_worker.start()

    def switch_page(self, index: int):
        """تغییر صفحه فعال در StackedWidget و به‌روزرسانی هایلایت سایدبار."""
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            is_active = (i == index)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        # ریفرش دیتای صفحه مورد نظر
        if index == 0:
            self.page_dashboard.refresh_data()
        elif index == 1:
            self.page_devices.refresh_data()
        elif index == 2:
            self.page_bluetooth.refresh_data()
        elif index == 3:
            self.page_settings.refresh_data()

    def refresh_all_pages(self):
        """به‌روزرسانی جامع تمام صفحات و منوی سینی سیستم."""
        default_sink = self.audio_mgr.get_default_sink()
        self.tray_icon.update_status(default_sink)

        pw_ok = self.detector.check_pipewire()
        self.sidebar_status_badge.set_variant(
            "success" if pw_ok else "error",
            "PipeWire: فعال" if pw_ok else "PipeWire: قطع"
        )

        curr_page = self.stacked_widget.currentIndex()
        if curr_page == 0:
            self.page_dashboard.refresh_data()
        elif curr_page == 1:
            self.page_devices.refresh_data()
        elif curr_page == 2:
            self.page_bluetooth.refresh_data()
        elif curr_page == 3:
            self.page_settings.refresh_data()

    def _on_sink_event(self, event_text: str):
        self._refresh_timer.start()

    def _on_server_event(self):
        self._refresh_timer.start()

    def _on_card_event(self, event_text: str):
        self._refresh_timer.start()

    def _do_coalesced_refresh(self):
        """اجرای متمرکز و بهینه به‌روزرسانی رابط کاربری بدون بار پردازشی تکراری."""
        default_sink = self.audio_mgr.get_default_sink()
        if hasattr(self, "tray_icon"):
            self.tray_icon.update_status(default_sink)
        self.page_dashboard.refresh_data()
        if self.stacked_widget.currentIndex() == 1:
            self.page_devices.refresh_data()

    def _on_stream_event(self):
        if self.stacked_widget.currentIndex() == 1:
            self.page_devices._update_apps()

    def _on_bluetooth_event(self):
        """رسیدگی به تغییرات وضعیت بلوتوث و اتصال خودکار به هدفون محبوب."""
        # بررسی اتصال خودکار به هدفون محبوب
        if self.config_mgr.is_auto_connect_enabled():
            fav_mac = self.config_mgr.get_favorite_device()
            if fav_mac:
                self._check_and_enforce_favorite(fav_mac)

        if self.stacked_widget.currentIndex() in (0, 2):
            self.page_dashboard.refresh_data()
            if self.stacked_widget.currentIndex() == 2:
                self.page_bluetooth.refresh_data()

    def _check_and_enforce_favorite(self, fav_mac: str):
        """اگر هدفون محبوب متصل شد، آن را خودکار به خروجی پیش‌فرض و A2DP تبدیل کن."""
        sinks = self.audio_mgr.get_output_sinks()
        for s in sinks:
            if s.is_bluetooth:
                props = s.properties
                dev_mac = props.get("device.bus_path", "") or props.get("device.string", "") or props.get("api.bluez5.address", "")
                if fav_mac.lower().replace(":", "_") in s.name.lower() or fav_mac.lower() in str(dev_mac).lower():
                    if not s.is_default:
                        logger.info("سوئیچ خودکار خروجی پیش‌فرض به هدفون محبوب: %s", s.name)
                        self.audio_mgr.set_default_sink(s.name)
                    if self.config_mgr.is_prefer_a2dp_enabled() and s.card_id:
                        self.profile_mgr.switch_to_a2dp_if_possible(str(s.card_id))
                    break

    def toggle_window(self):
        """پنهان‌سازی یا نمایش پنجره از سینی سیستم."""
        if self.isVisible():
            self.hide()
        else:
            self.show_and_activate()

    def show_and_activate(self):
        """نمایش پنجره و آوردن آن به فوکوس کاربر."""
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event: QCloseEvent):
        """مدیریت رویداد بستن پنجره با قابلیت کوچک‌سازی به System Tray."""
        if self._is_quitting:
            event.accept()
            return

        if self.config_mgr.is_close_to_tray_enabled():
            event.ignore()
            self.hide()
            if self.tray_icon.isVisible():
                self.tray_icon.showMessage(
                    "PipeOra",
                    "برنامه در سینی سیستم به فعالیت خود ادامه می‌دهد.",
                    QIcon(self.app_icon),
                    2000
                )
        else:
            self.quit_application()

    def quit_application(self):
        """خروج قطعی و آزادکردن تمام منابع و سرویس‌ها."""
        self._is_quitting = True
        if hasattr(self, "event_worker"):
            self.event_worker.stop()
        if hasattr(self, "tray_icon"):
            self.tray_icon.hide()
        self.close()

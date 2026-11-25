"""
نقطه ورود اصلی نرم‌افزار PipeOra
مدیریت Single Instance، بارگذاری استایل‌شیت Graphite Dark، فونت‌ها و سینی سیستم
"""

import argparse
import logging
import os
import signal
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtGui import QIcon, QFontDatabase, QFont
from PySide6.QtWidgets import QApplication

from app.core.audio_manager import AudioManager
from app.core.bluetooth_manager import BluetoothManager
from app.core.profile_manager import ProfileManager
from app.core.system_detector import SystemDetector
from app.core.config_manager import ConfigManager
from app.core.paths import get_project_root, get_resource_path
from app.services.autostart_service import AutostartService
from app.ui.main_window import MainWindow

# پیکربندی سیستم لاگ
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("pipeora")

SOCKET_NAME = f"pipeora_single_instance_{os.getuid() if hasattr(os, 'getuid') else 'socket'}"


class SingleInstanceApp:
    """جلوگیری از اجرای همزمان چند نسخه از برنامه از طریق QLocalServer."""

    def __init__(self, main_window: MainWindow):
        self.main_window = main_window
        self.server = QLocalServer()
        self.server.newConnection.connect(self._on_new_connection)

        # پاک‌سازی سوکت قبلی در صورت وجود
        QLocalServer.removeServer(SOCKET_NAME)
        if not self.server.listen(SOCKET_NAME):
            logger.warning("امکان ایجاد سرور سوکت تک‌نسخه وجود نداشت.")

    def _on_new_connection(self):
        socket = self.server.nextPendingConnection()
        if socket:
            socket.readyRead.connect(lambda: self._handle_incoming_message(socket))

    def _handle_incoming_message(self, socket):
        msg = socket.readAll().data().decode("utf-8")
        if "show" in msg:
            logger.info("درخواست نمایش پنجره از نسخه دیگر دریافت شد.")
            self.main_window.show_and_activate()
        socket.disconnectFromServer()


def check_existing_instance() -> bool:
    """بررسی اینکه آیا نسخه دیگری از برنامه در حال اجراست یا خیر."""
    socket = QLocalSocket()
    socket.connectToServer(SOCKET_NAME)
    if socket.waitForConnected(300):
        # نسخه دیگری فعال است، پیام فعال‌سازی پنجره ارسال می‌کنیم
        socket.write(b"show\n")
        socket.waitForBytesWritten(300)
        socket.disconnectFromServer()
        return True
    return False


def load_application_font():
    """بارگذاری و اولویت‌بندی فونت‌های فارسی سیستم."""
    font_candidates = ["Vazirmatn", "Noto Sans Arabic", "Noto Sans Arabic UI", "Vazir Code"]
    available_families = QFontDatabase.families()

    chosen_family = "sans-serif"
    for cand in font_candidates:
        if cand in available_families:
            chosen_family = cand
            break

    app_font = QFont(chosen_family, 10)
    QApplication.setFont(app_font)
    logger.info("فونت پیش‌فرض برنامه: %s", chosen_family)


def load_stylesheet() -> str:
    """بارگذاری استایل‌شیت یکپارچه Graphite Dark همراه با تزریق مسیر واقعی آیکون‌ها."""
    qss_path = get_resource_path("ui", "styles", "style.qss")
    icons_dir = get_resource_path("resources", "icons").as_posix()
    if qss_path.exists():
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                return f.read().replace("{{ICONS_DIR}}", icons_dir)
        except Exception as e:
            logger.error("خطا در بارگذاری استایل‌شیت: %s", e)
    return ""


def main():
    """تابع اصلی راه‌اندازی و اجرای برنامه دسکتاپ."""
    # آرگومان‌های خط فرمان
    parser = argparse.ArgumentParser(description="PipeOra - مدیریت پیشرفته و هوشمند صدای لینوکس")
    parser.add_argument("--minimized", action="store_true", help="اجرای مستقیم در سینی سیستم (بدون نمایش اولیه پنجره)")
    parser.add_argument("--version", action="store_true", help="نمایش نسخه برنامه")
    args = parser.parse_args()

    if args.version:
        from app import __version__
        if sys.stdout is not None:
            print(f"PipeOra v{__version__}")
        sys.exit(0)

    # بررسی اجرای نسخه تکراری
    if check_existing_instance():
        logger.info("نسخه دیگری از برنامه در حال اجراست. پنجره آن فعال گردید.")
        sys.exit(0)

    # تنظیمات Qt
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    app.setApplicationName("PipeOra")
    app.setApplicationDisplayName("PipeOra")
    app.setOrganizationName("Amirali")
    app.setDesktopFileName("pipeora")

    # قانون اساسی: رابط کاملاً راست‌چین فارسی
    app.setLayoutDirection(Qt.RightToLeft)

    # بارگذاری فونت و استایل
    load_application_font()
    qss = load_stylesheet()
    if qss:
        app.setStyleSheet(qss)

    # آیکون برنامه
    icons_dir = get_resource_path("resources", "icons")
    icon_candidates = [
        icons_dir / "pipeora.svg",
        get_project_root() / "packaging" / "pipeora.svg",
        icons_dir / "app_icon.svg"
    ]
    app_icon = QIcon()
    for cand in icon_candidates:
        if cand.exists():
            app_icon = QIcon(str(cand))
            break
    app.setWindowIcon(app_icon)

    # ایجاد سرویس‌ها و منیجرها
    detector = SystemDetector()
    audio_mgr = AudioManager()
    bt_mgr = BluetoothManager()
    profile_mgr = ProfileManager()
    config_mgr = ConfigManager()
    autostart_svc = AutostartService()

    # ایجاد پنجره اصلی
    main_window = MainWindow(
        audio_mgr=audio_mgr,
        bt_mgr=bt_mgr,
        profile_mgr=profile_mgr,
        detector=detector,
        config_mgr=config_mgr,
        autostart_svc=autostart_svc,
        app_icon=app_icon
    )

    # اتصال محافظت از Single Instance
    single_instance = SingleInstanceApp(main_window)
    app.aboutToQuit.connect(main_window.quit_application)

    # هندل کردن سیگنال‌های سیستمی (Ctrl+C در ترمینال)
    signal.signal(signal.SIGINT, lambda sig, frame: main_window.quit_application())

    # نمایش پنجره بر اساس آرگومان
    if not args.minimized and not config_mgr.get("start_minimized", False):
        main_window.show()
    else:
        logger.info("برنامه در حالت پس‌زمینه (سینی سیستم) راه‌اندازی شد.")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

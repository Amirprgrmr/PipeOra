import os
import pytest
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

os.environ["QT_QPA_PLATFORM"] = "offscreen"

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_main_window_creation(qapp, tmp_path):
    from app.core.audio_manager import AudioManager
    from app.core.bluetooth_manager import BluetoothManager
    from app.core.profile_manager import ProfileManager
    from app.core.system_detector import SystemDetector
    from app.core.config_manager import ConfigManager
    from app.services.autostart_service import AutostartService
    from app.ui.main_window import MainWindow

    audio_mgr = AudioManager()
    bt_mgr = BluetoothManager()
    profile_mgr = ProfileManager()
    detector = SystemDetector()
    config_mgr = ConfigManager(config_path=str(tmp_path / "cfg.json"))
    autostart_svc = AutostartService(autostart_dir=str(tmp_path / "autostart"))

    win = MainWindow(
        audio_mgr=audio_mgr,
        bt_mgr=bt_mgr,
        profile_mgr=profile_mgr,
        detector=detector,
        config_mgr=config_mgr,
        autostart_svc=autostart_svc,
        app_icon=QIcon()
    )
    assert win is not None
    assert win.windowTitle() == "AM Audio Control | مدیریت صدای AM"

    # Test page switching
    win.switch_page(1)
    assert win.stacked_widget.currentIndex() == 1
    win.switch_page(2)
    assert win.stacked_widget.currentIndex() == 2
    win.switch_page(0)
    assert win.stacked_widget.currentIndex() == 0

    # Clean shutdown
    win.quit_application()

import os
import pytest
from PySide6.QtWidgets import QApplication

os.environ["QT_QPA_PLATFORM"] = "offscreen"

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_pages_instantiation(qapp, tmp_path):
    from app.core.audio_manager import AudioManager
    from app.core.bluetooth_manager import BluetoothManager
    from app.core.profile_manager import ProfileManager
    from app.core.system_detector import SystemDetector
    from app.core.config_manager import ConfigManager
    from app.services.autostart_service import AutostartService

    from app.ui.dashboard_page import DashboardPage
    from app.ui.devices_page import DevicesPage
    from app.ui.bluetooth_page import BluetoothPage
    from app.ui.settings_page import SettingsPage
    from app.ui.about_page import AboutPage

    audio_mgr = AudioManager()
    bt_mgr = BluetoothManager()
    profile_mgr = ProfileManager()
    detector = SystemDetector()
    config_mgr = ConfigManager(config_path=str(tmp_path / "cfg.json"))
    autostart_svc = AutostartService(autostart_dir=str(tmp_path / "autostart"))

    # Test DashboardPage
    dash = DashboardPage(audio_mgr, bt_mgr, profile_mgr, detector, config_mgr)
    assert dash is not None

    # Test DevicesPage
    devs = DevicesPage(audio_mgr, profile_mgr, config_mgr)
    assert devs is not None

    # Test BluetoothPage
    bt_page = BluetoothPage(bt_mgr, config_mgr)
    assert bt_page is not None

    # Test SettingsPage
    settings = SettingsPage(config_mgr, detector, bt_mgr, autostart_svc)
    assert settings is not None

    # Test AboutPage
    about = AboutPage()
    assert about is not None

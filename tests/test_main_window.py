import os
from PySide6.QtGui import QIcon

os.environ["QT_QPA_PLATFORM"] = "offscreen"

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
    assert win.windowTitle() == "PipeOra | مدیریت پیشرفته صدای لینوکس"

    # Test page switching
    win.switch_page(1)
    assert win.stacked_widget.currentIndex() == 1
    win.switch_page(2)
    assert win.stacked_widget.currentIndex() == 2
    win.switch_page(0)
    assert win.stacked_widget.currentIndex() == 0

    win.quit_application()
    win.deleteLater()
    qapp.processEvents()


def test_favorite_enforcement_does_not_override_manual_profile(qapp, tmp_path):
    from unittest.mock import MagicMock
    from app.models.audio import SinkDevice
    from app.core.config_manager import ConfigManager
    from app.core.system_detector import SystemDetector
    from app.services.autostart_service import AutostartService
    from app.ui.main_window import MainWindow

    mock_audio = MagicMock()
    bt_sink = SinkDevice(
        id=200,
        name="bluez_output.84_AC_60_C9_02_74.1",
        description="QCY T13 ANC2",
        mute=False,
        volume_percent=75,
        is_default=True,
        is_bluetooth=True,
        card_id=86,
        card_name="bluez_card.84_AC_60_C9_02_74",
    )
    mock_audio.get_output_sinks.return_value = [bt_sink]
    mock_audio.get_default_sink.return_value = bt_sink
    mock_audio.get_sink_inputs.return_value = []

    mock_bt = MagicMock()
    mock_bt.is_bluetooth_powered.return_value = True
    mock_bt.get_paired_devices.return_value = []

    mock_prof = MagicMock()
    mock_prof.get_headset_status.return_value = (True, "hfp")
    mock_prof.get_wireplumber_autoswitch.return_value = False
    mock_prof.get_card_profiles.return_value = []

    cfg = ConfigManager(config_path=str(tmp_path / "cfg.json"))
    cfg.set_auto_connect_enabled(True)
    cfg.set_prefer_a2dp_enabled(True)
    cfg.set_favorite_device("84:AC:60:C9:02:74")

    win = MainWindow(
        audio_mgr=mock_audio,
        bt_mgr=mock_bt,
        profile_mgr=mock_prof,
        detector=SystemDetector(),
        config_mgr=cfg,
        autostart_svc=AutostartService(autostart_dir=str(tmp_path / "autostart")),
        app_icon=QIcon()
    )

    # First tick: enforces A2DP once upon initial connection
    win._check_and_enforce_favorite("84:AC:60:C9:02:74")
    assert mock_prof.switch_to_a2dp_if_possible.call_count == 1

    # Second tick (e.g. after user manually chose HFP): MUST NOT override!
    win._check_and_enforce_favorite("84:AC:60:C9:02:74")
    assert mock_prof.switch_to_a2dp_if_possible.call_count == 1

    # Simulate disconnect then reconnect: should re-arm once
    mock_audio.get_output_sinks.return_value = []
    win._check_and_enforce_favorite("84:AC:60:C9:02:74")
    mock_audio.get_output_sinks.return_value = [bt_sink]
    win._check_and_enforce_favorite("84:AC:60:C9:02:74")
    assert mock_prof.switch_to_a2dp_if_possible.call_count == 2

    win.quit_application()
    win.deleteLater()
    qapp.processEvents()

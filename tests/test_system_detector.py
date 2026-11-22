import pytest
from unittest.mock import patch, MagicMock
from app.core.system_detector import SystemDetector

def test_system_detector_tools_exist():
    detector = SystemDetector()
    tools = detector.check_tools()
    assert "wpctl" in tools
    assert "pactl" in tools
    assert "bluetoothctl" in tools

def test_system_detector_pipewire_active():
    detector = SystemDetector()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="active\n")
        assert detector.check_pipewire() is True
        mock_run.assert_called_with(
            ["systemctl", "--user", "is-active", "pipewire"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2.0
        )

def test_system_detector_service_inactive():
    detector = SystemDetector()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=3, stdout="inactive\n")
        assert detector.check_wireplumber() is False

def test_system_detector_bluez_system_service():
    detector = SystemDetector()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="active\n")
        assert detector.check_bluez() is True
        mock_run.assert_called_with(
            ["systemctl", "is-active", "bluetooth"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2.0
        )

def test_system_detector_get_system_health():
    detector = SystemDetector()
    with patch.object(detector, "check_pipewire", return_value=True), \
         patch.object(detector, "check_wireplumber", return_value=True), \
         patch.object(detector, "check_bluez", return_value=True), \
         patch.object(detector, "check_pipewire_pulse", return_value=True):
        health = detector.get_system_health()
        assert health["pipewire"] is True
        assert health["wireplumber"] is True
        assert health["bluez"] is True
        assert health["pipewire_pulse"] is True
        assert health["is_audio_ready"] is True

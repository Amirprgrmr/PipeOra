import pytest
from unittest.mock import patch, MagicMock
from app.core.bluetooth_manager import BluetoothManager
from app.models.bluetooth import BTDevice

SAMPLE_DBUS_OBJECTS = {
    "/org/bluez/hci0": {
        "org.bluez.Adapter1": {
            "Powered": True,
            "Discovering": False,
            "Address": "A0:B1:C2:D3:E4:F5"
        }
    },
    "/org/bluez/hci0/dev_84_AC_60_C9_02_74": {
        "org.bluez.Device1": {
            "Address": "84:AC:60:C9:02:74",
            "Name": "QCY T13 ANC2",
            "Alias": "QCY T13 ANC2",
            "Icon": "audio-headset",
            "Paired": True,
            "Connected": False,
            "Trusted": True,
            "UUIDs": [
                "0000110b-0000-1000-8000-00805f9b34fb", # Audio Sink
                "0000110c-0000-1000-8000-00805f9b34fb"  # AVRCP
            ]
        },
        "org.bluez.Battery1": {
            "Percentage": 90
        }
    }
}

def test_get_paired_devices_dbus():
    mgr = BluetoothManager()
    with patch.object(mgr, "_get_dbus_objects", return_value=SAMPLE_DBUS_OBJECTS):
        devices = mgr.get_paired_devices()
        assert len(devices) == 1
        dev = devices[0]
        assert dev.mac_address == "84:AC:60:C9:02:74"
        assert dev.name == "QCY T13 ANC2"
        assert dev.is_audio_device is True
        assert dev.is_headset is True
        assert dev.battery_percentage == 90

def test_connect_device():
    mgr = BluetoothManager()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="Connection successful\n")
        res = mgr.connect_device("84:AC:60:C9:02:74")
        assert res is True
        mock_run.assert_called_with(
            ["bluetoothctl", "connect", "84:AC:60:C9:02:74"],
            capture_output=True,
            text=True,
            check=False,
            timeout=8.0
        )

def test_disconnect_device():
    mgr = BluetoothManager()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="Successful disconnected\n")
        res = mgr.disconnect_device("84:AC:60:C9:02:74")
        assert res is True
        mock_run.assert_called_with(
            ["bluetoothctl", "disconnect", "84:AC:60:C9:02:74"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5.0
        )

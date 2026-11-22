import json
import pytest
from unittest.mock import patch, MagicMock
from app.core.audio_manager import AudioManager

SAMPLE_SINKS_JSON = json.dumps([
    {
        "index": 54,
        "name": "alsa_output.pci-0000_00_1f.3.analog-stereo",
        "description": "Built-in Audio Analog Stereo",
        "mute": False,
        "volume": {
            "front-left": {"value_percent": "70%"},
            "front-right": {"value_percent": "70%"}
        },
        "active_port": "analog-output-speaker",
        "properties": {
            "device.api": "alsa",
            "device.id": "44"
        }
    },
    {
        "index": 105,
        "name": "bluez_output.84_AC_60_C9_02_74.1",
        "description": "QCY T13 ANC2",
        "mute": False,
        "volume": {
            "front-left": {"value_percent": "85%"},
            "front-right": {"value_percent": "85%"}
        },
        "active_port": None,
        "properties": {
            "device.api": "bluez5",
            "device.id": "110"
        }
    }
])

SAMPLE_SERVER_INFO_JSON = json.dumps({
    "default_sink_name": "alsa_output.pci-0000_00_1f.3.analog-stereo"
})

def test_get_output_sinks_parsing():
    manager = AudioManager()
    with patch("subprocess.run") as mock_run:
        # First call is for server info, second is for sinks
        def side_effect(cmd, **kwargs):
            if "info" in cmd:
                return MagicMock(returncode=0, stdout=SAMPLE_SERVER_INFO_JSON)
            elif "sinks" in cmd:
                return MagicMock(returncode=0, stdout=SAMPLE_SINKS_JSON)
            return MagicMock(returncode=1, stdout="")

        mock_run.side_effect = side_effect

        sinks = manager.get_output_sinks()
        assert len(sinks) == 2
        
        # Verify first sink
        sink0 = sinks[0]
        assert sink0.id == 54
        assert sink0.volume_percent == 70
        assert sink0.is_default is True
        assert sink0.is_bluetooth is False
        
        # Verify bluetooth sink
        sink1 = sinks[1]
        assert sink1.id == 105
        assert sink1.volume_percent == 85
        assert sink1.is_default is False
        assert sink1.is_bluetooth is True
        assert "QCY T13 ANC2" in sink1.description

def test_set_volume_clamping():
    manager = AudioManager()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        # Test volume above 100 is clamped to 100
        res = manager.set_volume("54", 125)
        assert res is True
        mock_run.assert_called_with(
            ["pactl", "set-sink-volume", "54", "100%"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2.0
        )

        # Test negative volume is clamped to 0
        res = manager.set_volume("54", -15)
        assert res is True
        mock_run.assert_called_with(
            ["pactl", "set-sink-volume", "54", "0%"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2.0
        )

def test_set_mute():
    manager = AudioManager()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        res = manager.set_mute("54", True)
        assert res is True
        mock_run.assert_called_with(
            ["pactl", "set-sink-mute", "54", "1"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2.0
        )

def test_set_default_sink():
    manager = AudioManager()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        res = manager.set_default_sink("alsa_output.pci-0000_00_1f.3.analog-stereo")
        assert res is True
        mock_run.assert_called_with(
            ["pactl", "set-default-sink", "alsa_output.pci-0000_00_1f.3.analog-stereo"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2.0
        )


SAMPLE_SOURCES_JSON = json.dumps([
    {
        "index": 54,
        "name": "alsa_output.pci-0000_00_1f.3.analog-stereo.monitor",
        "description": "Monitor of Built-in Audio Analog Stereo"
    },
    {
        "index": 55,
        "name": "alsa_input.pci-0000_00_1f.3.analog-stereo",
        "description": "Built-in Audio Analog Stereo"
    },
    {
        "index": 2639,
        "name": "bluez_input.84:AC:60:C9:02:74",
        "description": "QCY T13 ANC2"
    }
])

SAMPLE_SOURCE_OUTPUTS_JSON = json.dumps([
    {
        "index": 7669,
        "source": 2639,
        "properties": {
            "application.name": "Antigravity"
        }
    }
])


def test_fallback_source_detection_and_stream_migration():
    manager = AudioManager()
    with patch("subprocess.run") as mock_run:
        def side_effect(cmd, **kwargs):
            if "sources" in cmd:
                return MagicMock(returncode=0, stdout=SAMPLE_SOURCES_JSON)
            elif "source-outputs" in cmd:
                return MagicMock(returncode=0, stdout=SAMPLE_SOURCE_OUTPUTS_JSON)
            return MagicMock(returncode=0, stdout="")

        mock_run.side_effect = side_effect

        fallback = manager.get_hardware_fallback_source()
        assert fallback == "alsa_input.pci-0000_00_1f.3.analog-stereo"

        # Test set default source
        res_src = manager.set_default_source(fallback)
        assert res_src is True

        # Test move recording streams
        moved_count = manager.move_recording_streams(fallback)
        assert moved_count == 1


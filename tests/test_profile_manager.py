import json
import pytest
from unittest.mock import patch, MagicMock
from app.core.profile_manager import ProfileManager

SAMPLE_CARDS_JSON = json.dumps([
    {
        "index": 110,
        "name": "bluez_card.84_AC_60_C9_02_74",
        "active_profile": "a2dp-sink",
        "profiles": [
            {
                "name": "off",
                "description": "Off",
                "available": "yes",
                "priority": 0
            },
            {
                "name": "a2dp-sink",
                "description": "High Fidelity Playback (A2DP Sink)",
                "available": "yes",
                "priority": 40
            },
            {
                "name": "headset-head-unit",
                "description": "Headset Head Unit (HSP/HFP)",
                "available": "yes",
                "priority": 20
            }
        ]
    }
])

def test_get_card_profiles_and_persian_translation():
    mgr = ProfileManager()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=SAMPLE_CARDS_JSON)
        profiles = mgr.get_card_profiles("110")
        assert len(profiles) == 3

        # Check A2DP profile
        a2dp = [p for p in profiles if p.is_a2dp][0]
        assert a2dp.name == "a2dp-sink"
        assert a2dp.is_active is True
        assert "A2DP" in a2dp.persian_name
        assert "استریو" in a2dp.persian_name

        # Check HFP profile
        hfp = [p for p in profiles if p.is_hfp][0]
        assert hfp.name == "headset-head-unit"
        assert hfp.is_active is False

def test_set_card_profile():
    mgr = ProfileManager()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        res = mgr.set_card_profile("110", "a2dp-sink")
        assert res is True
        mock_run.assert_called_with(
            ["pactl", "set-card-profile", "110", "a2dp-sink"],
            capture_output=True,
            text=True,
            check=False,
            timeout=3.0
        )


def test_headset_mode_switching():
    mock_audio_mgr = MagicMock()
    mock_audio_mgr.get_hardware_fallback_source.return_value = "alsa_input.pci-0000_00_1f.3.analog-stereo"
    mock_audio_mgr.set_default_source.return_value = True
    mock_audio_mgr.move_recording_streams.return_value = 1

    mgr = ProfileManager(audio_mgr=mock_audio_mgr)
    with patch("subprocess.run") as mock_run:
        def side_effect(cmd, **kwargs):
            if "list" in cmd and "cards" in cmd:
                return MagicMock(returncode=0, stdout=SAMPLE_CARDS_JSON)
            elif "list" in cmd and "sources" in cmd:
                sample_sources = json.dumps([
                    {"index": 55, "name": "alsa_input.pci-0000_00_1f.3.analog-stereo"},
                    {"index": 2639, "name": "bluez_input.84:AC:60:C9:02:74"}
                ])
                return MagicMock(returncode=0, stdout=sample_sources)
            return MagicMock(returncode=0, stdout="")

        mock_run.side_effect = side_effect

        # Currently active is a2dp-sink in SAMPLE_CARDS_JSON
        mode = mgr.get_headset_mode("110")
        assert mode == "a2dp"
        assert mgr.has_headset_modes("110") is True

        # Switch to hfp: should disable autoswitch, set profile, and update default source
        res_hfp = mgr.set_headset_mode("110", "hfp", disable_autoswitch=True)
        assert res_hfp is True
        mock_audio_mgr.set_default_source.assert_called_with("bluez_input.84:AC:60:C9:02:74")
        mock_audio_mgr.move_recording_streams.assert_called_with("bluez_input.84:AC:60:C9:02:74")

        # Verify wpctl settings was invoked to disable autoswitch
        wp_calls = [c.args[0] for c in mock_run.call_args_list if c.args and "wpctl" in c.args[0]]
        assert any("bluetooth.autoswitch-to-headset-profile" in c and "false" in c for c in wp_calls)

        # Switch to a2dp: should set default source to fallback mic first, move streams, and set a2dp
        res_a2dp = mgr.set_headset_mode("110", "a2dp", disable_autoswitch=True)
        assert res_a2dp is True
        mock_audio_mgr.set_default_source.assert_called_with("alsa_input.pci-0000_00_1f.3.analog-stereo")
        mock_audio_mgr.move_recording_streams.assert_called_with("alsa_input.pci-0000_00_1f.3.analog-stereo")


def test_wireplumber_autoswitch_get_and_set():
    mgr = ProfileManager()
    sample_wp_out = """
- Id: bluetooth.autoswitch-to-headset-profile
  Name: Auto-switch to headset profile
  Type: Boolean
  Default: true
  Value: false (Saved: false)
"""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout=sample_wp_out)
        assert mgr.get_wireplumber_autoswitch() is False

        mock_run.return_value = MagicMock(returncode=0, stdout="")
        assert mgr.set_wireplumber_autoswitch(True) is True



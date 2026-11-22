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

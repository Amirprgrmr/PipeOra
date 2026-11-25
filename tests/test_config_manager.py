import os
import json
import pytest
from app.core.config_manager import ConfigManager

def test_config_manager_default_values(tmp_path):
    config_file = str(tmp_path / "config.json")
    cfg = ConfigManager(config_path=config_file)
    
    assert cfg.get("auto_connect_favorite") is True
    assert cfg.get("prefer_a2dp") is True
    assert cfg.get("close_to_tray") is True
    assert cfg.get("favorite_device") is None

def test_config_manager_set_and_save(tmp_path):
    config_file = str(tmp_path / "config.json")
    cfg = ConfigManager(config_path=config_file)
    
    cfg.set_favorite_device("84:AC:60:C9:02:74")
    cfg.set_autostart_enabled(True)
    
    # Reload from disk
    cfg2 = ConfigManager(config_path=config_file)
    assert cfg2.get_favorite_device() == "84:AC:60:C9:02:74"
    assert cfg2.is_autostart_enabled() is True

def test_config_manager_corrupted_json_recovery(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("{invalid json", encoding="utf-8")
    
    cfg = ConfigManager(config_path=str(config_file))
    # Should safely recover with defaults and not crash
    assert cfg.get("prefer_a2dp") is True


def test_config_manager_migration(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    old_dir = tmp_path / "am-audio-control"
    old_dir.mkdir(parents=True)
    old_file = old_dir / "config.json"
    old_file.write_text(json.dumps({"favorite_device": "11:22:33:44:55:66", "prefer_a2dp": False}), encoding="utf-8")

    cfg = ConfigManager()
    assert cfg.config_path == tmp_path / "pipeora" / "config.json"
    assert cfg.get("favorite_device") == "11:22:33:44:55:66"
    assert cfg.get("prefer_a2dp") is False
    assert (tmp_path / "pipeora" / "config.json").exists()


def test_headset_auto_switch_config(tmp_path):
    cfg = ConfigManager(config_path=str(tmp_path / "cfg.json"))
    assert cfg.is_headset_auto_switch_enabled() is False
    cfg.set_headset_auto_switch_enabled(True)
    cfg2 = ConfigManager(config_path=str(tmp_path / "cfg.json"))
    assert cfg2.is_headset_auto_switch_enabled() is True


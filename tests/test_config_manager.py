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

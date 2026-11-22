import os
from pathlib import Path
from app.services.autostart_service import AutostartService

def test_autostart_enable_and_disable(tmp_path):
    autostart_dir = tmp_path / "autostart"
    service = AutostartService(autostart_dir=str(autostart_dir))
    
    assert service.is_enabled() is False
    
    # Enable
    res = service.enable(exec_path="/usr/bin/am-audio-control")
    assert res is True
    assert service.is_enabled() is True
    
    desktop_file = autostart_dir / "am-audio-control.desktop"
    assert desktop_file.exists()
    content = desktop_file.read_text(encoding="utf-8")
    assert "Exec=/usr/bin/am-audio-control" in content
    assert "Name=AM Audio Control" in content
    
    # Disable
    res_dis = service.disable()
    assert res_dis is True
    assert service.is_enabled() is False
    assert not desktop_file.exists()

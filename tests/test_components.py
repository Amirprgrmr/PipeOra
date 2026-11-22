import os
import pytest
from PySide6.QtWidgets import QApplication

# اطمینان از اجرای تست‌ها در محیط Offscreen Wayland/CI
os.environ["QT_QPA_PLATFORM"] = "offscreen"

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_status_badge(qapp):
    from app.ui.components.status_badge import StatusBadge
    badge = StatusBadge("تست", variant="success")
    assert badge.text() == "تست"
    badge.set_variant("warning", "هشدار")
    assert badge.text() == "هشدار"

def test_volume_slider_feedback_loop_prevention(qapp):
    from app.ui.components.volume_slider import VolumeSlider
    slider = VolumeSlider()
    
    received_volumes = []
    slider.volume_changed.connect(lambda v: received_volumes.append(v))
    
    # تنظیم از منبع خارجی با set_volume نباید سیگنال volume_changed بفرستد
    slider.set_volume(85)
    assert slider.slider.value() == 85
    assert len(received_volumes) == 0  # هیچ سیگنال تکراری ایجاد نشد
    
    # شبیه‌سازی تغییر توسط کاربر
    slider.slider.setValue(90)
    assert 90 in received_volumes

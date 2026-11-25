import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

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


def test_headset_mode_card(qapp):
    from app.core.profile_manager import ProfileManager
    from app.ui.components.headset_mode_card import HeadsetModeCard

    mgr = ProfileManager()
    card = HeadsetModeCard(mgr)
    assert card is not None
    # Initially hidden until set_target_card is called
    card.set_target_card(None)
    assert card.isVisible() is False
    # Verify card width fits cleanly in 860x560 window without horizontal overflow
    assert card.minimumSizeHint().width() < 680
    # Verify no emojis in notice banner
    notice = card.lbl_notice.text()
    assert "💡" not in notice and "🎙" not in notice
    # Verify option cards keep clean minimum height across repeated state refreshes
    assert card.frame_a2dp.minimumHeight() >= 150
    assert card.frame_hfp.minimumHeight() >= 150
    card._update_ui_state("a2dp")
    assert card._rendered_mode == "a2dp"
    card._update_ui_state("hfp")
    assert card._rendered_mode == "hfp"


def test_status_badge_min_height(qapp):
    from app.ui.components.status_badge import StatusBadge
    badge = StatusBadge("KDE (wayland)", variant="primary")
    assert badge.minimumHeight() >= 26


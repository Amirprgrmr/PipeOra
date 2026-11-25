import os
import pytest
from PySide6.QtWidgets import QApplication

os.environ["QT_QPA_PLATFORM"] = "offscreen"

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_icon_helper_loading(qapp):
    from app.ui.styles.icon_helper import IconHelper

    icons_to_test = [
        "speaker-high", "speaker-low", "speaker-mute",
        "headphones", "headset-mic", "bluetooth", "bluetooth-connected",
        "display-hdmi", "nav-home", "nav-devices", "nav-bluetooth",
        "nav-settings", "nav-info", "star-filled", "star-outline",
        "battery-high", "refresh", "check-circle", "pipeora",
        "check-mark", "chevron-down", "plus", "minus",
        "info-circle", "auto-switch", "mic-on", "mic-off"
    ]

    for name in icons_to_test:
        icon = IconHelper.get_icon(name)
        assert not icon.isNull(), f"آیکون {name} به درستی بارگذاری نشد!"
        pix = IconHelper.get_pixmap(name, 32)
        assert not pix.isNull(), f"پیکس‌مپ {name} خالی است!"

def test_speaker_icon_variants(qapp):
    from app.ui.styles.icon_helper import IconHelper

    icon_mute = IconHelper.speaker_icon(70, muted=True)
    assert not icon_mute.isNull()

    icon_low = IconHelper.speaker_icon(30, muted=False)
    assert not icon_low.isNull()

    icon_high = IconHelper.speaker_icon(85, muted=False)
    assert not icon_high.isNull()

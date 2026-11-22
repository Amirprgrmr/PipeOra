"""
مدیریت اجرای خودکار برنامه هنگام ورود به نشست دسکتاپ لینوکس (XDG Autostart)
"""

import logging
import os
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DESKTOP_TEMPLATE = """[Desktop Entry]
Type=Application
Name=PipeOra
Name[fa]=مدیریت هوشمند صدای PipeOra
Comment=Professional Linux Audio & Bluetooth Manager for PipeWire
Comment[fa]=مدیریت پیشرفته و اختصاصی خروجی صدا و بلوتوث لینوکس
Exec={exec_cmd}
Icon={icon_path}
Terminal=false
Categories=AudioVideo;Audio;Mixer;
X-GNOME-Autostart-enabled=true
X-KDE-autostart-after=panel
StartupWMClass=PipeOra
"""


class AutostartService:
    """مدیریت فایل‌های Autostart در پوشه ~/.config/autostart/"""

    def __init__(self, autostart_dir: Optional[str] = None):
        if autostart_dir:
            self.autostart_dir = Path(autostart_dir)
        else:
            config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
            self.autostart_dir = Path(config_home) / "autostart"

        self.desktop_file = self.autostart_dir / "pipeora.desktop"

    def is_enabled(self) -> bool:
        """بررسی وجود فایل autostart برای برنامه."""
        return self.desktop_file.exists()

    def enable(self, exec_path: Optional[str] = None, icon_path: str = "pipeora") -> bool:
        """ایجاد فایل autostart برای اجرای خودکار در ورود به سیستم."""
        if not exec_path:
            # اگر اسکریپت در مخزن یا سیستم نصب شده است
            project_root = Path(__file__).resolve().parent.parent.parent
            run_sh = project_root / "run.sh"
            if run_sh.exists():
                exec_cmd = f"{run_sh} --minimized"
            else:
                exec_cmd = f"{sys.executable} -m app.main --minimized"
        else:
            exec_cmd = exec_path

        try:
            self.autostart_dir.mkdir(parents=True, exist_ok=True)
            content = DESKTOP_TEMPLATE.format(
                exec_cmd=exec_cmd,
                icon_path=icon_path
            )
            with open(self.desktop_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.desktop_file.chmod(0o755)
            logger.info("اجرای خودکار فعال شد: %s", self.desktop_file)
            return True
        except Exception as e:
            logger.error("خطا در ایجاد فایل autostart: %s", e)
            return False

    def disable(self) -> bool:
        """حذف فایل autostart و غیرفعال‌سازی اجرای خودکار."""
        try:
            if self.desktop_file.exists():
                self.desktop_file.unlink()
                logger.info("اجرای خودکار غیرفعال شد.")
            return True
        except Exception as e:
            logger.error("خطا در غیرفعال‌سازی autostart: %s", e)
            return False

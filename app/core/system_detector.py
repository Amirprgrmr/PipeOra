"""
ماژول تشخیص سلامت و وضعیت سرویس‌های سیستمی
PipeWire, WirePlumber, BlueZ, systemd
"""

import os
import shutil
import subprocess
from typing import Dict, Any


class SystemDetector:
    """تشخیص و مانیتورینگ وضعیت سرویس‌های صوتی و بلوتوث سیستم."""

    REQUIRED_TOOLS = ["wpctl", "pactl", "pw-dump", "bluetoothctl"]

    def __init__(self):
        pass

    def check_service(self, service_name: str, is_user: bool = True) -> bool:
        """بررسی فعال بودن یک سرویس systemd بدون استفاده از shell."""
        cmd = ["systemctl"]
        if is_user:
            cmd.append("--user")
        cmd.extend(["is-active", service_name])

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=2.0
            )
            return res.stdout.strip() == "active"
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            return False

    def check_pipewire(self) -> bool:
        """بررسی وضعیت سرویس صوتی PipeWire."""
        return self.check_service("pipewire", is_user=True)

    def check_wireplumber(self) -> bool:
        """بررسی وضعیت مدیریت سشن WirePlumber."""
        return self.check_service("wireplumber", is_user=True)

    def check_pipewire_pulse(self) -> bool:
        """بررسی سرویس سازگاری PulseAudio برای PipeWire."""
        return self.check_service("pipewire-pulse", is_user=True)

    def check_bluez(self) -> bool:
        """بررسی سرویس بلوتوث سیستم (BlueZ)."""
        return self.check_service("bluetooth", is_user=False)

    def check_tools(self) -> Dict[str, bool]:
        """بررسی وجود ابزارهای خط فرمان ضروری در سیستم."""
        return {tool: shutil.which(tool) is not None for tool in self.REQUIRED_TOOLS}

    def get_system_health(self) -> Dict[str, Any]:
        """ارائه گزارش کامل و ساختاریافته از سلامت زیرساخت سیستم."""
        pw = self.check_pipewire()
        wp = self.check_wireplumber()
        pw_pulse = self.check_pipewire_pulse()
        bluez = self.check_bluez()
        tools = self.check_tools()

        is_audio_ready = pw and wp and pw_pulse and all(tools.values())

        desktop_session = os.environ.get("XDG_CURRENT_DESKTOP", "KDE")
        session_type = os.environ.get("XDG_SESSION_TYPE", "wayland")

        return {
            "pipewire": pw,
            "wireplumber": wp,
            "pipewire_pulse": pw_pulse,
            "bluez": bluez,
            "tools": tools,
            "is_audio_ready": is_audio_ready,
            "desktop_session": desktop_session,
            "session_type": session_type,
            "all_healthy": is_audio_ready and bluez
        }

"""
مدل‌های داده مربوط به دستگاه‌های بلوتوث
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class BTDevice:
    """مدل دستگاه بلوتوث (با تمرکز بر تجهیزات صوتی و هدفون‌ها)."""
    mac_address: str
    name: str
    alias: str
    icon: str
    paired: bool
    connected: bool
    trusted: bool
    rssi: Optional[int] = None
    battery_percentage: Optional[int] = None
    uuids: List[str] = field(default_factory=list)
    is_audio_device: bool = False

    @property
    def display_name(self) -> str:
        """نام قابل نمایش دستگاه."""
        return self.alias or self.name or self.mac_address

    @property
    def is_headset(self) -> bool:
        """بررسی اینکه آیا دستگاه هدفون یا ایرپاد است."""
        icon_lower = self.icon.lower()
        return "headset" in icon_lower or "headphones" in icon_lower

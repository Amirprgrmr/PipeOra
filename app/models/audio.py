"""
تعریف مدل‌های داده مربوط به دستگاه‌های صوتی و استریم برنامه‌ها
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class SinkDevice:
    """مدل خروجی صوتی (فقط Sink - بدون هرگونه ورودی یا میکروفن)."""
    id: int
    name: str
    description: str
    mute: bool
    volume_percent: int
    active_port: Optional[str] = None
    is_default: bool = False
    is_bluetooth: bool = False
    card_id: Optional[int] = None
    card_name: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        """ارائه نام تمیز و قابل فهم برای نمایش به کاربر."""
        if self.description:
            # ترجمه یا خلاصه‌سازی موارد رایج
            if "Built-in Audio" in self.description:
                return "بلندگوی داخلی (Built-in Audio)"
            if "Digital Stereo (HDMI)" in self.description:
                return "خروجی دیجیتال HDMI"
            return self.description
        return self.name


@dataclass
class AppStream:
    """مدل استریم صوتی برنامه‌های در حال پخش."""
    id: int
    name: str
    binary: str
    sink_id: int
    volume_percent: int
    mute: bool
    icon_name: Optional[str] = None

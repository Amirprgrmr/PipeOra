"""
کلاس کمکی بارگذاری، مدیریت کش و رندر آیکون‌های برداری SVG
جایگزین استاندارد ایموجی‌ها و استیکرها در رابط کاربری
"""

from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QPixmap


class IconHelper:
    """بارگذاری و نگهداری آیکون‌های وکتور اختصاصی SVG."""

    _icons_dir = Path(__file__).resolve().parent.parent.parent / "resources" / "icons"
    _cache: Dict[str, QIcon] = {}

    @classmethod
    def get_icon(cls, name: str) -> QIcon:
        """بارگذاری آیکون از مسیر SVG با کش‌گذاری حافظه."""
        clean_name = name.removesuffix(".svg")
        if clean_name in cls._cache:
            return cls._cache[clean_name]

        svg_path = cls._icons_dir / f"{clean_name}.svg"
        if not svg_path.exists():
            # بازگشت آیکون خالی در صورت عدم وجود
            return QIcon()

        icon = QIcon(str(svg_path))
        cls._cache[clean_name] = icon
        return icon

    @classmethod
    def get_pixmap(cls, name: str, size: int = 24) -> QPixmap:
        """تولید QPixmap برداری در ابعاد مشخص."""
        icon = cls.get_icon(name)
        return icon.pixmap(QSize(size, size))

    @classmethod
    def speaker_icon(cls, volume: int, muted: bool = False) -> QIcon:
        """انتخاب آیکون وکتور مناسب اسپیکر بر اساس سطح بلندی صدا و وضعیت بی‌صدا."""
        if muted or volume == 0:
            return cls.get_icon("speaker-mute")
        elif volume < 50:
            return cls.get_icon("speaker-low")
        else:
            return cls.get_icon("speaker-high")

    @classmethod
    def star_icon(cls, filled: bool = False) -> QIcon:
        """آیکون ستاره علاقه‌مندی توپر یا خالی."""
        return cls.get_icon("star-filled" if filled else "star-outline")

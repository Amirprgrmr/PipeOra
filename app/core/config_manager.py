"""
مدیریت ذخیره و بازیابی تنظیمات نرم‌افزار PipeOra
ذخیره‌سازی با فرمت استاندارد JSON در مسیر استاندارد XDG (~/.config/pipeora/config.json)
همراه با مهاجرت خودکار تنظیمات قبلی
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_CONFIG: Dict[str, Any] = {
    "favorite_device": None,
    "auto_connect_favorite": True,
    "prefer_a2dp": True,
    "autostart": False,
    "start_minimized": False,
    "close_to_tray": True,
    "notifications_enabled": True
}


class ConfigManager:
    """مدیریت پایدار تنظیمات کاربر با قابلیت اطمینان، بازیابی خودکار و مهاجرت شفاف."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            config_home = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
            self.config_path = Path(config_home) / "pipeora" / "config.json"
            self._migrate_old_config(Path(config_home))

        self._data: Dict[str, Any] = dict(DEFAULT_CONFIG)
        self.load()

    def _migrate_old_config(self, config_home: Path) -> None:
        """مهاجرت شفاف تنظیمات نسخه قبلی در صورت وجود."""
        old_path = config_home / "am-audio-control" / "config.json"
        if old_path.exists() and not self.config_path.exists():
            try:
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(old_path, self.config_path)
                logger.info("تنظیمات قبلی از %s به %s مهاجرت داده شد.", old_path, self.config_path)
            except Exception as e:
                logger.warning("خطا در مهاجرت تنظیمات قبلی: %s", e)

    def load(self) -> None:
        """بارگذاری تنظیمات از فایل JSON دیسک."""
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    self._data.update(loaded)
        except Exception as e:
            logger.warning("خطا در خواندن فایل تنظیمات (%s). بازگشت به مقادیر پیش‌فرض: %s", self.config_path, e)
            self._data = dict(DEFAULT_CONFIG)

    def save(self) -> bool:
        """ذخیره امن و اتمیک تنظیمات بر روی دیسک."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.config_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            temp_path.replace(self.config_path)
            return True
        except Exception as e:
            logger.error("خطا در ذخیره فایل تنظیمات: %s", e)
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """دریافت یک کلید از تنظیمات."""
        return self._data.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        """مقداردهی یک کلید و ذخیره خودکار اختیاری."""
        self._data[key] = value
        if auto_save:
            self.save()

    def get_favorite_device(self) -> Optional[str]:
        """دریافت شناسه/آدرس MAC دستگاه محبوب."""
        return self.get("favorite_device")

    def set_favorite_device(self, mac_or_id: Optional[str]) -> None:
        """تعیین یا حذف دستگاه محبوب."""
        self.set("favorite_device", mac_or_id)

    def is_auto_connect_enabled(self) -> bool:
        """بررسی فعال بودن اتصال خودکار به دستگاه محبوب."""
        return bool(self.get("auto_connect_favorite", True))

    def set_auto_connect_enabled(self, enabled: bool) -> None:
        """فعال یا غیرفعال‌سازی اتصال خودکار."""
        self.set("auto_connect_favorite", enabled)

    def is_prefer_a2dp_enabled(self) -> bool:
        """بررسی اولویت انتخاب پروفایل A2DP."""
        return bool(self.get("prefer_a2dp", True))

    def set_prefer_a2dp_enabled(self, enabled: bool) -> None:
        """تنظیم اولویت انتخاب پروفایل A2DP."""
        self.set("prefer_a2dp", enabled)

    def is_autostart_enabled(self) -> bool:
        """بررسی وضعیت اجرای خودکار هنگام ورود به سیستم."""
        return bool(self.get("autostart", False))

    def set_autostart_enabled(self, enabled: bool) -> None:
        """تنظیم اجرای خودکار."""
        self.set("autostart", enabled)

    def is_close_to_tray_enabled(self) -> bool:
        """بررسی فعال بودن بستن پنجره به سینی سیستم (System Tray)."""
        return bool(self.get("close_to_tray", True))

    def set_close_to_tray_enabled(self, enabled: bool) -> None:
        """تنظیم بستن به سینی سیستم."""
        self.set("close_to_tray", enabled)

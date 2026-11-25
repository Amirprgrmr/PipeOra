"""
مدیریت ایمن مسیر منابع نرم‌افزار در محیط توسعه، نصب پکیج و بسته‌های مستقل PyInstaller
"""

import sys
from pathlib import Path


def get_app_dir() -> Path:
    """بازگرداندن مسیر ریشه پکیج app در اجرا از سورس یا فایل باینری Frozen."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        bundled_app = Path(meipass) / "app"
        if bundled_app.exists():
            return bundled_app
    return Path(__file__).resolve().parent.parent


def get_project_root() -> Path:
    """بازگرداندن مسیر ریشه پروژه یا پوشه موقت بسته اجرایی."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return Path(__file__).resolve().parent.parent.parent


def get_resource_path(*parts: str) -> Path:
    """ساخت مسیر دقیق فایل‌های استاتیک و آیکون‌ها داخل پکیج app."""
    return get_app_dir().joinpath(*parts)

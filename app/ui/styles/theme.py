"""
تعریف ثابت‌های پالت رنگی Graphite Dark و مشخصات تایپوگرافی
"""

class Theme:
    # پالت رنگی اصلی (Graphite Dark)
    BG_DARK = "#111318"          # پس‌زمینه اصلی پنجره
    CARD_BG = "#191E27"          # کارت‌ها و بخش‌های اصلی
    CARD_BG_HOVER = "#1E2430"    # حالت هاور کارت‌ها
    SURFACE_SECONDARY = "#222936"# سطوح ثانویه و فرم‌ها
    BORDER_COLOR = "#2D3545"     # خطوط حاشیه و جداکننده‌ها
    BORDER_LIGHT = "#3B4559"     # خطوط حاشیه روشن‌تر

    # رنگ‌های تاکیدی و معنایی
    PRIMARY = "#67C9F3"          # رنگ اصلی (آبی آسمانی مدرن)
    PRIMARY_HOVER = "#85D5F6"
    PRIMARY_ACTIVE = "#4DBEEF"
    
    SUCCESS = "#55CFA0"          # وضعیت موفق / متصل (سبز زمردی)
    WARNING = "#E9B96E"          # وضعیت هشدار (کهربایی)
    ERROR = "#EB7777"            # وضعیت خطا / قطع (مرجانی)

    # متون و تایپوگرافی
    TEXT_PRIMARY = "#F2F4F8"     # متن اصلی و پرکنتراست
    TEXT_SECONDARY = "#A6AFBD"   # متن ثانویه و توضیحات
    TEXT_MUTED = "#6B7687"       # متن کم‌رنگ و برچسب‌های کم‌اهمیت

    # فونت‌های پیشنهادی فارسی
    FONT_FAMILY = "Vazirmatn, Noto Sans Arabic, Segoe UI, sans-serif"
    FONT_CODE = "Vazir Code, FreeMono, monospace"

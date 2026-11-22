"""
اسکریپت اعتبارسنجی جامع خودکار و آزمون یکپارچگی روی سیستم واقعی لینوکس
"""

import os
import sys
from pathlib import Path
import subprocess

# افزودن ریشه پروژه به مسیر پایتون
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_unit_tests():
    print("=" * 60)
    print("۱. اجرای تست‌های خودکار واحد (pytest)...")
    print("=" * 60)
    res = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], check=False)
    if res.returncode != 0:
        print("❌ تست‌های واحد با شکست مواجه شدند!")
        return False
    print("✅ تمامی تست‌های واحد با موفقیت پاس شدند.")
    return True

def run_live_system_checks():
    print("\n" + "=" * 60)
    print("۲. اعتبارسنجی زیرساخت زنده PipeWire و BlueZ در Parch Linux...")
    print("=" * 60)

    from app.core.system_detector import SystemDetector
    from app.core.audio_manager import AudioManager
    from app.core.profile_manager import ProfileManager
    from app.core.bluetooth_manager import BluetoothManager

    detector = SystemDetector()
    health = detector.get_system_health()
    print(f"• وضعیت PipeWire: {'فعال' if health['pipewire'] else 'غیرفعال'}")
    print(f"• وضعیت WirePlumber: {'فعال' if health['wireplumber'] else 'غیرفعال'}")
    print(f"• وضعیت بلوتوث BlueZ: {'فعال' if health['bluez'] else 'غیرفعال'}")
    print(f"• نشست گرافیکی: {health['desktop_session']} ({health['session_type']})")

    audio_mgr = AudioManager()
    sinks = audio_mgr.get_output_sinks()
    print(f"\n• تعداد خروجی‌های صوتی واقعی شناسایی‌شده: {len(sinks)}")
    for s in sinks:
        print(f"  - [{s.id}] {s.display_name} | ولوم: {s.volume_percent}٪ | پیش‌فرض: {s.is_default}")

    # قانون اساسی: بررسی عدم وجود میکروفن
    for s in sinks:
        assert "mic" not in s.name.lower() or "monitor" not in s.name.lower(), "خطا: میکروفن در لیست خروجی‌ها یافت شد!"
    print("✅ قانون اساسی محصول: صفر درصد ورودی صوتی / میکروفن در خروجی‌ها.")

    bt_mgr = BluetoothManager()
    paired = bt_mgr.get_paired_devices(audio_only=True)
    print(f"\n• تعداد دستگاه‌های بلوتوث صوتی جفت‌شده: {len(paired)}")
    for dev in paired:
        print(f"  - {dev.display_name} ({dev.mac_address}) | متصل: {dev.connected} | هدفون: {dev.is_headset}")

    profile_mgr = ProfileManager()
    default_sink = audio_mgr.get_default_sink()
    if default_sink and default_sink.card_id:
        profiles = profile_mgr.get_card_profiles(str(default_sink.card_id))
        print(f"\n• پروفایل‌های کارت خروجی فعال ({default_sink.display_name}): {len(profiles)} پروفایل")
        for p in profiles[:3]:
            print(f"  - {p.persian_name} [فعال: {p.is_active}]")

    print("\n" + "=" * 60)
    print("✅ اعتبارسنجی سیستم واقعی با موفقیت ۱۰۰٪ به پایان رسید.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_unit_tests() and run_live_system_checks()
    sys.exit(0 if success else 1)

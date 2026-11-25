"""
مدیریت پروفایل‌های صوتی کارت‌ها در PipeWire
با اولویت قطعی برای پروفایل استریوی باکیفیت (A2DP) و عدم انتخاب خودکار HFP/HSP
"""

import json
import logging
import subprocess
import time
from dataclasses import dataclass
from typing import List, Optional, Any, Tuple

logger = logging.getLogger(__name__)


@dataclass
class AudioProfile:
    """مدل پروفایل صوتی یک کارت سخت‌افزاری یا بلوتوث."""
    name: str
    description: str
    persian_name: str
    available: bool
    priority: int
    is_active: bool
    is_a2dp: bool = False
    is_hfp: bool = False


class ProfileManager:
    """مدیریت و سوئیچ پروفایل‌های صوتی در سطح کارت‌های پایپ‌وایر با اتوماسیون هوشمند ورودی میکروفن."""

    def __init__(self, audio_mgr: Optional[Any] = None):
        self._audio_mgr = audio_mgr

    @property
    def audio_manager(self):
        """دسترسی با بارگذاری تنبل به AudioManager."""
        if self._audio_mgr is None:
            from app.core.audio_manager import AudioManager
            self._audio_mgr = AudioManager()
        return self._audio_mgr

    def _run_cmd(self, cmd: List[str], timeout: float = 3.0) -> Optional[str]:
        """اجرای ایمن دستورات خط فرمان با مدیریت خطای کامل."""
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout
            )
            if res.returncode == 0:
                return res.stdout
            return None
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            logger.error("خطا در اجرای دستور پروفایل: %s", e)
            return None

    def get_persian_profile_name(self, profile_name: str, desc: str) -> str:
        """ترجمه و بومی‌سازی نام پروفایل برای کاربر فارسی‌زبان."""
        p_lower = profile_name.lower()
        d_lower = desc.lower()

        if "a2dp" in p_lower or "a2dp" in d_lower:
            return "پخش استریوی باکیفیت (A2DP)"
        elif "headset" in p_lower or "hfp" in p_lower or "hsp" in p_lower:
            return "پروفایل مکالمه (HFP/HSP - کیفیت پایین)"
        elif "analog-stereo" in p_lower:
            return "استریو آنالوگ (اسپیکر / هدفون سیمی)"
        elif "hdmi" in p_lower:
            return "خروجی صوتی دیجیتال HDMI"
        elif "pro-audio" in p_lower:
            return "صدای حرفه‌ای و کم‌تاخیر (Pro Audio)"
        elif p_lower == "off":
            return "خاموش / غیرفعال"

        return desc or profile_name

    def _find_card(self, cards: List[dict], card_id_or_name: str) -> Optional[dict]:
        """یافتن کارت صوتی بر اساس شناسه، نام، شیء پایپ‌وایر یا مک آدرس بلوتوث."""
        target_str = str(card_id_or_name).strip()
        if not target_str:
            return None

        clean_mac = target_str.replace(":", "_").lower()

        for c in cards:
            c_index = str(c.get("index", ""))
            c_name = str(c.get("name", ""))
            props = c.get("properties", {}) or {}
            dev_name = str(props.get("device.name", ""))
            obj_id = str(props.get("object.id", ""))
            bt_addr = str(props.get("api.bluez5.address", ""))
            dev_str = str(props.get("device.string", ""))

            # تطابق مستقیم
            if target_str in (c_index, c_name, dev_name, obj_id, bt_addr, dev_str):
                return c

            # تطابق با مک آدرس بلوتوث
            if clean_mac and clean_mac in c_name.lower():
                return c

        return None

    def get_card_profiles(self, card_id_or_name: str) -> List[AudioProfile]:
        """دریافت پروفایل‌های کارت صوتی و تحلیل آنها."""
        out = self._run_cmd(["pactl", "-f", "json", "list", "cards"])
        if not out:
            return []

        try:
            cards = json.loads(out)
        except json.JSONDecodeError:
            return []

        matched_card = self._find_card(cards, card_id_or_name)
        if not matched_card:
            return []

        active_profile_name = matched_card.get("active_profile", "")
        raw_profiles = matched_card.get("profiles", {})

        profiles: List[AudioProfile] = []

        # pactl -f json می‌تواند profiles را به صورت dict یا list بازگرداند
        profile_items = []
        if isinstance(raw_profiles, dict):
            for p_name, p_data in raw_profiles.items():
                if isinstance(p_data, dict):
                    data = dict(p_data)
                    data["name"] = p_name
                    profile_items.append(data)
        elif isinstance(raw_profiles, list):
            profile_items = raw_profiles

        for p in profile_items:
            name = p.get("name", "")
            desc = p.get("description", name)
            available = p.get("available") in ["yes", True]
            priority = p.get("priority", 0)
            is_active = (name == active_profile_name)

            p_lower = name.lower()
            is_a2dp = "a2dp" in p_lower or "a2dp" in desc.lower()
            is_hfp = "hfp" in p_lower or "hsp" in p_lower or "headset" in p_lower

            persian_name = self.get_persian_profile_name(name, desc)

            profiles.append(AudioProfile(
                name=name,
                description=desc,
                persian_name=persian_name,
                available=available,
                priority=priority,
                is_active=is_active,
                is_a2dp=is_a2dp,
                is_hfp=is_hfp
            ))

        # مرتب‌سازی: ابتدا فعال، سپس اولویت عددی
        profiles.sort(key=lambda x: (x.is_active, x.is_a2dp, x.priority), reverse=True)
        return profiles

    def set_card_profile(self, card_id_or_name: str, profile_name: str) -> bool:
        """اعمال تغییر پروفایل صوتی بر روی کارت در PipeWire."""
        target = str(card_id_or_name).strip()
        prof = str(profile_name).strip()

        # استخراج نام یا ایندکس معتبر کارت
        out = self._run_cmd(["pactl", "-f", "json", "list", "cards"])
        if out:
            try:
                cards = json.loads(out)
                matched = self._find_card(cards, target)
                if matched and matched.get("name"):
                    target = str(matched.get("name"))
                elif matched and matched.get("index") is not None:
                    target = str(matched.get("index"))
            except json.JSONDecodeError:
                pass

        res = self._run_cmd(["pactl", "set-card-profile", target, prof])
        return res is not None

    def get_wireplumber_autoswitch(self) -> Optional[bool]:
        """خواندن وضعیت سوییچ خودکار پروفایل هدست در WirePlumber."""
        out = self._run_cmd(
            ["wpctl", "settings", "bluetooth.autoswitch-to-headset-profile"],
            timeout=2.0
        )
        if not out:
            return None
        for line in out.splitlines():
            clean = line.strip().lower()
            if clean.startswith("value:"):
                val = clean.split(":", 1)[1].strip()
                if val.startswith("true"):
                    return True
                if val.startswith("false"):
                    return False
        return None

    def set_wireplumber_autoswitch(self, enabled: bool) -> bool:
        """
        تنظیم زنده سیاست تغییر خودکار پروفایل هدست در WirePlumber.
        هنگام قفل دستی پروفایل روی HFP یا A2DP باید غیرفعال شود تا پروفایل بعد از ۴ ثانیه نپرد.
        """
        val_str = "true" if enabled else "false"
        key = "bluetooth.autoswitch-to-headset-profile"
        res = self._run_cmd(["wpctl", "settings", key, val_str], timeout=2.0)
        if res is not None:
            # ذخیره دائمی مقدار جاری در تنظیمات WirePlumber
            self._run_cmd(["wpctl", "settings", "--save", key], timeout=2.0)
            return True
        return False

    def get_headset_status(self, card_id_or_name: str) -> Tuple[bool, str]:
        """
        دریافت هم‌زمان پشتیبانی دوحالته و حالت فعال فعلی هدست با یک فراخوانی pactl:
        خروجی: (has_headset_modes, 'a2dp' | 'hfp' | 'other')
        """
        profiles = self.get_card_profiles(card_id_or_name)
        has_a2dp = any(p.is_a2dp for p in profiles)
        has_hfp = any(p.is_hfp for p in profiles)
        active_mode = "other"
        for p in profiles:
            if p.is_active:
                if p.is_a2dp:
                    active_mode = "a2dp"
                elif p.is_hfp:
                    active_mode = "hfp"
                break
        return (has_a2dp and has_hfp), active_mode

    def has_headset_modes(self, card_id_or_name: str) -> bool:
        """بررسی اینکه آیا کارت صوتی از دو حالت A2DP و HFP پشتیبانی می‌کند یا خیر."""
        has_modes, _ = self.get_headset_status(card_id_or_name)
        return has_modes

    def get_headset_mode(self, card_id_or_name: str) -> str:
        """
        تشخیص حالت فعلی هدست بلوتوث:
        - 'a2dp': حالت پخش موسیقی باکیفیت بالا (میکروفن هدفون غیرفعال)
        - 'hfp': حالت مکالمه و تماس (میکروفن هدفون فعال)
        - 'other': سایر حالات یا عدم پشتیبانی
        """
        _, mode = self.get_headset_status(card_id_or_name)
        return mode

    def _find_bluetooth_source(self, card_id_or_name: str, max_retries: int = 15, delay: float = 0.05) -> Optional[str]:
        """یافتن منبع ورودی میکروفن بلوتوث (bluez_input) پس از تغییر پروفایل به HFP."""
        target_str = str(card_id_or_name).strip()
        clean_mac = target_str.replace(":", "_").lower()

        for _ in range(max_retries):
            out = self._run_cmd(["pactl", "-f", "json", "list", "sources"])
            if out:
                try:
                    sources = json.loads(out)
                    for s in sources:
                        name = s.get("name", "")
                        if "bluez" in name.lower() and "input" in name.lower() and "monitor" not in name.lower():
                            if clean_mac and clean_mac in name.lower().replace(":", "_"):
                                return name
                            return name
                except json.JSONDecodeError:
                    pass
            time.sleep(delay)

        return None

    def set_headset_mode(self, card_id_or_name: str, mode: str, disable_autoswitch: bool = True) -> bool:
        """
        تغییر مستقیم حالت کاربری هدفون بلوتوث با حل ریشه‌ای پرش ۴ ثانیه‌ای WirePlumber و اتوماسیون میکروفن:
        - mode='a2dp':
            ۱. غیرفعال‌سازی autoswitch در صورت قفل دستی تا استریم‌های پس‌زمینه کیفیت موسیقی را خراب نکنند
            ۲. جابه‌جایی ورودی پیش‌فرض سیستم و استریم‌های فعال به میکروفن لپ‌تاپ
            ۳. سوییچ کارت به کیفیت عالی موسیقی (A2DP Stereo)
        - mode='hfp':
            ۱. غیرفعال‌سازی autoswitch در صورت قفل دستی تا WirePlumber بعد از ۴ ثانیه پروفایل را به A2DP برنگرداند
            ۲. سوییچ کارت به پروفایل مکالمه (HFP Headset)
            ۳. تنظیم خودکار منبع پیش‌فرض سیستم و برنامه‌ها به میکروفن هدفون
        """
        profiles = self.get_card_profiles(card_id_or_name)
        target_mode = mode.lower().strip()

        def _pick_profile(is_target):
            avail = [p for p in profiles if is_target(p) and p.available]
            return avail[0] if avail else next((p for p in profiles if is_target(p)), None)

        if target_mode == "a2dp":
            prof = _pick_profile(lambda p: p.is_a2dp)
            if prof:
                logger.info("شروع فرآیند سوییچ به حالت موسیقی A2DP: %s", prof.name)
                if disable_autoswitch:
                    self.set_wireplumber_autoswitch(False)

                fallback_mic = self.audio_manager.get_hardware_fallback_source()
                if fallback_mic:
                    logger.info("انتقال ورودی سیستم به میکروفن داخلی: %s", fallback_mic)
                    self.audio_manager.set_default_source(fallback_mic)
                    self.audio_manager.move_recording_streams(fallback_mic)

                return self.set_card_profile(card_id_or_name, prof.name)

        elif target_mode == "hfp":
            prof = _pick_profile(lambda p: p.is_hfp)
            if prof:
                logger.info("شروع فرآیند سوییچ به حالت مکالمه HFP: %s", prof.name)
                if disable_autoswitch:
                    self.set_wireplumber_autoswitch(False)

                res = self.set_card_profile(card_id_or_name, prof.name)
                if not res:
                    return False

                bt_source = self._find_bluetooth_source(card_id_or_name)
                if bt_source:
                    logger.info("تنظیم خودکار میکروفن هدفون به عنوان ورودی اصلی: %s", bt_source)
                    self.audio_manager.set_default_source(bt_source)
                    self.audio_manager.move_recording_streams(bt_source)

                return True

        logger.warning("پروفایل متناسب با حالت %s در کارت %s یافت نشد.", mode, card_id_or_name)
        return False

    def switch_to_a2dp_if_possible(self, card_id_or_name: str) -> bool:
        """سوئیچ خودکار به پروفایل باکیفیت A2DP در صورت پشتیبانی کارت."""
        has_modes, mode = self.get_headset_status(card_id_or_name)
        if has_modes and mode != "a2dp":
            return self.set_headset_mode(card_id_or_name, "a2dp", disable_autoswitch=False)
        profiles = self.get_card_profiles(card_id_or_name)
        for p in profiles:
            if p.is_a2dp and p.available and not p.is_active:
                logger.info("سوئیچ خودکار به پروفایل باکیفیت A2DP: %s", p.name)
                return self.set_card_profile(card_id_or_name, p.name)
        return False

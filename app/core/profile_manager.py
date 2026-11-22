"""
مدیریت پروفایل‌های صوتی کارت‌ها در PipeWire
با اولویت قطعی برای پروفایل استریوی باکیفیت (A2DP) و عدم انتخاب خودکار HFP/HSP
"""

import json
import logging
import subprocess
from dataclasses import dataclass
from typing import List, Optional

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
    """مدیریت و سوئیچ پروفایل‌های صوتی در سطح کارت‌های پایپ‌وایر."""

    def __init__(self):
        pass

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

    def get_card_profiles(self, card_id_or_name: str) -> List[AudioProfile]:
        """دریافت پروفایل‌های کارت صوتی و تحلیل آنها."""
        out = self._run_cmd(["pactl", "-f", "json", "list", "cards"])
        if not out:
            return []

        try:
            cards = json.loads(out)
        except json.JSONDecodeError:
            return []

        target_str = str(card_id_or_name)
        matched_card = None
        for c in cards:
            if str(c.get("index")) == target_str or c.get("name") == target_str:
                matched_card = c
                break

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
        res = self._run_cmd(["pactl", "set-card-profile", target, prof])
        return res is not None

    def switch_to_a2dp_if_possible(self, card_id_or_name: str) -> bool:
        """سوئیچ خودکار به پروفایل باکیفیت A2DP در صورت پشتیبانی کارت."""
        profiles = self.get_card_profiles(card_id_or_name)
        for p in profiles:
            if p.is_a2dp and p.available and not p.is_active:
                logger.info("سوئیچ خودکار به پروفایل باکیفیت A2DP: %s", p.name)
                return self.set_card_profile(card_id_or_name, p.name)
        return False

"""
مدیریت خروجی‌های صوتی و ولوم از طریق PipeWire و رابط سازگاری PulseAudio
منحصراً برای مدیریت خروجی صدا (بدون هیچ‌گونه قابلیت ورودی یا میکروفن)
"""

import json
import logging
import subprocess
from typing import List, Optional, Dict, Any

from app.models.audio import SinkDevice, AppStream

logger = logging.getLogger(__name__)


class AudioManager:
    """ارتباط با PipeWire از طریق pactl ساختاریافته (JSON) و wpctl."""

    def __init__(self):
        pass

    def _run_cmd(self, cmd: List[str], timeout: float = 2.0) -> Optional[str]:
        """اجرای ایمن دستورات خط فرمان بدون shell=True با مدیریت خطای کامل."""
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
            logger.warning("دستور %s با کد %d شکست خورد: %s", " ".join(cmd), res.returncode, res.stderr)
            return None
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            logger.error("خطا در اجرای دستور %s: %s", cmd, e)
            return None

    def get_default_sink_name(self) -> Optional[str]:
        """دریافت نام خروجی صوتی پیش‌فرض فعلی از pactl."""
        out = self._run_cmd(["pactl", "-f", "json", "info"])
        if not out:
            return None
        try:
            data = json.loads(out)
            return data.get("default_sink_name")
        except json.JSONDecodeError:
            return None

    def get_output_sinks(self) -> List[SinkDevice]:
        """
        دریافت فهرست تمام خروجی‌های صوتی سیستم (Sinks).
        قانون اساسی: فقط Sinks پردازش می‌شوند؛ هرگز Sources یا ورودی‌ها لیست نمی‌شوند.
        """
        out = self._run_cmd(["pactl", "-f", "json", "list", "sinks"])
        if not out:
            return []

        default_sink = self.get_default_sink_name()

        try:
            sinks_data = json.loads(out)
        except json.JSONDecodeError:
            return []

        devices: List[SinkDevice] = []
        for s in sinks_data:
            sink_id = s.get("index", 0)
            sink_name = s.get("name", "")
            description = s.get("description", sink_name)
            mute = bool(s.get("mute", False))
            active_port = s.get("active_port")
            props = s.get("properties", {})

            # محاسبه درصد ولوم به صورت میانگین کانال‌ها
            volume_percent = self._extract_volume_percent(s.get("volume", {}))

            # بررسی نوع دستگاه (آیا بلوتوث است؟)
            is_bt = (
                "bluez" in sink_name.lower() or
                props.get("device.api") == "bluez5" or
                "bluez" in props.get("device.bus", "").lower()
            )

            card_id = None
            if "device.id" in props:
                try:
                    card_id = int(props["device.id"])
                except (ValueError, TypeError):
                    pass

            is_default = (sink_name == default_sink) or (f"@{sink_id}@" == default_sink)

            card_name = props.get("device.name")

            device = SinkDevice(
                id=sink_id,
                name=sink_name,
                description=description,
                mute=mute,
                volume_percent=volume_percent,
                active_port=active_port,
                is_default=is_default,
                is_bluetooth=is_bt,
                card_id=card_id,
                card_name=card_name,
                properties=props
            )
            devices.append(device)

        return devices

    def _extract_volume_percent(self, vol_dict: Dict[str, Any]) -> int:
        """استخراج درصد میانگین ولوم از آبجکت volume در pactl json."""
        percentages = []
        for ch_data in vol_dict.values():
            if isinstance(ch_data, dict) and "value_percent" in ch_data:
                pct_str = ch_data["value_percent"].replace("%", "").strip()
                try:
                    percentages.append(int(pct_str))
                except ValueError:
                    pass

        if percentages:
            avg = sum(percentages) // len(percentages)
            return max(0, min(100, avg))
        return 0

    def get_default_sink(self) -> Optional[SinkDevice]:
        """یافتن و بازگرداندن سینک پیش‌فرض فعال."""
        sinks = self.get_output_sinks()
        for s in sinks:
            if s.is_default:
                return s
        if sinks:
            return sinks[0]
        return None

    def set_default_sink(self, sink_name_or_id: str) -> bool:
        """انتخاب یک سینک به عنوان خروجی پیش‌فرض سیستم."""
        clean_target = str(sink_name_or_id).strip()
        res = self._run_cmd(["pactl", "set-default-sink", clean_target])
        if res is not None:
            return True
        # تلاش مجدد با wpctl در صورت نیاز
        if clean_target.isdigit():
            wp_res = self._run_cmd(["wpctl", "set-default", clean_target])
            return wp_res is not None
        return False

    def set_volume(self, sink_name_or_id: str, volume_percent: int) -> bool:
        """تنظیم حجم صدای خروجی مشخص (بین ۰ تا ۱۰۰ درصد)."""
        clamped_volume = max(0, min(100, int(volume_percent)))
        vol_str = f"{clamped_volume}%"
        target = str(sink_name_or_id).strip()

        res = self._run_cmd(["pactl", "set-sink-volume", target, vol_str])
        return res is not None

    def change_volume(self, sink_name_or_id: str, delta_percent: int) -> bool:
        """تغییر گامی حجم صدا (مثلاً +5% یا -5%)."""
        current_sink = self.get_default_sink() if str(sink_name_or_id).lower() in ["@default@", "@default_sink@"] else None
        if not current_sink:
            for s in self.get_output_sinks():
                if str(s.id) == str(sink_name_or_id) or s.name == str(sink_name_or_id):
                    current_sink = s
                    break

        new_vol = 50
        if current_sink:
            new_vol = current_sink.volume_percent + delta_percent

        return self.set_volume(sink_name_or_id, new_vol)

    def set_mute(self, sink_name_or_id: str, mute: bool) -> bool:
        """تنظیم وضعیت بی‌صدا (Mute) برای یک خروجی."""
        mute_val = "1" if mute else "0"
        target = str(sink_name_or_id).strip()
        res = self._run_cmd(["pactl", "set-sink-mute", target, mute_val])
        return res is not None

    def toggle_mute(self, sink_name_or_id: str) -> bool:
        """معکوس کردن وضعیت بی‌صدا برای یک خروجی."""
        target = str(sink_name_or_id).strip()
        res = self._run_cmd(["pactl", "set-sink-mute", target, "toggle"])
        return res is not None

    def get_sink_inputs(self) -> List[AppStream]:
        """دریافت لیست برنامه‌هایی که در حال حاضر صدا پخش می‌کنند."""
        out = self._run_cmd(["pactl", "-f", "json", "list", "sink-inputs"])
        if not out:
            return []

        try:
            streams_data = json.loads(out)
        except json.JSONDecodeError:
            return []

        streams: List[AppStream] = []
        for st in streams_data:
            stream_id = st.get("index", 0)
            sink_id = st.get("sink", 0)
            mute = bool(st.get("mute", False))
            vol_pct = self._extract_volume_percent(st.get("volume", {}))

            props = st.get("properties", {})
            app_name = props.get("application.name") or props.get("media.name") or "برنامه صوتی"
            binary = props.get("application.process.binary", "")
            icon_name = props.get("application.icon_name")

            streams.append(AppStream(
                id=stream_id,
                name=app_name,
                binary=binary,
                sink_id=sink_id,
                volume_percent=vol_pct,
                mute=mute,
                icon_name=icon_name
            ))

        return streams

    def set_sink_input_volume(self, input_id: int, volume_percent: int) -> bool:
        """تنظیم حجم صدای یک استریم برنامه مشخص."""
        clamped = max(0, min(100, int(volume_percent)))
        res = self._run_cmd(["pactl", "set-sink-input-volume", str(input_id), f"{clamped}%"])
        return res is not None

    def move_sink_input(self, input_id: int, sink_name_or_id: str) -> bool:
        """انتقال خروجی صدای یک برنامه به خروجی دیگر."""
        res = self._run_cmd(["pactl", "move-sink-input", str(input_id), str(sink_name_or_id)])
        return res is not None

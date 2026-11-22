"""
مدیریت دستگاه‌های بلوتوث از طریق BlueZ D-Bus و bluetoothctl
با تمرکز بر هدفون‌ها و دستگاه‌های صوتی بلوتوث
"""

import logging
import re
import subprocess
from typing import List, Optional, Dict, Any

from app.models.bluetooth import BTDevice

logger = logging.getLogger(__name__)

# UUIDهای رایج صوتی استاندارد بلوتوث
AUDIO_UUIDS = {
    "0000110b-0000-1000-8000-00805f9b34fb",  # Audio Sink (A2DP)
    "0000110a-0000-1000-8000-00805f9b34fb",  # Audio Source
    "0000110c-0000-1000-8000-00805f9b34fb",  # A/V Remote Control Target
    "0000110e-0000-1000-8000-00805f9b34fb",  # A/V Remote Control
    "0000111e-0000-1000-8000-00805f9b34fb",  # Handsfree
    "00001108-0000-1000-8000-00805f9b34fb",  # Headset
}


class BluetoothManager:
    """ارتباط با سرویس BlueZ و مدیریت دستگاه‌های بلوتوث."""

    MAC_REGEX = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")

    def __init__(self):
        self._bus = None
        self._init_dbus()

    def _init_dbus(self):
        """تلاش برای اتصال به D-Bus سیستم."""
        try:
            import dbus
            self._bus = dbus.SystemBus()
        except Exception as e:
            logger.warning("اتصال به D-Bus بلوتوث برقرار نشد: %s (از Fallback خط فرمان استفاده خواهد شد)", e)
            self._bus = None

    def _validate_mac(self, mac: str) -> bool:
        """اعتبارسنجی فرمت آدرس سخت‌افزاری MAC برای امنیت."""
        return bool(self.MAC_REGEX.match(mac.strip()))

    def _get_dbus_objects(self) -> Dict[str, Any]:
        """دریافت درخت اشیاء مدیریت‌شده از BlueZ D-Bus."""
        if not self._bus:
            self._init_dbus()
        if not self._bus:
            return {}

        try:
            import dbus
            bluez = self._bus.get_object("org.bluez", "/")
            mgr = dbus.Interface(bluez, "org.freedesktop.DBus.ObjectManager")
            return mgr.GetManagedObjects()
        except Exception as e:
            logger.debug("خطا در دریافت اشیاء از D-Bus: %s", e)
            return {}

    def is_bluetooth_powered(self) -> bool:
        """بررسی روشن بودن آداپتور بلوتوث سیستم."""
        objects = self._get_dbus_objects()
        for path, ifaces in objects.items():
            if "org.bluez.Adapter1" in ifaces:
                return bool(ifaces["org.bluez.Adapter1"].get("Powered", False))

        # Fallback با bluetoothctl
        try:
            res = subprocess.run(
                ["bluetoothctl", "show"],
                capture_output=True,
                text=True,
                check=False,
                timeout=2.0
            )
            return "Powered: yes" in res.stdout
        except Exception:
            return False

    def set_bluetooth_powered(self, powered: bool) -> bool:
        """روشن یا خاموش کردن آداپتور بلوتوث."""
        arg = "on" if powered else "off"
        try:
            res = subprocess.run(
                ["bluetoothctl", "power", arg],
                capture_output=True,
                text=True,
                check=False,
                timeout=3.0
            )
            return res.returncode == 0
        except Exception:
            return False

    def get_paired_devices(self, audio_only: bool = True) -> List[BTDevice]:
        """
        دریافت فهرست دستگاه‌های جفت‌شده با تمرکز بر تجهیزات صوتی.
        درصد باتری و سیگنال فقط در صورت ارائه اطلاعات واقعی از BlueZ ثبت می‌شوند.
        """
        devices: List[BTDevice] = []
        objects = self._get_dbus_objects()

        if objects:
            for path, ifaces in objects.items():
                if "org.bluez.Device1" in ifaces:
                    dev_data = ifaces["org.bluez.Device1"]
                    if not dev_data.get("Paired", False):
                        continue

                    mac = str(dev_data.get("Address", ""))
                    name = str(dev_data.get("Name", mac))
                    alias = str(dev_data.get("Alias", name))
                    icon = str(dev_data.get("Icon", "audio-headset"))
                    connected = bool(dev_data.get("Connected", False))
                    trusted = bool(dev_data.get("Trusted", False))

                    raw_rssi = dev_data.get("RSSI")
                    rssi = int(raw_rssi) if raw_rssi is not None else None

                    # استخراج درصد باتری واقعی از اینترفیس Battery1
                    battery_pct = None
                    if "org.bluez.Battery1" in ifaces:
                        raw_bat = ifaces["org.bluez.Battery1"].get("Percentage")
                        if raw_bat is not None:
                            battery_pct = int(raw_bat)

                    uuids = [str(u).lower() for u in dev_data.get("UUIDs", [])]

                    # بررسی اینکه آیا دستگاه صوتی است؟
                    has_audio_uuid = any(u in AUDIO_UUIDS for u in uuids)
                    has_audio_icon = "audio" in icon.lower() or "headset" in icon.lower()
                    is_audio = has_audio_uuid or has_audio_icon

                    if audio_only and not is_audio:
                        continue

                    devices.append(BTDevice(
                        mac_address=mac,
                        name=name,
                        alias=alias,
                        icon=icon,
                        paired=True,
                        connected=connected,
                        trusted=trusted,
                        rssi=rssi,
                        battery_percentage=battery_pct,
                        uuids=uuids,
                        is_audio_device=is_audio
                    ))
            return devices

        # Fallback با bluetoothctl
        return self._get_paired_devices_cli(audio_only)

    def _get_paired_devices_cli(self, audio_only: bool = True) -> List[BTDevice]:
        """روش جایگزین دریافت دستگاه‌های جفت‌شده از طریق خط فرمان."""
        devices = []
        try:
            res = subprocess.run(
                ["bluetoothctl", "devices"],
                capture_output=True,
                text=True,
                check=False,
                timeout=3.0
            )
            for line in res.stdout.splitlines():
                parts = line.strip().split(" ", 2)
                if len(parts) >= 3 and parts[0] == "Device":
                    mac = parts[1]
                    name = parts[2]
                    info = self.get_device_info_cli(mac)
                    if info:
                        devices.append(info)
        except Exception as e:
            logger.error("خطا در خواندن دستگاه‌های بلوتوث از CLI: %s", e)
        return devices

    def get_device_info_cli(self, mac: str) -> Optional[BTDevice]:
        """خواندن اطلاعات تفصیلی یک دستگاه از bluetoothctl info."""
        if not self._validate_mac(mac):
            return None

        try:
            res = subprocess.run(
                ["bluetoothctl", "info", mac],
                capture_output=True,
                text=True,
                check=False,
                timeout=3.0
            )
            out = res.stdout
            name = mac
            alias = mac
            paired = "Paired: yes" in out
            connected = "Connected: yes" in out
            trusted = "Trusted: yes" in out
            icon = "audio-headset"

            for line in out.splitlines():
                line = line.strip()
                if line.startswith("Name:"):
                    name = line.split(":", 1)[1].strip()
                elif line.startswith("Alias:"):
                    alias = line.split(":", 1)[1].strip()
                elif line.startswith("Icon:"):
                    icon = line.split(":", 1)[1].strip()

            battery_pct = None
            bat_match = re.search(r"Battery Percentage:\s*0x[0-9a-fA-F]+\s*\((\d+)\)", out)
            if bat_match:
                battery_pct = int(bat_match.group(1))

            return BTDevice(
                mac_address=mac,
                name=name,
                alias=alias,
                icon=icon,
                paired=paired,
                connected=connected,
                trusted=trusted,
                battery_percentage=battery_pct,
                is_audio_device=True
            )
        except Exception:
            return None

    def connect_device(self, mac_address: str) -> bool:
        """اتصال به یک دستگاه بلوتوث جفت‌شده."""
        mac = mac_address.strip()
        if not self._validate_mac(mac):
            logger.warning("آدرس MAC نامعتبر برای اتصال: %s", mac)
            return False

        try:
            res = subprocess.run(
                ["bluetoothctl", "connect", mac],
                capture_output=True,
                text=True,
                check=False,
                timeout=8.0
            )
            return "Connection successful" in res.stdout or res.returncode == 0
        except Exception as e:
            logger.error("خطا در اتصال به دستگاه بلوتوث %s: %s", mac, e)
            return False

    def disconnect_device(self, mac_address: str) -> bool:
        """قطع اتصال از یک دستگاه بلوتوث."""
        mac = mac_address.strip()
        if not self._validate_mac(mac):
            logger.warning("آدرس MAC نامعتبر برای قطع اتصال: %s", mac)
            return False

        try:
            res = subprocess.run(
                ["bluetoothctl", "disconnect", mac],
                capture_output=True,
                text=True,
                check=False,
                timeout=5.0
            )
            return "Successful disconnected" in res.stdout or res.returncode == 0
        except Exception as e:
            logger.error("خطا در قطع اتصال دستگاه بلوتوث %s: %s", mac, e)
            return False

    def start_discovery(self) -> bool:
        """شروع جستجوی دستگاه‌های بلوتوث جدید."""
        try:
            res = subprocess.run(
                ["bluetoothctl", "scan", "on"],
                capture_output=True,
                text=True,
                check=False,
                timeout=3.0
            )
            return res.returncode == 0
        except Exception:
            return False

    def stop_discovery(self) -> bool:
        """توقف جستجوی دستگاه‌های بلوتوث."""
        try:
            res = subprocess.run(
                ["bluetoothctl", "scan", "off"],
                capture_output=True,
                text=True,
                check=False,
                timeout=3.0
            )
            return res.returncode == 0
        except Exception:
            return False

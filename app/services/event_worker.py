"""
ورکر پس‌زمینه دریافت زنده رویدادهای PipeWire و بلوتوث (EventWorker)
مبتنی بر QThread و دستور pactl subscribe برای به‌روزرسانی آنی رابط کاربری بدون Polling سنگین
"""

import logging
import subprocess
import time
from typing import Optional

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class EventWorker(QThread):
    """
    شنود پیوسته رویدادهای صوتی لینوکس در ترد جداگانه
    و مخابره سیگنال‌های امن Qt به ترد اصلی رابط کاربری.
    """

    # سیگنال‌های وضعیت صوتی
    sink_changed = Signal(str)            # تغییر در خروجی‌های صوتی (ولوم، پورت، ایجاد/حذف)
    server_changed = Signal()             # تغییر در سرور یا تغییر خروجی پیش‌فرض
    stream_changed = Signal()             # تغییر در استریم‌های برنامه‌ها (پخش، توقف، ولوم برنامه)
    card_changed = Signal(str)            # تغییر در کارت‌های صوتی و پروفایل‌ها
    bluetooth_changed = Signal()          # اتصال یا قطع دستگاه‌های بلوتوث

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._proc: Optional[subprocess.Popen] = None

    def run(self):
        """اجرای حلقه شنود رویدادها."""
        self._running = True
        logger.info("سرویس شنود رویدادهای زنده صوتی شروع به کار کرد.")

        # شروع فرآیند pactl subscribe
        try:
            self._proc = subprocess.Popen(
                ["pactl", "subscribe"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1
            )
        except Exception as e:
            logger.error("خطا در اجرای pactl subscribe: %s", e)
            self._running = False
            return

        last_bt_check = 0.0

        while self._running:
            # بررسی دوره‌ای وضعیت بلوتوث هر ۲.۵ ثانیه
            now = time.time()
            if now - last_bt_check >= 2.5:
                self.bluetooth_changed.emit()
                last_bt_check = now

            if not self._proc or not self._proc.stdout:
                break

            line = self._proc.stdout.readline()
            if not line:
                if self._proc.poll() is not None:
                    # فرآیند متوقف شده است (مثلاً ریستارت پایپ‌وایر)
                    time.sleep(1.0)
                    try:
                        self._proc = subprocess.Popen(
                            ["pactl", "subscribe"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            text=True,
                            bufsize=1
                        )
                    except Exception:
                        pass
                continue

            event_line = line.strip()
            # فیلتر کردن دقیق رویدادهای مربوط به میکروفن یا ورودی‌ها
            if "source" in event_line.lower() and "source-output" not in event_line.lower():
                # رویدادهای منابع میکروفن کاملاً نادیده گرفته می‌شوند
                continue

            # تحلیل رویدادهای خروجی صوتی
            if "sink #" in event_line:
                self.sink_changed.emit(event_line)
            elif "server" in event_line:
                self.server_changed.emit()
            elif "sink-input" in event_line:
                self.stream_changed.emit()
            elif "card" in event_line:
                self.card_changed.emit(event_line)

    def stop(self):
        """توقف تمیز ورکر و خاتمه دادن به ساب‌پراسس."""
        self._running = False
        if self._proc:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=1.0)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
            self._proc = None
        self.wait()
        logger.info("سرویس شنود رویدادهای صوتی متوقف شد.")

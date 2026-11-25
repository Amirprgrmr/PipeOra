"""
ورکر پس‌زمینه دریافت زنده رویدادهای PipeWire و بلوتوث (EventWorker)
مبتنی بر QThread، دستور pactl subscribe و selectors برای شنود غیربلاکینگ و به‌روزرسانی آنی
"""

import logging
import os
import selectors
import shutil
import subprocess
import time
from typing import Optional

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class EventWorker(QThread):
    """
    شنود پیوسته رویدادهای صوتی لینوکس در ترد جداگانه با I/O غیربلاکینگ
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

    def _spawn_subscribe(self) -> Optional[subprocess.Popen]:
        """اجرای فرآیند pactl subscribe با بافر صفر برای قرائت خام با selector."""
        return subprocess.Popen(
            ["pactl", "subscribe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )

    def _process_line(self, event_line: str):
        """تحلیل خط رویداد و مخابره سیگنال مناسب به رابط کاربری."""
        lower = event_line.lower()
        if not lower:
            return

        # نادیده گرفتن تغییرات خام منابع ورودی (میکروفن)
        if "on source #" in lower:
            return

        if "on sink #" in lower:
            self.sink_changed.emit(event_line)
        elif "on server" in lower:
            self.server_changed.emit()
        elif "on sink-input #" in lower:
            self.stream_changed.emit()
        elif "on card #" in lower or "on source-output #" in lower:
            # تغییر کارت یا شروع/پایان استریم ضبط (برای بازتاب سوییچ خودکار هدست در UI)
            self.card_changed.emit(event_line)

    def run(self):
        """اجرای حلقه غیربلاکینگ شنود رویدادها."""
        if shutil.which("pactl") is None:
            logger.info("ابزار pactl در این سیستم‌عامل یافت نشد؛ سرویس شنود زنده رویدادهای PipeWire غیرفعال ماند.")
            self._running = False
            return

        self._running = True
        logger.info("سرویس شنود رویدادهای زنده صوتی شروع به کار کرد.")

        try:
            self._proc = self._spawn_subscribe()
        except Exception as e:
            logger.error("خطا در اجرای pactl subscribe: %s", e)
            self._running = False
            return

        sel = selectors.DefaultSelector()
        fd = self._proc.stdout.fileno() if self._proc and self._proc.stdout else None
        if fd is not None:
            sel.register(fd, selectors.EVENT_READ)

        last_bt_check = 0.0
        byte_buf = b""

        try:
            while self._running:
                now = time.time()
                if now - last_bt_check >= 2.5:
                    self.bluetooth_changed.emit()
                    last_bt_check = now

                if not self._proc or not self._proc.stdout:
                    break

                events = sel.select(timeout=0.4)
                if not events:
                    continue

                chunk = os.read(fd, 4096)
                if not chunk:
                    # EOF - فرآیند متوقف شده (مثلاً ریستارت PipeWire)
                    try:
                        sel.unregister(fd)
                    except Exception:
                        pass
                    if not self._running:
                        break
                    time.sleep(1.0)
                    try:
                        self._proc = self._spawn_subscribe()
                        if self._proc and self._proc.stdout:
                            fd = self._proc.stdout.fileno()
                            sel.register(fd, selectors.EVENT_READ)
                            byte_buf = b""
                    except Exception:
                        pass
                    continue

                byte_buf += chunk
                while b"\n" in byte_buf:
                    raw_line, byte_buf = byte_buf.split(b"\n", 1)
                    line = raw_line.decode("utf-8", errors="replace").strip()
                    if line:
                        self._process_line(line)
        finally:
            try:
                sel.close()
            except Exception:
                pass

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
        self.wait(1500)
        logger.info("سرویس شنود رویدادهای صوتی متوقف شد.")

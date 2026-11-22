# برنامه اجرایی و معماری فنی AM Audio Control
## نرم‌افزار دسکتاپ اختصاصی مدیریت صدای لینوکس | Parch & Arch Linux

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** طراحی، پیاده‌سازی، آزمایش و بسته‌بندی نرم‌افزار دسکتاپ بومی و اختصاصی **AM Audio Control** (مدیریت صدای AM) با پایتون و PySide6 (Qt 6) برای پلتفرم Parch Linux / Arch Linux در محیط KDE Plasma (Wayland/X11)، با اتصال ۱۰۰٪ واقعی به زیرساخت PipeWire، WirePlumber و BlueZ و رعایت قانون بنیادین حذف کامل هرگونه ورودی و میکروفن.

**Architecture:** تفکیک دقیق لایه‌ها (Layered Architecture)؛ هسته ارتباطی شامل Audio Manager (مبتنی بر `pactl -f json` و `wpctl` و شنود زنده رویدادهای `pactl subscribe`)، Bluetooth Manager (مبتنی بر اینترفیس D-Bus سرویس `org.bluez` با Fallback امن به `bluetoothctl`)، Profile Manager (تمرکز بر A2DP Stereo)، مدیریت پیکربندی با فرمت JSON در مسیر استاندارد XDG، و رابط کاربری ماژولار PySide6 در تم اختصاصی Graphite Dark با پشتیبانی کامل از چینش راست‌چین (RTL) و ادغام سیستمی با System Tray و Autostart.

**Tech Stack:** Python 3.14+, PySide6 (Qt 6.12+), PipeWire 1.6+, WirePlumber, BlueZ 5+, D-Bus (dbus-python / QtDBus), XDG Desktop Standards, pacman/PKGBUILD.

---

## Global Constraints

- **پلتفرم هدف:** انحصاری لینوکس (Parch Linux، Arch Linux، KDE Plasma، Wayland/X11). هیچ وابستگی به ویندوز، مک، الکترون یا وب وجود ندارد.
- **قانون بنیادین صوتی:** حذف ۱۰۰٪ هرگونه قابلیت میکروفن، ضبط صدا، ورودی صوتی (Sources/Capture) و عدم ارائه HFP/HSP به عنوان قابلیت محصول. اولویت قطعی با A2DP Stereo.
- **امنیت شل:** ممنوعیت مطلق استفاده از `shell=True` در اجرای دستورات سیستمی؛ اعتبارسنجی تمام آرگومان‌ها با لیست مشخص؛ عدم نیاز به دسترسی root یا sudo دائمی.
- **هویت بصری:** تم اختصاصی Graphite Dark بر پایه پالت رنگی استاندارد کاربر (`#111318` پس‌زمینه، `#191E27` کارتها، `#222936` سطوح ثانویه، `#67C9F3` رنگ اصلی، `#55CFA0` موفقیت، `#EB7777` خطا، `#F2F4F8` متن).
- **زبان و چیدمان:** رابط کاربری کاملاً فارسی با استاندارد راست‌چین (RTL) و حفظ جهت چپ‌به‌راست (LTR) در آدرس‌های MAC، درصدها و شناسه‌ها.
- **پایداری فرآیندها:** اجرای عملیات پس‌زمینه و شنود رویدادها در Worker Thread مستقل (`QThread`) جهت جلوگیری از هرگونه انجماد (Freeze) رابط کاربری و جلوگیری از حلقه بازخورد (Feedback Loop) در اسلایدر صدا.

---

## بررسی و یافته‌های محیط واقعی سیستم (System Audit Findings)

بر اساس بررسی‌های عملی انجام‌شده روی سیستم کاربر:
1. **توزیع و نسخه سیستم‌عامل:** Parch Linux Desktop Edition (Rolling)، با هسته لینوکس و ساختار بسته‌بندی Arch Linux.
2. **محیط گرافیکی:** KDE Plasma تحت Wayland (`kwin_wayland`، `plasmashell`).
3. **پایتون:** Python 3.14.10 نصب و فعال در `/usr/bin/python3`.
4. **وضعیت سرویس‌های صوتی کاربر:**
   - `pipewire.service`: Active
   - `wireplumber.service`: Active
   - `pipewire-pulse.service`: Active
   - نسخه پایپ‌وایر: 1.6.11
5. **وضعیت بلوتوث و تجهیزات:**
   - `bluetooth.service`: Active
   - اینترفیس D-Bus در `org.bluez` فعال و در دسترس است.
   - دستگاه هدفون واقعی **QCY T13 ANC2** با مک‌آدرس `84:AC:60:C9:02:74` در سیستم جفت‌شده (Paired) و مورد شناسایی قطعی قرار گرفت.
6. **کارت‌های صوتی موجود:**
   - کارت `0`: HDA Intel PCH (خروجی Built-in Audio Analog Stereo - شناسه پیش‌فرض)
   - کارت `1`: HDA NVidia (خروجی HDMI Digital Stereo)
7. **ابزارهای خط فرمان و کتابخانه‌های کمکی:**
   - `/usr/bin/wpctl` موجود و کارآمد.
   - `/usr/bin/pactl` دارای خروجی مستقیم JSON با پرچم `-f json` برای sinks, cards, sink-inputs.
   - `dbus-python` در سیستم موجود و ارتباط مستقیم با `org.bluez` برقرار می‌کند.
   - بسته رسمی مخزن `extra/pyside6 6.12.0-3` برای Pacman و پکیج‌های PyPI از طریق `uv` سازگار با نسخه پایتون در دسترس هستند.

---

## ساختار درختی پروژه

```
PipeOra/
├── app/
│   ├── __init__.py
│   ├── main.py                          # نقطه ورود برنامه، مدیریت SingleInstance و بارگذاری استایل/آیکون
│   ├── core/
│   │   ├── __init__.py
│   │   ├── system_detector.py           # بررسی وضعیت PipeWire, WirePlumber, BlueZ و پایداری سرویس‌ها
│   │   ├── audio_manager.py             # مدیریت خروجی‌ها، ولوم، بی‌صدا، و استریم برنامه‌ها (خروجی‌محور)
│   │   ├── bluetooth_manager.py         # مدیریت D-Bus با BlueZ، اتصال/قطع، وضعیت باتری واقعی، RSSI
│   │   ├── profile_manager.py           # مدیریت پروفایل کارت‌ها با اولویت استریو باکیفیت (A2DP)
│   │   └── config_manager.py            # ذخیره و بازیابی تنظیمات در ~/.config/am-audio-control/config.json
│   ├── services/
│   │   ├── __init__.py
│   │   ├── event_worker.py              # ترد پس‌زمینه QThread برای دریافت رویدادهای زنده PipeWire و BlueZ
│   │   └── autostart_service.py         # ایجاد و مدیریت فایل autostart در ~/.config/autostart/
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py               # پنجره اصلی با سایدبار، ناوبری واکنش‌گرا و هندل بستن به تری
│   │   ├── tray_icon.py                 # کنترل آیکون System Tray با منوی سریع ولوم، خروج و بازیابی پنجره
│   │   ├── dashboard_page.py            # صفحه خانه: وضعیت سرویس‌ها، کارت خروجی فعال، اسلایدر اصلی، سوئیچ سریع
│   │   ├── devices_page.py              # صفحه دستگاه‌های صوتی: لیست سینک‌های خروجی، پروفایل‌ها، صدای برنامه‌ها
│   │   ├── bluetooth_page.py            # صفحه بلوتوث: دستگاه‌های جفت‌شده، اتصال/قطع، سیگنال و باتری
│   │   ├── settings_page.py             # صفحه تنظیمات: اتصال خودکار هدفون، Autostart، دستگاه محبوب
│   │   ├── about_page.py                # صفحه درباره ما و مشخصات فنی مهندسی
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── volume_slider.py         # اسلایدر اختصاصی با درصد، جلوگیری از Feedback loop و گام‌های کلیدی
│   │   │   ├── device_card.py           # کارت نمایش دستگاه با دکمه‌های وضعیت، بج اتصال و نشان پیش‌فرض
│   │   │   └── status_badge.py          # برچسب وضعیت فشرده با استایل گرافیت و رنگ‌های معنایی
│   │   └── styles/
│   │       ├── __init__.py
│   │       ├── theme.py                 # متغیرهای رنگی، فونت و استانداردهای طراحی Graphite Dark
│   │       └── style.qss                # استایل‌شیت یکپارچه Qt با پشتیبانی کامل از RTL
│   └── resources/
│       ├── __init__.py
│       ├── icons/                       # آیکون‌های SVG برنامه (اسپیکر، هدفون، بلوتوث، تنظیمات و...)
│       │   └── app_icon.svg
│       └── fonts/                       # بارگذاری فونت استاندارد وزیرمتن در صورت نیاز
├── packaging/
│   ├── PKGBUILD                         # فایل ساخت پکیج رسمی برای Arch/Parch Linux با pacman
│   ├── am-audio-control.desktop         # فایل دسکتاپ استاندارد XDG
│   └── am-audio-control.svg             # آیکون برداری باکیفیت بالا
├── docs/
│   ├── README.md                        # مستندات کامل به زبان فارسی
│   ├── INSTALL.md                       # راهنمای نصب و راه‌اندازی در Parch/Arch
│   └── ARCHITECTURE.md                  # مستندات معماری داخلی و ارتباط با PipeWire/BlueZ
├── tests/
│   ├── __init__.py
│   ├── test_system_detector.py
│   ├── test_audio_manager.py
│   ├── test_config_manager.py
│   └── test_profile_manager.py
├── pyproject.toml                       # تعریف متادیتای پایتون و وابستگی‌ها
├── requirements.txt                     # فهرست وابستگی‌ها
└── run.sh                               # اسکریپت راه‌اندازی سریع با محیط مجازی ایزوله
```

---

## Review Focus (حالت‌های حساس و خطاهای احتمالی)

۱. **توقف ناگهانی یا راه‌اندازی مجدد PipeWire/WirePlumber:** نباید برنامه کرش کند؛ مانیتورینگ وضعیت باید پیام خطای فارسی واضح با دکمه "تلاش مجدد" نمایش دهد.
۲. **حلقه فیدبک اسلایدر صدا (Feedback Loop):** هنگامی که کاربر اسلایدر را حرکت می‌دهد، دریافت رویداد تغییر صدا از پایپ‌وایر نباید اسلایدر را دوباره ست کرده و پالس مکرر ایجاد کند (`is_updating_ui` guard).
۳. **تغییر سخت‌افزاری صدا (کلیدهای کیبورد یا سایر برنامه‌ها):** رابط کاربری و سینی سیستم باید در کسری از ثانیه همگام شوند.
۴. **روشن/خاموش شدن بلوتوث یا قطع ناگهانی هدفون (QCY T13 ANC2):** سیستم باید قطع شدن را شناسایی کرده و به صورت خودکار خروجی را به بلندگوی لپ‌تاپ بازگردانده و وضعیت داشبورد را به‌روز کند.
۵. **عدم نمایش کوچکترین ردپای میکروفن:** در تمامی متدهای دریافت خروجی از `pactl` و `wpctl`، تمامی `source`ها و `source-output`ها به صورت قطعی فیلتر می‌شوند تا هیچ ورودی صوتی نمایش داده نشود.

---

## گام‌های اجرایی و وظایف پیاده‌سازی (Tasks)

### Task 1: پیکربندی زیرساخت پروژه، وابستگی‌ها و محیط ایزوله
**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `run.sh`
- Create: `app/__init__.py`

- [ ] **Step 1: ساخت ساختار اولیه دایرکتوری‌ها و فایل‌های محیطی**
- [ ] **Step 2: ایجاد فایل `requirements.txt` شامل `pyside6>=6.8.0`, `dbus-python>=1.3.0`, `pytest>=8.0.0`**
- [ ] **Step 3: ایجاد فایل `run.sh` برای بررسی خودکار پایتون، ایجاد venv با `uv` و اجرای برنامه**
- [ ] **Step 4: تست اجرای سلامت محیط**

---

### Task 2: پیاده‌سازی لایه تشخیص سیستم (System Detector)
**Files:**
- Create: `app/core/system_detector.py`
- Create: `tests/test_system_detector.py`

**Interfaces:**
- `SystemDetector.check_pipewire() -> ServiceStatus`
- `SystemDetector.check_wireplumber() -> ServiceStatus`
- `SystemDetector.check_bluez() -> ServiceStatus`
- `SystemDetector.get_system_health() -> Dict[str, Any]`

- [ ] **Step 1: نوشتن تست‌های واحد برای `SystemDetector` با Mock و بررسی خروجی واقعی `systemctl --user is-active`**
- [ ] **Step 2: پیاده‌سازی `SystemDetector` با استفاده از `subprocess.run` ایمن (بدون shell=True)**
- [ ] **Step 3: اجرای تست‌های واحد و اعتبارسنجی عبور موفقیت‌آمیز**

---

### Task 3: پیاده‌سازی هسته مدیریت صدای PipeWire (Audio Manager)
**Files:**
- Create: `app/core/audio_manager.py`
- Create: `tests/test_audio_manager.py`

**Interfaces:**
- `AudioManager.get_output_sinks() -> List[SinkDevice]` (فقط Sinks، با فیلتر دقیق منابع میکروفن)
- `AudioManager.get_default_sink() -> Optional[SinkDevice]`
- `AudioManager.set_default_sink(sink_name_or_id: str) -> bool`
- `AudioManager.set_volume(sink_name_or_id: str, volume_percent: int) -> bool` (محدود به ۰ تا ۱۰۰)
- `AudioManager.set_mute(sink_name_or_id: str, mute: bool) -> bool`
- `AudioManager.get_sink_inputs() -> List[AppStream]` (فهرست برنامه‌های در حال پخش با شناسه، نام و ولوم)
- `AudioManager.set_sink_input_volume(input_id: int, volume_percent: int) -> bool`
- `AudioManager.move_sink_input(input_id: int, sink_name: str) -> bool`

- [ ] **Step 1: نوشتن تست‌های واحد اعتبارسنجی خروجی‌های صوتی و پارس اطلاعات JSON از `pactl -f json`**
- [ ] **Step 2: پیاده‌سازی `AudioManager` با پردازش واقعی پایپ‌وایر و اعتبارسنجی ورودی‌ها**
- [ ] **Step 3: اجرای تست با دستورات واقعی سیستم و بررسی همخوانی با `wpctl status`**

---

### Task 4: پیاده‌سازی هسته مدیریت پروفایل‌های صوتی (Profile Manager)
**Files:**
- Create: `app/core/profile_manager.py`
- Create: `tests/test_profile_manager.py`

**Interfaces:**
- `ProfileManager.get_card_profiles(card_id_or_name: str) -> List[AudioProfile]`
- `ProfileManager.set_card_profile(card_id_or_name: str, profile_name: str) -> bool`
- `ProfileManager.get_persian_profile_name(profile_name: str) -> str` (ترجمه استاندارد مثل "پخش استریوی باکیفیت (A2DP)")
- `ProfileManager.is_a2dp_supported(card_id_or_name: str) -> bool`

- [ ] **Step 1: نوشتن تست پارس پروفایل‌های کارت صوتی و اولویت‌بندی A2DP**
- [ ] **Step 2: پیاده‌سازی `ProfileManager` با نام‌گذاری خوانای فارسی و نادیده‌گرفتن پروفایل‌های مکالمه کم‌کیفیت**
- [ ] **Step 3: اجرای تست واحد**

---

### Task 5: پیاده‌سازی هسته مدیریت بلوتوث (Bluetooth Manager)
**Files:**
- Create: `app/core/bluetooth_manager.py`
- Create: `tests/test_bluetooth_manager.py`

**Interfaces:**
- `BluetoothManager.get_adapter_status() -> AdapterStatus`
- `BluetoothManager.get_paired_audio_devices() -> List[BTDevice]`
- `BluetoothManager.connect_device(mac_address: str) -> bool`
- `BluetoothManager.disconnect_device(mac_address: str) -> bool`
- `BluetoothManager.get_device_battery(mac_address: str) -> Optional[int]` (فقط درصد واقعی از BlueZ D-Bus)

- [ ] **Step 1: نوشتن تست واحد برای D-Bus Object Manager و ساختار دستگاه‌ها**
- [ ] **Step 2: پیاده‌سازی `BluetoothManager` با اتصال مستقیم به `org.bluez` روی SystemBus**
- [ ] **Step 3: تست خواندن مشخصات هدفون واقعی `QCY T13 ANC2` موجود در سیستم**

---

### Task 6: پیاده‌سازی مدیریت پیکربندی و ذخیره تنظیمات (Config Manager)
**Files:**
- Create: `app/core/config_manager.py`
- Create: `tests/test_config_manager.py`

**Interfaces:**
- `ConfigManager.get_favorite_device() -> Optional[str]`
- `ConfigManager.set_favorite_device(mac_or_name: str)`
- `ConfigManager.is_auto_connect_enabled() -> bool`
- `ConfigManager.set_auto_connect_enabled(enabled: bool)`
- `ConfigManager.is_autostart_enabled() -> bool`
- `ConfigManager.set_autostart_enabled(enabled: bool)`

- [ ] **Step 1: نوشتن تست ذخیره و بازیابی در پوشه کانفیگ XDG کاربر**
- [ ] **Step 2: پیاده‌سازی `ConfigManager` با فرمت استاندارد JSON و پیش‌فرض‌های امن**
- [ ] **Step 3: اجرای تست واحد**

---

### Task 7: سرویس شنود زنده رویدادها (Event Worker) و Autostart
**Files:**
- Create: `app/services/event_worker.py`
- Create: `app/services/autostart_service.py`

**Interfaces:**
- `EventWorker(QThread)` با سیگنال‌های: `sink_changed`, `volume_changed(int, bool)`, `stream_changed`, `bluetooth_status_changed`
- `AutostartService.enable_autostart() -> bool`
- `AutostartService.disable_autostart() -> bool`

- [ ] **Step 1: پیاده‌سازی پروسه پس‌زمینه `pactl subscribe` در ترد غیراصلی Qt بدون اشغال بیهوده CPU**
- [ ] **Step 2: پیاده‌سازی مدیریت فایل `.desktop` در `~/.config/autostart/am-audio-control.desktop`**
- [ ] **Step 3: تست ارسال سیگنال و ایجاد/حذف فایل اتواستارت**

---

### Task 8: طراحی سیستم تم و استایل یکپارچه Graphite Dark (UI Styles & Theme)
**Files:**
- Create: `app/ui/styles/theme.py`
- Create: `app/ui/styles/style.qss`
- Create: `app/resources/icons/app_icon.svg`

- [ ] **Step 1: تعریف کد رنگ‌های معین (`#111318`, `#191E27`, `#222936`, `#67C9F3`, `#55CFA0`, `#EB7777`, `#F2F4F8`)**
- [ ] **Step 2: ساخت استایل‌شیت مدرن Qt Widgets با استانداردهای RTL، گوشه‌های نرم (8-12px)، هاورهای ملایم و اسکرول‌بار ظریف**
- [ ] **Step 3: طراحی آیکون اختصاصی برداری SVG برای نرم‌افزار**

---

### Task 9: پیاده‌سازی کامپوننت‌های سفارشی UI
**Files:**
- Create: `app/ui/components/volume_slider.py`
- Create: `app/ui/components/device_card.py`
- Create: `app/ui/components/status_badge.py`

- [ ] **Step 1: پیاده‌سازی `VolumeSlider` با قابلیت نمایش درصد زنده، کلیک مستقیم، گام‌های ۵٪ و محافظت در برابر Event Loop**
- [ ] **Step 2: پیاده‌سازی `DeviceCard` با نمایش نام، آیکون (بلندگو/هدفون بلوتوث)، وضعیت اتصال، دکمه انتخاب به عنوان پیش‌فرض و ستاره موردعلاقه**
- [ ] **Step 3: پیاده‌سازی `StatusBadge` با رنگ‌های وضعیت فعال، متصل، غیرفعال**

---

### Task 10: پیاده‌سازی صفحات اصلی (Dashboard, Devices, Bluetooth, Settings, About)
**Files:**
- Create: `app/ui/dashboard_page.py`
- Create: `app/ui/devices_page.py`
- Create: `app/ui/bluetooth_page.py`
- Create: `app/ui/settings_page.py`
- Create: `app/ui/about_page.py`

- [ ] **Step 1: پیاده‌سازی Dashboard با کارت Hero خروجی فعال، اسلایدر اصلی، وضعیت سرویس‌ها و انتخاب سریع خروجی**
- [ ] **Step 2: پیاده‌سازی Devices Page با فهرست تفصیلی سینک‌های خروجی، پروفایل صوتی A2DP و مدیریت استریم برنامه‌ها**
- [ ] **Step 3: پیاده‌سازی Bluetooth Page با مدیریت دستگاه‌های جفت‌شده، اتصال هدفون QCY T13 ANC2 و سیگنال/باتری**
- [ ] **Step 4: پیاده‌سازی Settings Page با تنظیمات اتصال خودکار، انتخاب دستگاه محبوب و اجرای خودکار**
- [ ] **Step 5: پیاده‌سازی About Page با مشخصات سازنده (Amirali Homayoonzadeh | amirprgrmr)، نسخه، لینک وب‌سایت و مستندات**

---

### Task 11: پیاده‌سازی پنجره اصلی (Main Window)، System Tray و نقطه ورود اصلی
**Files:**
- Create: `app/ui/main_window.py`
- Create: `app/ui/tray_icon.py`
- Create: `app/main.py`

- [ ] **Step 1: ساخت پنجره اصلی با سایدبار راست‌چین (RTL)، ناوبری روان میان صفحات و پشتیبانی از Wayland**
- [ ] **Step 2: ساخت System Tray با منوی سریع فارسی، کنترل ولوم و امکان Minimize to Tray در زمان بستن پنجره**
- [ ] **Step 3: راه‌اندازی مکانیزم Single Instance با `QLocalServer` برای جلوگیری از اجرای چند نسخه همزمان**
- [ ] **Step 4: اتصال کامل Event Worker به رابط کاربری جهت به‌روزرسانی لحظه‌ای بدون ریفرش دستی**

---

### Task 12: تست جامع و اعتبارسنجی روی سیستم واقعی (Parch Linux / PipeWire / Bluetooth)
**Files:**
- Create: `tests/run_all_tests.py`

- [ ] **Step 1: اجرای تمامی تست‌های واحد خودکار با `pytest`**
- [ ] **Step 2: تست عملی تغییر ولوم سیستم و بررسی تطابق لحظه‌ای با PipeWire**
- [ ] **Step 3: تست عملی شناسایی دستگاه بلوتوث `QCY T13 ANC2` و بررسی اتصال/قطع**
- [ ] **Step 4: تست رفتار برنامه در زمان بستن و فعال بودن در System Tray**
- [ ] **Step 5: تست اجرای خودکار (Autostart)**

---

### Task 13: آماده‌سازی بسته‌بندی، فایل PKGBUILD و مستندات فارسی
**Files:**
- Create: `packaging/PKGBUILD`
- Create: `packaging/am-audio-control.desktop`
- Create: `docs/README.md`
- Create: `docs/INSTALL.md`
- Create: `docs/ARCHITECTURE.md`

- [ ] **Step 1: تدوین فایل `PKGBUILD` استاندارد برای Arch Linux و Parch Linux با وابستگی‌های دقیق**
- [ ] **Step 2: ایجاد فایل Desktop Entry استاندارد با دسته‌بندی `AudioVideo;Audio;Mixer;`**
- [ ] **Step 3: نگارش مستندات جامع فارسی شامل معرفی، راهنمای نصب، عیب‌یابی و معماری**

---

## برنامه اعتبارسنجی و تست (Verification Plan)

### تست‌های خودکار (Automated Tests)
- اجرای `pytest tests/ -v` برای پوشش تست‌های واحد بخش‌های `SystemDetector`, `AudioManager`, `BluetoothManager`, `ConfigManager`.
- تست اعتبارسنجی بدون شل (`shell=False`) و اعتبارسنجی ورودی‌های عددی ولوم (۰ تا ۱۰۰).

### آزمون‌های عملی روی سیستم واقعی (Manual Verification Checklist)
۱. اجرای نرم‌افزار با اسکریپت `./run.sh` روی Parch Linux و تأیید باز شدن پنجره در محیط KDE Plasma تحت Wayland.
۲. بررسی کامل چینش راست‌چین (RTL) و خوانایی فونت فارسی در تمام صفحات.
۳. تغییر ولوم از طریق اسلایدر برنامه و مشاهده تغییر واقعی خروجی صدای سیستم در ویجت ولوم KDE Plasma.
۴. فشردن کلیدهای سخت‌افزاری ولوم لپ‌تاپ و مشاهده به‌روزرسانی آنی اسلایدر در برنامه.
۵. بررسی شناسایی خروجی اسپیکر داخلی لپ‌تاپ و هدفون بلوتوث QCY T13 ANC2.
۶. بررسی عدم وجود هرگونه گزینه، تب یا متغیر مرتبط با میکروفن یا ضبط صدا.
۷. تست بستن پنجره و بررسی ماندگاری آیکون در System Tray و عملکرد منوی سریع.
۸. فعال‌سازی گزینه Autostart و تأیید ایجاد فایل در `~/.config/autostart/`.

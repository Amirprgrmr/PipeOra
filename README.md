<div dir="rtl">

# PipeOra — مدیریت پیشرفته و هوشمند صدا و بلوتوث

[![Version](https://img.shields.io/badge/Version-v1.0.1-67C9F3?style=flat-square)](https://github.com/Amirprgrmr/PipeOra/releases)
[![Platform](https://img.shields.io/badge/Primary%20OS-Parch%20%7C%20Arch%20Linux-1793D1?style=flat-square)](https://parchlinux.com)
[![Builds](https://img.shields.io/badge/Standalone%20Builds-Linux%20%7C%20Windows%20%7C%20macOS-55CFA0?style=flat-square)](#ساخت-نسخه-اجرایی-مستقل-برای-سه-سیستم‌عامل)
[![Audio](https://img.shields.io/badge/Audio-PipeWire%20%2B%20WirePlumber-2EA44F?style=flat-square)](https://pipewire.org)
[![UI](https://img.shields.io/badge/UI-PySide6%20Qt%206%20(RTL)-41CD52?style=flat-square)](https://doc.qt.io/qtforpython-6/)
[![License](https://img.shields.io/badge/License-MIT-9AA4B2?style=flat-square)](LICENSE)

**PipeOra** یک نرم‌افزار دسکتاپ سبک، سریع و خوش‌ساخت با **Python 3** و **PySide6 (Qt 6)** برای مدیریت دقیق خروجی‌های صدا، پروفایل هدست‌های بلوتوث و میکسر صدای برنامه‌هاست. طراحی این ابزار بر اساس نیاز واقعی دسکتاپ **Parch Linux / Arch Linux** (محیط **KDE Plasma تحت Wayland**) و با رابط کاربری کاملاً راست‌چین فارسی و تم مهندسی **Graphite Dark** انجام شده است.

---

## ویژگی‌ها و قابلیت‌های کلیدی

### تمرکز ۱۰۰٪ بر خروجی صدا بدون شلوغی اضافه
- فهرست خروجی‌ها و داشبورد منحصراً روی **Audio Output Sinks** تمرکز دارد تا کنترل صدا سریع، خلوت و شفاف باشد (بدون شلوغی کارت‌های ضبط صدا و ورودی‌های متعدد).

### مدیریت هوشمند پروفایل هدست بلوتوث (A2DP / HFP) و قفل دستی پایدار
- سوئیچ یک‌کلیک میان **موسیقی و فیلم (`A2DP` استریو ۴۸ کیلوهرتز AAC/SBC)** و **مکالمه و تماس (`HFP` با میکروفن هدفون)**.
- **حل ریشه‌ای پرش ۴ ثانیه‌ای WirePlumber:** با مدیریت مستقیم سیاست `bluetooth.autoswitch-to-headset-profile` از طریق `wpctl settings`، در حالت **قفل دستی پایدار** انتخاب شما روی `HFP` یا `A2DP` ثابت می‌ماند و خودبه‌خود بعد از چند ثانیه برنمی‌گردد؛ در عین حال می‌توانید گزینه **تغییر خودکار هوشمند (`WirePlumber Auto`)** را در هر لحظه روشن یا خاموش کنید.
- **انتقال خودکار میکروفن و استریم‌ها:** هنگام خروج از حالت مکالمه (`HFP -> A2DP`)، ورودی پیش‌فرض سیستم خودکار به میکروفن سخت‌افزاری داخلی لپ‌تاپ منتقل می‌شود تا در پخش موسیقی افت کیفیت رخ ندهد.

### شنود زنده رویدادها با مصرف منابع ناچیز
- پایش بلادرنگ تغییرات کارت‌های صوتی، پورت‌ها، استریم‌های ضبط/پخش و وضعیت اتصال بلوتوث از طریق `pactl subscribe` و `selectors.DefaultSelector()` بدون polling سنگین.
- همگام‌سازی دوجانبه با کلیدهای سخت‌افزاری کیبورد و کاهش چشمگیر ترافیک IPC هنگام جابه‌جایی اسلایدر ولوم (`40Hz` throttling).

### میکسر برنامه‌ها، بلوتوث D-Bus و ادغام کامل با دسکتاپ
- **میکسر صدای برنامه‌ها (`DevicesPage`):** کنترل مستقل بلندی صدا و جابه‌جایی خروجی هر برنامه در حال پخش (مرورگر، تلگرام، مدیاپلیر و...).
- **مدیریت بلوتوث (`BluetoothPage`):** ارتباط مستقیم با `org.bluez` روی D-Bus (با Fallback خودکار `bluetoothctl`)، نمایش درصد باتری واقعی هدفون، قدرت سیگنال و تنظیم دستگاه محبوب.
- **ادغام دسکتاپ:** اجرای تک‌نسخه‌ای (`QLocalServer`)، آیکون و منوی زنده در سینی سیستم (System Tray)، پشتیبانی از بستن به Tray و اجرای خودکار با XDG Autostart.
- **طراحی تمیز با آیکون‌های برداری:** بدون استفاده از ایموجی یا استیکر در UI؛ تمام اجزا با آیکون‌های SVG اختصاصی و تایپوگرافی استاندارد فارسی (`Vazirmatn` / `Noto Sans Arabic`).

---

## وضعیت پشتیبانی سیستم‌عامل‌ها

PipeOra دارای **پایپ‌لاین ساخت خودکار برای هر سه سیستم‌عامل (Linux، Windows و macOS)** است؛ با این حال از نظر فنی مهم است تفاوت سطح پشتیبانی زیرساخت صوتی را دقیق بدانید:

| سیستم‌عامل | بسته قابل دانلود (Release) | وضعیت رابط گرافیکی (Qt 6) | وضعیت کنترل صوتی و بلوتوث |
| :--- | :--- | :---: | :--- |
| **Linux (Parch / Arch / Wayland & X11)** | `PipeOra-v*-linux-x86_64.tar.gz` + `.whl` + `PKGBUILD` | کامل | **کامل و بومی** (`PipeWire`, `WirePlumber`, `BlueZ`, `pactl`, `wpctl`) |
| **Windows (x86_64)** | `PipeOra-v*-windows-x86_64.zip` (`PipeOra.exe`) | کامل (مستقل) | فاقد بک‌اند `PipeWire`/`BlueZ` (برای پیش‌نمایش UI و توسعه بک‌اند آینده) |
| **macOS (Apple Silicon / Universal)** | `PipeOra-v*-macos-*.dmg` (`PipeOra.app`) | کامل (مستقل) | فاقد بک‌اند `PipeWire`/`BlueZ` (برای پیش‌نمایش UI و توسعه بک‌اند آینده) |

---

## نصب و راه‌اندازی

### ۱. دریافت بسته‌های آماده از GitHub Releases
جدیدترین نسخه آماده برای **Linux**، **Windows** و **macOS** به‌همراه فایل `SHA256SUMS.txt` در صفحه [Releases](https://github.com/Amirprgrmr/PipeOra/releases) منتشر می‌شود:

- **لینوکس (پرتابل مستقل):** استخراج `PipeOra-v*-linux-x86_64.tar.gz` و اجرای `./PipeOra/PipeOra`
- **ویندوز:** استخراج `PipeOra-v*-windows-x86_64.zip` و اجرای `PipeOra.exe`
- **مک‌اواس:** باز کردن `PipeOra-v*-macos-*.dmg` و انتقال `PipeOra.app` به پوشه `Applications`

### ۲. نصب بومی در Arch Linux و Parch Linux (`PKGBUILD`)

```bash
git clone https://github.com/Amirprgrmr/PipeOra.git
cd PipeOra/packaging
makepkg -si
```

پس از نصب، با دستور `pipeora` یا از منوی برنامه‌های KDE اجرا می‌شود.

### ۳. اجرا از سورس کد (محیط توسعه)

پیش‌نیازهای سیستم روی **Parch / Arch Linux**:

```bash
sudo pacman -S --needed python pyside6 pipewire pipewire-pulse wireplumber bluez bluez-utils python-dbus
```

اجرای مستقیم با اسکریپت راه‌انداز:

```bash
git clone https://github.com/Amirprgrmr/PipeOra.git
cd PipeOra
chmod +x run.sh
./run.sh
```

---

## ساخت نسخه اجرایی مستقل برای سه سیستم‌عامل

اسکریپت یکپارچه [`scripts/build_app.py`](scripts/build_app.py) با استفاده از **PyInstaller** و بسته‌بندی بومی، خروجی مستقل سیستم‌عامل فعلی را می‌سازد، تست `--version` را اجرا می‌کند و بسته نهایی را در پوشه `dist/` قرار می‌دهد:

```bash
# نصب وابستگی‌های بیلد در محیط مجازی محلی
.venv/bin/pip install -r requirements.txt pyinstaller

# ساخت بسته مستقل متناسب با سیستم‌عامل فعلی (Linux .tar.gz / Windows .zip / macOS .dmg)
.venv/bin/python scripts/build_app.py

# پیش‌نمایش دستور ساخت برای هر سیستم‌عامل بدون اجرای بیلد:
.venv/bin/python scripts/build_app.py --platform windows --dry-run
.venv/bin/python scripts/build_app.py --platform macos --dry-run
.venv/bin/python scripts/build_app.py --platform linux --dry-run
```

### خودکارسازی با GitHub Actions (CI/CD)
- **ورک‌فلو [`ci.yml`](.github/workflows/ci.yml):** اجرای `compileall`، تمام تست‌های `pytest` روی پایتون `3.11`، `3.12` و `3.13` و سپس ساخت و تست هم‌زمان بسته مستقل روی سه رانر **`ubuntu-latest`**، **`windows-latest`** و **`macos-latest`**.
- **ورک‌فلو [`release.yml`](.github/workflows/release.yml):** با ثبت هر تگ `v*`، بسته‌های **Linux**، **Windows**، **macOS**، **Python Wheel (`.whl`)**، سورس **`.tar.gz`** و فایل **`SHA256SUMS.txt`** را خودکار در GitHub Releases منتشر می‌کند.

---

## ساختار معماری پروژه

```text
PipeOra/
├── app/
│   ├── core/
│   │   ├── audio_manager.py       # مدیریت سینک‌های خروجی، ولوم و استریم‌های صوتی (pactl)
│   │   ├── profile_manager.py     # کنترل پروفایل A2DP/HFP و تنظیم WirePlumber autoswitch
│   │   ├── bluetooth_manager.py   # ارتباط D-Bus با org.bluez و کنترل دستگاه‌ها
│   │   ├── config_manager.py      # ذخیره تنظیمات کاربر در ~/.config/pipeora/config.json
│   │   ├── system_detector.py     # تشخیص وضعیت سرویس‌های PipeWire، WirePlumber و BlueZ
│   │   └── paths.py               # حل مسیر منابع در سورس و بسته‌های PyInstaller
│   ├── models/                    # مدل‌های داده خروجی صوتی و دستگاه بلوتوث
│   ├── services/
│   │   ├── event_worker.py        # شنود زنده غیربلاکینگ با pactl subscribe و selectors
│   │   └── autostart_service.py   # مدیریت فایل XDG Autostart
│   ├── resources/icons/           # آیکون‌های برداری SVG اختصاصی
│   └── ui/
│       ├── main_window.py         # پنجره اصلی، ناوبری و هماهنگی رویدادها
│       ├── dashboard_page.py      # داشبورد زنده، کارت Hero، حالت هدست و سوئیچ سریع
│       ├── devices_page.py        # فهرست خروجی‌ها و میکسر مستقل برنامه‌ها
│       ├── bluetooth_page.py      # مدیریت، اسکن و انتخاب هدست محبوب بلوتوث
│       ├── settings_page.py       # تنظیمات رفتار هدست، دسکتاپ و سلامت سرویس‌ها
│       ├── about_page.py          # معرفی نسخه و توسعه‌دهنده
│       ├── tray_icon.py           # آیکون و منوی سینی سیستم
│       └── components/            # ویجت‌های اختصاصی (HeadsetModeCard, VolumeSlider, ...)
├── packaging/                     # فایل‌های PKGBUILD، .desktop، آیکون SVG، PNGها و .ico
├── scripts/
│   └── build_app.py               # اسکریپت رسمی بیلد مستقل برای Linux / Windows / macOS
├── tests/                         # تست‌های واحد pytest و اسکریپت اعتبارسنجی سیستم زنده
└── run.sh                         # راه‌انداز سریع محیط توسعه
```

---

## اجرای تست‌ها و اعتبارسنجی

```bash
# اجرای تمام تست‌های واحد در حالت Offscreen Qt
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/ -v

# اجرای تست‌های واحد + بررسی زنده سرویس‌های PipeWire/WirePlumber/BlueZ روی سیستم لینوکس
.venv/bin/python tests/run_all_tests.py
```

---

## توسعه‌دهنده و مجوز

- **توسعه‌دهنده:** امیرعلی همایونزاده (Amirali Homayoonzadeh)
- **وب‌سایت:** [amirprgrmr.ir](https://amirprgrmr.ir)
- **تلگرام:** [t.me/Amirprgrmr](https://t.me/Amirprgrmr)
- **مجوز انتشار:** [MIT License](LICENSE)

</div>

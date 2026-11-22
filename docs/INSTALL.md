# راهنمای نصب و راه‌اندازی AM Audio Control
## راهنمای جامع برای توزیع‌های Parch Linux و Arch Linux

---

## ۱. پیش‌نیازهای سیستمی

این نرم‌افزار به صورت اختصاصی برای لینوکس با زیرساخت صوتی مدرن توسعه یافته است:

- سیستم‌عامل: **Parch Linux** یا **Arch Linux** (یا سایر توزیع‌های مبتنی بر آرچ)
- زیرساخت صوتی: **PipeWire** و **WirePlumber**
- لایه سازگاری: **pipewire-pulse**
- زیرسیستم بلوتوث: **BlueZ**
- پایتون: نسخه **3.11** یا بالاتر (تست‌شده روی Python 3.14)
- فریم‌ورک رابط کاربری: **PySide6 (Qt 6)**

### بررسی وضعیت سرویس‌ها قبل از نصب:
```bash
# بررسی وضعیت فعال بودن پایپ‌وایر
systemctl --user is-active pipewire wireplumber pipewire-pulse

# بررسی فعال بودن بلوتوث
systemctl is-active bluetooth
```

اگر هر یک از سرویس‌ها فعال نبودند، می‌توانید با دستورات زیر آن‌ها را فعال کنید:
```bash
# فعال‌سازی پایپ‌وایر
systemctl --user enable --now pipewire wireplumber pipewire-pulse

# فعال‌سازی بلوتوث
sudo systemctl enable --now bluetooth
```

---

## ۲. روش اول: اجرای مستقیم و توسعه (پیشنهادی برای توسعه)

نرم‌افزار مجهز به اسکریپت راه‌اندازی خودکار `run.sh` است که از ابزار پرسرعت `uv` یا `venv` پایتون استفاده می‌کند بدون اینکه فایل‌های سیستمی دستکاری شوند (سازگار با سیاست PEP 668 در آرچ):

```bash
# رفتن به دایرکتوری پروژه
cd PipeOra

# اعطای دسترسی به اسکریپت
chmod +x run.sh

# اجرای برنامه
./run.sh
```

برای اجرای مستقیم در پس‌زمینه (حالت سینی سیستم):
```bash
./run.sh --minimized
```

---

## ۳. روش دوم: ساخت و نصب بسته رسمی Pacman (PKGBUILD)

برای نصب کامل نرم‌افزار در سطح سیستم و یکپارچه‌شدن با منوی برنامه‌های KDE Plasma:

```bash
# رفتن به پوشه بسته‌بندی
cd PipeOra/packaging

# نصب وابستگی‌های ساخت پکیج آرچ (در صورت نیاز)
sudo pacman -S --needed base-devel git python-build python-installer python-wheel

# ساخت بسته با makepkg
makepkg -si
```

پس از اتمام، برنامه در منوی استارت دسکتاپ (KDE Launcher) با نام **مدیریت صدای AM** ظاهر خواهد شد و با دستور خط فرمان زیر نیز قابل اجراست:
```bash
am-audio-control
```

---

## ۴. روش فعال‌سازی اجرای خودکار (Autostart)

۱. وارد صفحه **تنظیمات** برنامه شوید.
۲. گزینه **«اجرای خودکار برنامه هنگام ورود به سیستم»** را فعال کنید.

یا به صورت دستی با قرار دادن فایل در دایرکتوری autostart:
```bash
mkdir -p ~/.config/autostart
cp packaging/am-audio-control.desktop ~/.config/autostart/
```

---

## ۵. روش حذف کامل (Uninstallation)

### در صورت نصب با Pacman:
```bash
sudo pacman -R am-audio-control
```

### حذف فایل‌های تنظیمات و کش برنامه:
```bash
# حذف فایل کانفیگ اختصاصی
rm -rf ~/.config/am-audio-control

# حذف فایل اجرای خودکار
rm -f ~/.config/autostart/am-audio-control.desktop

# حذف محیط مجازی توسعه (در صورت وجود)
rm -rf PipeOra/.venv
```

---

## ۶. عیب‌یابی (Troubleshooting)

### مشکل ۱: پنجره برنامه باز نمی‌شود ولی در پردازش‌ها هست
برنامه دارای مکانیزم تک‌نسخه‌ای (Single Instance) است. اگر نسخه قبلی در پس‌زمینه یا سینی سیستم فعال است، کافی است روی آیکون آن در System Tray کلیک کنید یا دستور زیر را بزنید تا پنجره فعال شود:
```bash
am-audio-control
```

### مشکل ۲: هدفون بلوتوث در لیست نشان داده نمی‌شود
ابتدا مطمئن شوید هدفون با سیستم جفت (Paired) شده است:
```bash
bluetoothctl devices
```
اگر هدفون در لیست نیست، آن را در حالت Pairing قرار داده و از صفحه «مدیریت بلوتوث» یا ابزار سیستم جفت کنید.

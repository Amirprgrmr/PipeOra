"""
صفحه درباره برنامه (AboutPage)
معرفی پروژه AM Audio Control، شناسنامه مهندسی، توسعه‌دهنده و فناوری‌های لینوکس
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QPushButton
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

from app.ui.styles.icon_helper import IconHelper


class AboutPage(QWidget):
    """صفحه درباره ما و معرفی اختصاصی پروژه."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(20)
        container_layout.setAlignment(Qt.AlignTop)

        # کارت اصلی مشخصات برنامه
        card_main = QFrame()
        card_main.setProperty("card", "true")
        card_layout = QVBoxLayout(card_main)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(16)
        card_layout.setAlignment(Qt.AlignCenter)

        # لوگوی برنامه با وکتور SVG باکیفیت
        lbl_logo = QLabel()
        lbl_logo.setFixedSize(72, 72)
        lbl_logo.setAlignment(Qt.AlignCenter)
        lbl_logo.setPixmap(IconHelper.get_pixmap("headphones", 40))
        lbl_logo.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(103, 201, 243, 0.2), stop:1 rgba(85, 207, 160, 0.2));
                border: 2px solid #67C9F3;
                border-radius: 36px;
                padding: 12px;
            }
        """)
        card_layout.addWidget(lbl_logo, 0, Qt.AlignCenter)

        # نام و نسخه
        lbl_app_name = QLabel("AM Audio Control")
        lbl_app_name.setStyleSheet("font-size: 22px; font-weight: bold; color: #F2F4F8;")
        card_layout.addWidget(lbl_app_name, 0, Qt.AlignCenter)

        lbl_persian_name = QLabel("مدیریت صدای AM | نسخه ۱.۰.۰")
        lbl_persian_name.setStyleSheet("font-size: 14px; font-weight: 600; color: #67C9F3;")
        card_layout.addWidget(lbl_persian_name, 0, Qt.AlignCenter)

        lbl_desc = QLabel(
            "نرم‌افزار دسکتاپ بومی و اختصاصی مدیریت خروجی صدا و تجهیزات صوتی بلوتوث برای لینوکس.\n"
            "طراحی‌شده اختصاصی برای توزیع Parch Linux و Arch Linux در محیط KDE Plasma (Wayland)."
        )
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setStyleSheet("color: #A6AFBD; font-size: 13px; line-height: 1.6;")
        card_layout.addWidget(lbl_desc, 0, Qt.AlignCenter)

        container_layout.addWidget(card_main)

        # کارت مشخصات سازنده و توسعه‌دهنده
        card_dev = QFrame()
        card_dev.setProperty("card", "true")
        dev_layout = QVBoxLayout(card_dev)
        dev_layout.setContentsMargins(20, 20, 20, 20)
        dev_layout.setSpacing(12)

        lbl_dev_title = QLabel("توسعه‌دهنده و مهندسی نرم‌افزار")
        lbl_dev_title.setObjectName("sectionTitle")
        dev_layout.addWidget(lbl_dev_title)

        lbl_author = QLabel("امیرعلی همایونزاده | Amirali Homayoonzadeh (amirprgrmr)")
        lbl_author.setStyleSheet("color: #F2F4F8; font-size: 14px; font-weight: bold;")
        dev_layout.addWidget(lbl_author)

        lbl_role = QLabel("Software Engineer & Linux Desktop Developer")
        lbl_role.setObjectName("mutedText")
        dev_layout.addWidget(lbl_role)

        # لینک‌های ارتباطی
        links_layout = QHBoxLayout()
        links_layout.setSpacing(12)

        btn_site = QPushButton("وب‌سایت شخصی (amirprgrmr.ir)")
        btn_site.setProperty("primary", "true")
        btn_site.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://amirprgrmr.ir")))
        links_layout.addWidget(btn_site)

        btn_tg = QPushButton("کانال / ارتباط تلگرام")
        btn_tg.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://t.me/Amirprgrmr")))
        links_layout.addWidget(btn_tg)

        links_layout.addStretch()
        dev_layout.addLayout(links_layout)

        container_layout.addWidget(card_dev)

        # کارت استک و زیرساخت فنی
        card_stack = QFrame()
        card_stack.setProperty("card", "true")
        stack_layout = QVBoxLayout(card_stack)
        stack_layout.setContentsMargins(20, 20, 20, 20)
        stack_layout.setSpacing(10)

        lbl_stack_title = QLabel("پشته فناوری و زیرساخت")
        lbl_stack_title.setObjectName("sectionTitle")
        stack_layout.addWidget(lbl_stack_title)

        tech_text = (
            "• زبان و فریم‌ورک: Python 3.14 + PySide6 (Qt 6.12+)\n"
            "• مدیریت صوت: PipeWire 1.6+ & WirePlumber Session Manager\n"
            "• مدیریت بلوتوث: BlueZ D-Bus Interface (org.bluez)\n"
            "• پلتفرم هدف: Parch Linux / Arch Linux (KDE Plasma Wayland)\n"
            "• معماری: تفکیک ماژولار هسته و رابط کاربری، شنود زنده رویدادهای pactl subscribe\n"
            "• قانون محصول: حذف ۱۰۰٪ هرگونه ورودی و میکروفن، اولویت با کیفیت پخش استریو (A2DP)"
        )
        lbl_tech = QLabel(tech_text)
        lbl_tech.setStyleSheet("color: #A6AFBD; font-size: 12px; line-height: 1.8;")
        stack_layout.addWidget(lbl_tech)

        container_layout.addWidget(card_stack)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

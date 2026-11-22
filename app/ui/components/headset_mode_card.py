"""
کامپوننت اختصاصی سوئیچ حالت کاربری هدفون بلوتوث (HeadsetModeCard)
امکان انتخاب هوشمند میان کیفیت استریوی موسیقی (A2DP) و فعال‌سازی میکروفن مکالمه (HFP)
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)

from app.core.profile_manager import ProfileManager
from app.ui.styles.icon_helper import IconHelper
from app.ui.components.status_badge import StatusBadge


class HeadsetModeCard(QFrame):
    """کارت تعاملی دوگانه برای سوئیچ میان حالت موسیقی و مکالمه هدفون بلوتوث."""

    mode_changed = Signal(str)  # بازگرداندن 'a2dp' یا 'hfp'

    def __init__(self, profile_mgr: ProfileManager, parent=None):
        super().__init__(parent)
        self.profile_mgr = profile_mgr
        self._card_id: Optional[str] = None
        self._current_mode = "a2dp"

        self.setProperty("card", "true")
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(14)

        # عنوان و توضیحات هدر کارت
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(2)

        lbl_title = QLabel("حالت کاربری هدفون و میکروفن (Headset Profile)")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #F2F4F8;")
        header_text.addWidget(lbl_title)

        lbl_desc = QLabel("انتخاب آگاهانه میان بالاترین کیفیت پخش موسیقی یا فعال‌سازی میکروفن هدفون برای تماس")
        lbl_desc.setStyleSheet("color: #A6AFBD; font-size: 11px;")
        header_text.addWidget(lbl_desc)

        header_layout.addLayout(header_text)
        header_layout.addStretch()

        self.badge_active = StatusBadge("کیفیت استریو A2DP", variant="success")
        header_layout.addWidget(self.badge_active)
        main_layout.addLayout(header_layout)

        # ردیف کارت‌های گزینشی
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)

        # ------------------ کارت ۱: حالت استریو A2DP (موسیقی) ------------------
        self.frame_a2dp = QFrame()
        self.frame_a2dp.setCursor(Qt.PointingHandCursor)
        self.frame_a2dp.setStyleSheet("""
            QFrame {
                background-color: #222936;
                border: 2px solid #2D3545;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        a2dp_layout = QVBoxLayout(self.frame_a2dp)
        a2dp_layout.setSpacing(8)

        a2dp_top = QHBoxLayout()
        lbl_a2dp_icon = QLabel()
        lbl_a2dp_icon.setPixmap(IconHelper.get_pixmap("headphones", 26))
        a2dp_top.addWidget(lbl_a2dp_icon)

        lbl_a2dp_title = QLabel("حالت موسیقی و فیلم (A2DP)")
        lbl_a2dp_title.setStyleSheet("font-weight: bold; color: #F2F4F8; font-size: 13px;")
        a2dp_top.addWidget(lbl_a2dp_title)
        a2dp_top.addStretch()

        self.badge_a2dp_state = StatusBadge("فعال", variant="success")
        a2dp_top.addWidget(self.badge_a2dp_state)
        a2dp_layout.addLayout(a2dp_top)

        lbl_a2dp_detail = QLabel(
            "• کیفیت استریوی فوق‌العاده با کدک AAC / SBC\n"
            "• میکروفن هدفون خاموش (استفاده از میکروفن داخلی لپ‌تاپ)"
        )
        lbl_a2dp_detail.setStyleSheet("color: #A6AFBD; font-size: 11px; line-height: 1.5;")
        a2dp_layout.addWidget(lbl_a2dp_detail)

        self.btn_select_a2dp = QPushButton("انتخاب حالت موسیقی")
        self.btn_select_a2dp.setProperty("primary", "true")
        self.btn_select_a2dp.clicked.connect(lambda: self._select_mode("a2dp"))
        a2dp_layout.addWidget(self.btn_select_a2dp)

        cards_layout.addWidget(self.frame_a2dp, 1)

        # ------------------ کارت ۲: حالت مکالمه HFP (میکروفن هدفون) ------------------
        self.frame_hfp = QFrame()
        self.frame_hfp.setCursor(Qt.PointingHandCursor)
        self.frame_hfp.setStyleSheet("""
            QFrame {
                background-color: #222936;
                border: 2px solid #2D3545;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        hfp_layout = QVBoxLayout(self.frame_hfp)
        hfp_layout.setSpacing(8)

        hfp_top = QHBoxLayout()
        lbl_hfp_icon = QLabel()
        lbl_hfp_icon.setPixmap(IconHelper.get_pixmap("headset-mic", 26))
        hfp_top.addWidget(lbl_hfp_icon)

        lbl_hfp_title = QLabel("حالت مکالمه و تماس (HFP)")
        lbl_hfp_title.setStyleSheet("font-weight: bold; color: #F2F4F8; font-size: 13px;")
        hfp_top.addWidget(lbl_hfp_title)
        hfp_top.addStretch()

        self.badge_hfp_state = StatusBadge("غیرفعال", variant="neutral")
        hfp_top.addWidget(self.badge_hfp_state)
        hfp_layout.addLayout(hfp_top)

        lbl_hfp_detail = QLabel(
            "• فعال‌سازی کامل میکروفن هدفون برای جلسات و تماس\n"
            "• خروجی صدا به کیفیت مکالمه (مونو فرکانس پایین) تبدیل می‌شود"
        )
        lbl_hfp_detail.setStyleSheet("color: #A6AFBD; font-size: 11px; line-height: 1.5;")
        hfp_layout.addWidget(lbl_hfp_detail)

        self.btn_select_hfp = QPushButton("فعال‌سازی میکروفن و تماس")
        self.btn_select_hfp.clicked.connect(lambda: self._select_mode("hfp"))
        hfp_layout.addWidget(self.btn_select_hfp)

        cards_layout.addWidget(self.frame_hfp, 1)

        main_layout.addLayout(cards_layout)

        # پیام راهنمای پایین کارت
        self.lbl_notice = QLabel()
        self.lbl_notice.setWordWrap(True)
        self.lbl_notice.setStyleSheet("""
            QLabel {
                background-color: rgba(25, 30, 39, 0.7);
                border: 1px dashed #3B4559;
                border-radius: 6px;
                padding: 8px 12px;
                color: #A6AFBD;
                font-size: 11px;
            }
        """)
        main_layout.addWidget(self.lbl_notice)

    def set_target_card(self, card_id: Optional[str]):
        """تنظیم شناسه کارت بلوتوث و به‌روزرسانی حالت."""
        self._card_id = card_id
        if not card_id or not self.profile_mgr.has_headset_modes(card_id):
            self.setVisible(False)
            return

        self.setVisible(True)
        mode = self.profile_mgr.get_headset_mode(card_id)
        self._update_ui_state(mode)

    def _update_ui_state(self, mode: str):
        """به‌روزرسانی استایل و برچسب‌های وضعیت بر اساس حالت فعال."""
        self._current_mode = mode

        if mode == "a2dp":
            self.badge_active.set_variant("success", "کیفیت استریو A2DP (میکروفن خاموش)")
            self.badge_a2dp_state.set_variant("success", "فعال")
            self.badge_hfp_state.set_variant("neutral", "غیرفعال")

            self.frame_a2dp.setStyleSheet("""
                QFrame {
                    background-color: rgba(103, 201, 243, 0.08);
                    border: 2px solid #67C9F3;
                    border-radius: 10px;
                    padding: 12px;
                }
            """)
            self.frame_hfp.setStyleSheet("""
                QFrame {
                    background-color: #222936;
                    border: 2px solid #2D3545;
                    border-radius: 10px;
                    padding: 12px;
                }
            """)

            self.btn_select_a2dp.setText("حالت فعال")
            self.btn_select_a2dp.setEnabled(False)
            self.btn_select_hfp.setText("فعال‌سازی میکروفن و تماس")
            self.btn_select_hfp.setEnabled(True)

            self.lbl_notice.setText("💡 کیفیت پخش استریوی ۴۸ کیلوهرتز فعال است. ورودی سیستم به صورت خودکار به میکروفن داخلی لپ‌تاپ منتقل شده تا پخش موسیقی بدون پرش و با بالاترین کیفیت پایدار بماند.")

        elif mode == "hfp":
            self.badge_active.set_variant("warning", "حالت مکالمه HFP (میکروفن فعال)")
            self.badge_a2dp_state.set_variant("neutral", "غیرفعال")
            self.badge_hfp_state.set_variant("warning", "فعال")

            self.frame_hfp.setStyleSheet("""
                QFrame {
                    background-color: rgba(233, 185, 110, 0.08);
                    border: 2px solid #E9B96E;
                    border-radius: 10px;
                    padding: 12px;
                }
            """)
            self.frame_a2dp.setStyleSheet("""
                QFrame {
                    background-color: #222936;
                    border: 2px solid #2D3545;
                    border-radius: 10px;
                    padding: 12px;
                }
            """)

            self.btn_select_hfp.setText("حالت فعال")
            self.btn_select_hfp.setEnabled(False)
            self.btn_select_a2dp.setText("بازگشت به کیفیت عالی موسیقی")
            self.btn_select_a2dp.setEnabled(True)

            self.lbl_notice.setText("🎙️ میکروفن هدفون اکنون فعال و به عنوان ورودی اصلی سیستم و برنامه‌ها تنظیم شد. خروجی صدا موقتاً در حالت مکالمه قرار دارد و پس از پایان تماس می‌توانید به کیفیت استریو برگردید.")

    def _select_mode(self, mode: str):
        if not self._card_id:
            return

        # نمایش وضعیت گذار
        if mode == "a2dp":
            self.btn_select_a2dp.setText("در حال انتقال ورودی و سوییچ...")
        else:
            self.btn_select_hfp.setText("در حال فعال‌سازی میکروفن...")

        self.btn_select_a2dp.setEnabled(False)
        self.btn_select_hfp.setEnabled(False)

        success = self.profile_mgr.set_headset_mode(self._card_id, mode)
        if success:
            self._update_ui_state(mode)
            self.mode_changed.emit(mode)
        else:
            # بازیابی حالت قبلی در صورت بروز خطا
            current_mode = self.profile_mgr.get_headset_mode(self._card_id)
            self._update_ui_state(current_mode)

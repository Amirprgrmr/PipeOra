"""
کامپوننت اختصاصی سوئیچ حالت کاربری هدفون بلوتوث (HeadsetModeCard)
انتخاب هوشمند میان کیفیت استریوی موسیقی (A2DP) و فعال‌سازی میکروفن مکالمه (HFP)
با کنترل قفل دستی ضدپرش، پشتیبانی از تغییر خودکار WirePlumber و چیدمان بدون سرریز افقی
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QSizePolicy, QLayout
)

from app.core.profile_manager import ProfileManager
from app.core.config_manager import ConfigManager
from app.ui.styles.icon_helper import IconHelper
from app.ui.components.status_badge import StatusBadge


class HeadsetModeCard(QFrame):
    """کارت تعاملی دوگانه برای سوئیچ میان حالت موسیقی و مکالمه هدفون بلوتوث."""

    mode_changed = Signal(str)  # بازگرداندن 'a2dp' یا 'hfp'

    def __init__(
        self,
        profile_mgr: ProfileManager,
        config_mgr: Optional[ConfigManager] = None,
        parent=None
    ):
        super().__init__(parent)
        self.profile_mgr = profile_mgr
        self.config_mgr = config_mgr
        self._card_id: Optional[str] = None
        self._current_mode = "a2dp"
        self._rendered_mode: Optional[str] = None
        self._is_updating_toggle = False

        self.setProperty("card", "true")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSizeConstraint(QLayout.SetMinimumSize)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(14)

        # عنوان و وضعیت فعال کارت
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        header_text = QVBoxLayout()
        header_text.setSpacing(3)

        lbl_title = QLabel("حالت کاربری هدفون و میکروفن (Headset Profile)")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #F2F4F8;")
        lbl_title.setWordWrap(True)
        header_text.addWidget(lbl_title)

        lbl_desc = QLabel("انتخاب دقیق بین کیفیت استریو موسیقی (میکروفن لپ‌تاپ) یا فعال‌سازی میکروفن هدفون")
        lbl_desc.setStyleSheet("color: #A6AFBD; font-size: 11px;")
        lbl_desc.setWordWrap(True)
        header_text.addWidget(lbl_desc)

        header_layout.addLayout(header_text, 1)

        self.badge_active = StatusBadge("کیفیت استریو A2DP", variant="success")
        header_layout.addWidget(self.badge_active, 0, Qt.AlignTop)
        main_layout.addLayout(header_layout)

        # ردیف دو کارت انتخابی با عرض متعادل بدون سرریز
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        # ------------------ کارت ۱: حالت استریو A2DP (موسیقی) ------------------
        self.frame_a2dp = QFrame()
        self.frame_a2dp.setObjectName("optionCardA2DP")
        self.frame_a2dp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.frame_a2dp.setMinimumHeight(152)
        a2dp_layout = QVBoxLayout(self.frame_a2dp)
        a2dp_layout.setContentsMargins(14, 14, 14, 14)
        a2dp_layout.setSpacing(10)

        a2dp_top = QHBoxLayout()
        a2dp_top.setSpacing(8)
        lbl_a2dp_icon = QLabel()
        lbl_a2dp_icon.setFixedSize(26, 26)
        lbl_a2dp_icon.setAlignment(Qt.AlignCenter)
        lbl_a2dp_icon.setPixmap(IconHelper.get_pixmap("headphones", 22))
        a2dp_top.addWidget(lbl_a2dp_icon)

        lbl_a2dp_title = QLabel("موسیقی و فیلم (A2DP)")
        lbl_a2dp_title.setStyleSheet("font-weight: bold; color: #F2F4F8; font-size: 13px;")
        lbl_a2dp_title.setWordWrap(True)
        a2dp_top.addWidget(lbl_a2dp_title, 1)

        self.badge_a2dp_state = StatusBadge("فعال", variant="success")
        a2dp_top.addWidget(self.badge_a2dp_state)
        a2dp_layout.addLayout(a2dp_top)

        lbl_a2dp_detail = QLabel(
            "• پخش استریو ۴۸ کیلوهرتز با کدک AAC/SBC\n"
            "• میکروفن هدفون خاموش (استفاده از میکروفن لپ‌تاپ)"
        )
        lbl_a2dp_detail.setStyleSheet("color: #A6AFBD; font-size: 11px;")
        lbl_a2dp_detail.setWordWrap(True)
        a2dp_layout.addWidget(lbl_a2dp_detail)
        a2dp_layout.addStretch(1)

        self.btn_select_a2dp = QPushButton("انتخاب حالت موسیقی")
        self.btn_select_a2dp.setCursor(Qt.PointingHandCursor)
        self.btn_select_a2dp.setMinimumHeight(36)
        self.btn_select_a2dp.setProperty("primary", "true")
        self.btn_select_a2dp.clicked.connect(lambda: self._select_mode("a2dp"))
        a2dp_layout.addWidget(self.btn_select_a2dp)

        cards_layout.addWidget(self.frame_a2dp, 1)

        # ------------------ کارت ۲: حالت مکالمه HFP (میکروفن هدفون) ------------------
        self.frame_hfp = QFrame()
        self.frame_hfp.setObjectName("optionCardHFP")
        self.frame_hfp.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.frame_hfp.setMinimumHeight(152)
        hfp_layout = QVBoxLayout(self.frame_hfp)
        hfp_layout.setContentsMargins(14, 14, 14, 14)
        hfp_layout.setSpacing(10)

        hfp_top = QHBoxLayout()
        hfp_top.setSpacing(8)
        lbl_hfp_icon = QLabel()
        lbl_hfp_icon.setFixedSize(26, 26)
        lbl_hfp_icon.setAlignment(Qt.AlignCenter)
        lbl_hfp_icon.setPixmap(IconHelper.get_pixmap("headset-mic", 22))
        hfp_top.addWidget(lbl_hfp_icon)

        lbl_hfp_title = QLabel("مکالمه و تماس (HFP)")
        lbl_hfp_title.setStyleSheet("font-weight: bold; color: #F2F4F8; font-size: 13px;")
        lbl_hfp_title.setWordWrap(True)
        hfp_top.addWidget(lbl_hfp_title, 1)

        self.badge_hfp_state = StatusBadge("غیرفعال", variant="neutral")
        hfp_top.addWidget(self.badge_hfp_state)
        hfp_layout.addLayout(hfp_top)

        lbl_hfp_detail = QLabel(
            "• فعال‌سازی کامل میکروفن هدفون برای جلسات و تماس\n"
            "• صدای خروجی مونو مکالمه (پهنای باند محدود)"
        )
        lbl_hfp_detail.setStyleSheet("color: #A6AFBD; font-size: 11px;")
        lbl_hfp_detail.setWordWrap(True)
        hfp_layout.addWidget(lbl_hfp_detail)
        hfp_layout.addStretch(1)

        self.btn_select_hfp = QPushButton("فعال‌سازی میکروفن و تماس")
        self.btn_select_hfp.setCursor(Qt.PointingHandCursor)
        self.btn_select_hfp.setMinimumHeight(36)
        self.btn_select_hfp.clicked.connect(lambda: self._select_mode("hfp"))
        hfp_layout.addWidget(self.btn_select_hfp)

        cards_layout.addWidget(self.frame_hfp, 1)

        main_layout.addLayout(cards_layout)

        # نوار تنظیم سوییچ خودکار هوشمند سیستم
        auto_bar = QFrame()
        auto_bar.setObjectName("autoSwitchBar")
        auto_bar.setStyleSheet("""
            QFrame#autoSwitchBar {
                background-color: #202734;
                border: 1px solid #2D3545;
                border-radius: 8px;
            }
        """)
        auto_layout = QHBoxLayout(auto_bar)
        auto_layout.setContentsMargins(12, 8, 12, 8)
        auto_layout.setSpacing(10)

        lbl_auto_icon = QLabel()
        lbl_auto_icon.setFixedSize(20, 20)
        lbl_auto_icon.setPixmap(IconHelper.get_pixmap("auto-switch", 16))
        auto_layout.addWidget(lbl_auto_icon)

        self.chk_auto_switch = QCheckBox("تغییر خودکار هوشمند هنگام شروع مکالمه (WirePlumber Auto)")
        self.chk_auto_switch.setCursor(Qt.PointingHandCursor)
        self.chk_auto_switch.setToolTip(
            "در صورت فعال بودن، هنگام استفاده برنامه‌ها از میکروفن خودکار به HFP می‌رود و ۴ ثانیه بعد به A2DP برمی‌گردد.\n"
            "در حالت غیرفعال (قفل دستی)، انتخاب شما ثابت می‌ماند و هرگز بعد از چند ثانیه نمی‌پرد."
        )
        if self.config_mgr:
            self.chk_auto_switch.setChecked(self.config_mgr.is_headset_auto_switch_enabled())
        self.chk_auto_switch.toggled.connect(self._on_auto_switch_toggled)
        auto_layout.addWidget(self.chk_auto_switch, 1)

        self.badge_lock = StatusBadge("قفل دستی پایدار", variant="primary")
        auto_layout.addWidget(self.badge_lock)

        main_layout.addWidget(auto_bar)

        # پیام راهنمای پایین کارت با آیکون وکتور (بدون ایموجی)
        notice_frame = QFrame()
        notice_frame.setObjectName("noticeBanner")
        notice_frame.setStyleSheet("""
            QFrame#noticeBanner {
                background-color: rgba(25, 30, 39, 0.75);
                border: 1px dashed #3B4559;
                border-radius: 8px;
            }
        """)
        notice_layout = QHBoxLayout(notice_frame)
        notice_layout.setContentsMargins(12, 8, 12, 8)
        notice_layout.setSpacing(10)

        self.lbl_notice_icon = QLabel()
        self.lbl_notice_icon.setFixedSize(18, 18)
        self.lbl_notice_icon.setPixmap(IconHelper.get_pixmap("info-circle", 16))
        notice_layout.addWidget(self.lbl_notice_icon, 0, Qt.AlignTop)

        self.lbl_notice = QLabel()
        self.lbl_notice.setWordWrap(True)
        self.lbl_notice.setStyleSheet("color: #A6AFBD; font-size: 11px;")
        notice_layout.addWidget(self.lbl_notice, 1)

        main_layout.addWidget(notice_frame)

    def set_target_card(self, card_id: Optional[str]):
        """تنظیم شناسه کارت بلوتوث و به‌روزرسانی حالت در یک فراخوانی بهینه."""
        self._card_id = card_id
        if not card_id:
            self.setVisible(False)
            return

        has_modes, mode = self.profile_mgr.get_headset_status(card_id)
        if not has_modes:
            self.setVisible(False)
            return

        self.setVisible(True)
        self._sync_auto_switch_indicator()
        self._update_ui_state(mode)

    def _sync_auto_switch_indicator(self):
        wp_auto = self.profile_mgr.get_wireplumber_autoswitch()
        if wp_auto is None and self.config_mgr:
            wp_auto = self.config_mgr.is_headset_auto_switch_enabled()
        elif wp_auto is None:
            wp_auto = False

        self._is_updating_toggle = True
        try:
            self.chk_auto_switch.setChecked(bool(wp_auto))
            if wp_auto:
                self.badge_lock.set_variant("warning", "هوشمند خودکار")
            else:
                self.badge_lock.set_variant("primary", "قفل دستی پایدار")
        finally:
            self._is_updating_toggle = False

    def _update_ui_state(self, mode: str):
        """به‌روزرسانی استایل، دکمه‌ها و برچسب‌های وضعیت بر اساس حالت فعال."""
        self._current_mode = mode
        if self._rendered_mode == mode:
            return
        self._rendered_mode = mode

        if mode == "a2dp":
            self.badge_active.set_variant("success", "استریو A2DP (میکروفن خاموش)")
            self.badge_a2dp_state.set_variant("success", "فعال")
            self.badge_hfp_state.set_variant("neutral", "غیرفعال")

            self.frame_a2dp.setStyleSheet("""
                QFrame#optionCardA2DP {
                    background-color: rgba(103, 201, 243, 0.08);
                    border: 2px solid #67C9F3;
                    border-radius: 10px;
                }
            """)
            self.frame_hfp.setStyleSheet("""
                QFrame#optionCardHFP {
                    background-color: #222936;
                    border: 1px solid #2D3545;
                    border-radius: 10px;
                }
            """)

            self.btn_select_a2dp.setText("حالت فعال")
            self.btn_select_a2dp.setProperty("primary", "false")
            self.btn_select_a2dp.setEnabled(False)

            self.btn_select_hfp.setText("فعال‌سازی میکروفن و تماس")
            self.btn_select_hfp.setProperty("primary", "true")
            self.btn_select_hfp.setEnabled(True)

            self.lbl_notice_icon.setPixmap(IconHelper.get_pixmap("info-circle", 16))
            self.lbl_notice.setText(
                "کیفیت پخش استریو ۴۸ کیلوهرتز فعال است و ورودی سیستم به میکروفن داخلی لپ‌تاپ منتقل شده تا پخش موسیقی بدون افت کیفیت پایدار بماند."
            )

        elif mode == "hfp":
            self.badge_active.set_variant("warning", "مکالمه HFP (میکروفن فعال)")
            self.badge_a2dp_state.set_variant("neutral", "غیرفعال")
            self.badge_hfp_state.set_variant("warning", "فعال")

            self.frame_hfp.setStyleSheet("""
                QFrame#optionCardHFP {
                    background-color: rgba(233, 185, 110, 0.09);
                    border: 2px solid #E9B96E;
                    border-radius: 10px;
                }
            """)
            self.frame_a2dp.setStyleSheet("""
                QFrame#optionCardA2DP {
                    background-color: #222936;
                    border: 1px solid #2D3545;
                    border-radius: 10px;
                }
            """)

            self.btn_select_hfp.setText("حالت فعال")
            self.btn_select_hfp.setProperty("primary", "false")
            self.btn_select_hfp.setEnabled(False)

            self.btn_select_a2dp.setText("بازگشت به کیفیت عالی موسیقی")
            self.btn_select_a2dp.setProperty("primary", "true")
            self.btn_select_a2dp.setEnabled(True)

            self.lbl_notice_icon.setPixmap(IconHelper.get_pixmap("mic-on", 16))
            self.lbl_notice.setText(
                "میکروفن هدفون فعال و به‌عنوان ورودی اصلی سیستم تنظیم شد. خروجی صدا موقتاً در حالت مکالمه مونو قرار دارد؛ پس از تماس می‌توانید به کیفیت استریو بازگردید."
            )

        for btn in (self.btn_select_a2dp, self.btn_select_hfp):
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _on_auto_switch_toggled(self, checked: bool):
        if self._is_updating_toggle:
            return
        if self.config_mgr:
            self.config_mgr.set_headset_auto_switch_enabled(checked)
        self.profile_mgr.set_wireplumber_autoswitch(checked)
        self._sync_auto_switch_indicator()
        if self._card_id:
            self.mode_changed.emit(self.profile_mgr.get_headset_mode(self._card_id))

    def _select_mode(self, mode: str):
        if not self._card_id:
            return

        if mode == "a2dp":
            self.btn_select_a2dp.setText("در حال انتقال به حالت موسیقی...")
        else:
            self.btn_select_hfp.setText("در حال فعال‌سازی میکروفن...")

        self.btn_select_a2dp.setEnabled(False)
        self.btn_select_hfp.setEnabled(False)

        # انتخاب دستی قفل حالت را اعمال می‌کند تا WirePlumber بعد از ۴ ثانیه پروفایل را نپراند
        success = self.profile_mgr.set_headset_mode(self._card_id, mode, disable_autoswitch=True)
        if success and self.config_mgr:
            self.config_mgr.set_headset_auto_switch_enabled(False)

        actual_mode = self.profile_mgr.get_headset_mode(self._card_id)
        self._sync_auto_switch_indicator()
        self._rendered_mode = None
        self._update_ui_state(actual_mode if actual_mode in ("a2dp", "hfp") else mode)
        if success:
            self.mode_changed.emit(actual_mode)

"""
کامپوننت برچسب وضعیت فشرده (StatusBadge)
با طراحی مینیمال و رنگ‌های معنایی Graphite Dark
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel


class StatusBadge(QLabel):
    """برچسب وضعیت کپسولی با نشانگر رنگی."""

    VARIANT_STYLES = {
        "success": {
            "bg": "rgba(85, 207, 160, 0.15)",
            "color": "#55CFA0",
            "border": "1px solid rgba(85, 207, 160, 0.35)",
        },
        "primary": {
            "bg": "rgba(103, 201, 243, 0.15)",
            "color": "#67C9F3",
            "border": "1px solid rgba(103, 201, 243, 0.35)",
        },
        "warning": {
            "bg": "rgba(233, 185, 110, 0.15)",
            "color": "#E9B96E",
            "border": "1px solid rgba(233, 185, 110, 0.35)",
        },
        "error": {
            "bg": "rgba(235, 119, 119, 0.15)",
            "color": "#EB7777",
            "border": "1px solid rgba(235, 119, 119, 0.35)",
        },
        "neutral": {
            "bg": "rgba(166, 175, 189, 0.12)",
            "color": "#A6AFBD",
            "border": "1px solid #2D3545",
        }
    }

    def __init__(self, text: str = "", variant: str = "neutral", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.set_variant(variant, text)

    def set_variant(self, variant: str, text: str = ""):
        """تغییر نوع و رنگ‌بندی برچسب."""
        if text:
            self.setText(text)
        style_info = self.VARIANT_STYLES.get(variant, self.VARIANT_STYLES["neutral"])
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {style_info['bg']};
                color: {style_info['color']};
                border: {style_info['border']};
                border-radius: 10px;
                padding: 3px 10px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)

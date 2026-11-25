"""
توابع کمکی مدیریت چیدمان و پاک‌سازی ایمن ویجت‌های Qt
"""

from PySide6.QtWidgets import QLayout


def clear_layout(layout: QLayout) -> None:
    """
    حذف بازگشتی تمام ویجت‌ها و زیرلایوت‌ها بدون باقی گذاشتن ویجت‌های یتیم در حافظه.
    """
    while layout.count():
        item = layout.takeAt(0)
        if item is None:
            continue
        widget = item.widget()
        if widget is not None:
            widget.hide()
            widget.setParent(None)
            widget.deleteLater()
        else:
            child_layout = item.layout()
            if child_layout is not None:
                clear_layout(child_layout)

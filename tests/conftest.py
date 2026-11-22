import os
import sys
from pathlib import Path

# استفاده از پلتفرم offscreen برای اجرای امن و ایزوله تست‌های رابط کاربری در محیط لینوکس
os.environ["QT_QPA_PLATFORM"] = "offscreen"

# افزودن مسیر ریشه پروژه به sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

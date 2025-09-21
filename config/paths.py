import os
import sys
import tempfile

if sys.platform.startswith("win"):
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TMP_ROOT = os.path.join(PROJECT_ROOT, "tmp")
else:
    # Linux / macOS 使用系統暫存目錄
    TMP_ROOT = tempfile.gettempdir()

# 日誌目錄
LOG_DIR = os.path.join(TMP_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# SQLite 資料庫
DB_PATH = os.path.join(TMP_ROOT, "land_bot_dashboard.sqlite")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 原始資料下載目錄
RAW_DATA_DIR = os.path.join(TMP_ROOT, "real_estate_raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# 舊資料備份目錄
OLD_DATA_DIR = os.path.join(TMP_ROOT, "real_estate_old")
os.makedirs(OLD_DATA_DIR, exist_ok=True)

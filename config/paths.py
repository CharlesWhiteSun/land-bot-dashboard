import os
import tempfile

# 全域可寫入根目錄
TMP_ROOT = tempfile.gettempdir()  # /tmp

# 日誌目錄
LOG_DIR = os.path.join(TMP_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# SQLite 資料庫
DB_PATH = os.path.join(TMP_ROOT, "land_bot_dashboard.sqlite")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ChromeDriver 安裝目錄
CHROMEDRIVER_DIR = os.path.join(TMP_ROOT, "chromedriver")
os.makedirs(CHROMEDRIVER_DIR, exist_ok=True)

# 原始資料下載目錄
RAW_DATA_DIR = os.path.join(TMP_ROOT, "real_estate_raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# 舊資料備份目錄
OLD_DATA_DIR = os.path.join(TMP_ROOT, "real_estate_old")
os.makedirs(OLD_DATA_DIR, exist_ok=True)

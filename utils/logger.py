import os
import logging
from datetime import datetime
import tempfile

# ===== 建立 logs 資料夾 =====
# 先嘗試在專案根目錄建立 logs
try:
    os.makedirs('logs', exist_ok=True)
    LOG_DIR = 'logs'
except PermissionError:
    # 如果沒有權限，改用 /tmp/logs
    LOG_DIR = os.path.join(tempfile.gettempdir(), 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)

# ===== 當日 log 檔名 =====
log_filename = os.path.join(LOG_DIR, f'log_{datetime.now().strftime("%Y-%m-%d")}.txt')

# ===== 建立 logger 實例 =====
logger = logging.getLogger("land_bot_dashboard_logger")
logger.setLevel(logging.DEBUG)

# ===== 建立 FileHandler =====
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# ===== 設定 log 格式 =====
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')
file_handler.setFormatter(formatter)

# ===== 確保不重複加入 handler =====
if not logger.hasHandlers():
    logger.addHandler(file_handler)

# ===== 封裝 log 函式 =====
def log_error(error_code: str, detail: str, trace_id: str = "") -> None:
    if trace_id:
        logger.error("TraceID=%s | ErrorCode=%s | Detail=%s", trace_id, error_code, detail, stacklevel=2)
    else:
        logger.error("ErrorCode=%s | Detail=%s", error_code, detail, stacklevel=2)

def log_warning(message: str) -> None:
    logger.warning(message, stacklevel=2)

def log_info(message: str) -> None:
    logger.info(message, stacklevel=2)

def log_debug(message: str) -> None:
    logger.debug(message, stacklevel=2)

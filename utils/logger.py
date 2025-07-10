import os
import logging
from datetime import datetime

# 建立 logs 資料夾
os.makedirs('logs', exist_ok=True)

# 當日 log 檔名
log_filename = os.path.join('logs', f'log_{datetime.now().strftime("%Y-%m-%d")}.txt')

# 建立 logger 實例
logger = logging.getLogger("land_bot_dashboard_logger")
logger.setLevel(logging.DEBUG)

# 建立 FileHandler
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 設定 log 格式
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')
file_handler.setFormatter(formatter)

# 確保不重複加入 handler
if not logger.hasHandlers():
    logger.addHandler(file_handler)

def log_error(error_code: str, detail: str, trace_id: str = "") -> None:
    if trace_id:
        logger.error("TraceID=%s | ErrorCode=%s | Detail=%s", trace_id, error_code, detail)
    else:
        logger.error("ErrorCode=%s | Detail=%s", error_code, detail)

def log_warning(message: str) -> None:
    logger.warning(message)

def log_info(message: str) -> None:
    logger.info(message)

def log_debug(message: str) -> None:
    logger.debug(message)
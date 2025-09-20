import os
import logging
from datetime import datetime
from config.paths import LOG_DIR

log_filename = os.path.join(LOG_DIR, f'log_{datetime.now().strftime("%Y-%m-%d")}.txt')

logger = logging.getLogger("land_bot_dashboard_logger")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')
file_handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(file_handler)

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

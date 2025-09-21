import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Tuple
from config.paths import RAW_DATA_DIR  # 使用全域可寫入資料夾

DATA_DIR = RAW_DATA_DIR
DATA_FILE = os.path.join(DATA_DIR, "latest_notice.json")
HASH_FILE = os.path.join(DATA_DIR, "latest_notice.hash")
INIT_FLAG_FILE = os.path.join(DATA_DIR, ".init_done")

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

# ===== 計算資料的 hash（避免重複寫入） =====
def calculate_data_hash(data: Dict) -> str:
    json_str = json.dumps(data, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(json_str.encode("utf-8")).hexdigest()

# ===== 檢查是否為系統首次啟動 =====
def is_first_time_startup() -> bool:
    return not os.path.exists(INIT_FLAG_FILE)

# ===== 標記已初始化 =====
def mark_initialized():
    with open(INIT_FLAG_FILE, "w", encoding="utf-8") as f:
        f.write(f"initialized at {datetime.now().isoformat()}")

# ===== 讀取之前的 hash 值 =====
def read_previous_hash() -> str:
    if not os.path.exists(HASH_FILE):
        return ""
    with open(HASH_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

# ===== 寫入目前的 hash 值 =====
def write_current_hash(hash_str: str):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        f.write(hash_str)

# ===== 儲存資料 =====
def save_data(data: Dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===== 核心邏輯：是否需要更新資料 =====
def check_data(new_data: Dict) -> Tuple[bool, bool, str]:
    """
    管理資料儲存與判斷是否更新。

    :param new_data: 新取得的資料 dict
    :return: Tuple[有最新資料, 要拉取歷史資料, 資訊文字]
    """
    new_hash = calculate_data_hash(new_data)

    if is_first_time_startup():
        ensure_data_dir()
        save_data(new_data)
        write_current_hash(new_hash)
        mark_initialized()
        return True, True, "系統首次啟動，需要初始化新及歷史資料"
    
    old_hash = read_previous_hash()

    if new_hash != old_hash:
        ensure_data_dir()
        save_data(new_data)
        write_current_hash(new_hash)
        return True, False, "只需更新新資料，不需拉取舊資料"

    return False, False, "無需更新"

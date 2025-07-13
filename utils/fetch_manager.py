import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Tuple

# 檔案位置設定
DATA_DIR = os.path.join("api", "data", "real_estate", "raw")
DATA_FILE = os.path.join(DATA_DIR, "fetch_options_route.json")
HASH_FILE = os.path.join(DATA_DIR, "fetch_options_route.hash")
INIT_FLAG_FILE = os.path.join(DATA_DIR, ".init_done")

# 確保資料夾存在
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

# 計算資料的 hash（避免重複寫入）
def calculate_data_hash(data: Dict) -> str:
    json_str = json.dumps(data, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(json_str.encode("utf-8")).hexdigest()

# 檢查是否為系統首次啟動
def is_first_time_startup() -> bool:
    return not os.path.exists(INIT_FLAG_FILE)

# 標記已初始化
def mark_initialized():
    with open(INIT_FLAG_FILE, "w", encoding="utf-8") as f:
        f.write(f"initialized at {datetime.now().isoformat()}")

# 讀取之前的 hash 值
def read_previous_hash() -> str:
    if not os.path.exists(HASH_FILE):
        return ""
    with open(HASH_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

# 寫入目前的 hash 值
def write_current_hash(hash_str: str):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        f.write(hash_str)

# 儲存資料
def save_data(data: Dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 核心邏輯：是否需要更新資料
def check_data(new_data: Dict) -> Tuple[bool, str]:
    """
    管理資料儲存與判斷是否更新。

    :param new_data: 新取得的資料 dict
    :return: Tuple[是否有更新, 資訊文字]
    """
    new_hash = calculate_data_hash(new_data)

    if is_first_time_startup():
        ensure_data_dir()
        save_data(new_data)
        write_current_hash(new_hash)
        mark_initialized()
        return True, "系統首次啟動，已初始化資料"
    
    old_hash = read_previous_hash()

    if new_hash != old_hash:
        ensure_data_dir()
        save_data(new_data)
        write_current_hash(new_hash)
        return True, "資料內容有更新，已重新儲存"
    
    return False, "資料未變動，無需更新"
        

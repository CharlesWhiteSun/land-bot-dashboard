import csv
import json
import os
import re
from typing import Callable
from config.paths import RAW_DATA_DIR  # 引入 config.paths 中的 RAW_DATA_DIR 定義

def remove_irrelevant_csv_files(directory: str):
    """
    從指定資料夾中刪除不符合條件的 CSV 檔案：
    - 檔名不含 lvr_land
    - 交易類別為 c
    - 交易物件類別為 build, land, park
    """
    removed_files = []

    for filename in os.listdir(directory):

        filepath = os.path.join(directory, filename)
        filename_lower = filename.lower()

        # 不含 "lvr_land"
        if "lvr_land" not in filename_lower:
            os.remove(filepath)
            removed_files.append(filename)
            continue

        parts = filename_lower.split("_")

        # 交易類別為 c
        if len(parts) > 3:
            type_code = parts[3].replace(".csv", "")
            if type_code == "c":
                os.remove(filepath)
                removed_files.append(filename)
                continue

        if len(parts) <= 4:
            continue

        # 交易物件類別為 build, land, park
        object_code = parts[4].replace(".csv", "")
        if object_code in {"build", "land", "park"}:
            os.remove(filepath)
            removed_files.append(filename)

    # 結果輸出
    if removed_files:
        for f in removed_files:
            print(f"✅已刪除以下檔案：{f}")
    else:
        print("☑️沒有檔案需要刪除。")


def apply_function_to_real_estate_dirs(func: Callable[[str], None]):
    """
    對 raw 資料夾底下的 latest_notice 和所有 historySeason_id 對應的子資料夾，呼叫傳入的函式 func。
    傳入的參數為「資料夾路徑」。
    """
    # 確保 base 資料夾存在
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    json_path = os.path.join(RAW_DATA_DIR, "fetch_options_route.json")
    folder_names = {"latest_notice"}

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            folder_keys = data.get("historySeason_id", {}).keys()
            folder_names.update(folder_keys)

    for folder_name in folder_names:
        folder_path = os.path.join(RAW_DATA_DIR, folder_name)
        if os.path.exists(folder_path):
            func(folder_path)

import json
import os
import shutil
import pandas as pd
from datetime import datetime
from typing import Callable


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
        print("✅ 已刪除以下檔案：")
        for f in removed_files:
            print(f"  - {f}")
    else:
        print("✅ 沒有檔案需要刪除。")


def apply_function_to_real_estate_dirs(func: Callable[[str], None]):
    """
    對 raw 資料夾底下的 latest_notice 和所有 historySeason_id 對應的子資料夾，呼叫傳入的函式 func。
    傳入的參數為「資料夾路徑」。
    """
    base_dir = os.path.join("api", "data", "real_estate", "raw")
    json_path = os.path.join(base_dir, "fetch_options_route.json")

    folder_names = {"latest_notice"}

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            folder_keys = data.get("historySeason_id", {}).keys()
            folder_names.update(folder_keys)

    for folder_name in folder_names:
        folder_path = os.path.join(base_dir, folder_name)
        if os.path.exists(folder_path):
            func(folder_path)


def process_real_estate_data(input_dir: str, output_dir: str, archive_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    # 欄位保留清單（中文）
    required_columns = [
        "鄉鎮市區", "交易年月日", "建物型態", "主要用途", "總價元",
        "單價元平方公尺", "車位類別", "車位總價元", "車位移轉總面積平方公尺",
        "建築完成年月", "建物移轉總面積平方公尺", "移轉層次", "總樓層數", "電梯", "交易標的"
    ]

    for filename in os.listdir(input_dir):
        if not filename.endswith(".csv"):
            continue

        filepath = os.path.join(input_dir, filename)

        try:
            df = pd.read_csv(filepath, header=0, encoding="utf-8")

            # 只保留第一行中文欄位
            if df.columns[0] != "鄉鎮市區":
                df.columns = df.iloc[0]
                df = df[1:]

            # 🔧 檢查並補齊缺少欄位
            for col in required_columns:
                if col not in df.columns:
                    df[col] = pd.NA  # 或用 np.nan 也可以

            # 清除其他欄位，只保留指定欄位
            df = df[required_columns].copy()

            # 時間欄位處理
            df["交易年月日"] = pd.to_datetime(df["交易年月日"], format="%Y%m%d", errors='coerce')
            df["交易年"] = df["交易年月日"].dt.year
            df["交易月"] = df["交易年月日"].dt.month
            df["交易日"] = df["交易年月日"].dt.day
            df["年月"] = df["交易年月日"].dt.to_period("M").astype(str)

            # 數值欄位轉換
            for col in ["總價元", "單價元平方公尺", "車位總價元", "車位移轉總面積平方公尺", "建物移轉總面積平方公尺"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # 車位單價
            df["車位單價"] = df.apply(
                lambda x: x["車位總價元"] / x["車位移轉總面積平方公尺"]
                if x["車位移轉總面積平方公尺"] and x["車位移轉總面積平方公尺"] > 0 else None,
                axis=1
            )

            # 建築完成日轉換
            def parse_build_date(val):
                try:
                    val = str(int(float(val)))
                    if len(val) == 7:
                        year = int(val[:3]) + 1911
                        month = int(val[3:5])
                        day = int(val[5:])
                    elif len(val) == 6:
                        year = int(val[:3]) + 1911
                        month = int(val[3:5])
                        day = 1
                    else:
                        return pd.NaT
                    return datetime(year, month, day)
                except:
                    return pd.NaT

            df["建築完成日"] = df["建築完成年月"].apply(parse_build_date)
            df["屋齡"] = df.apply(
                lambda row: row["交易年月日"].year - row["建築完成日"].year
                if pd.notnull(row["建築完成日"]) and pd.notnull(row["交易年月日"]) else None,
                axis=1
            )

            # 交易標的分類
            def classify_target(val):
                if isinstance(val, str):
                    if "土地" in val and "建物" in val:
                        return "房地"
                    elif "土地" in val:
                        return "土地"
                    elif "建物" in val:
                        return "建物"
                return "其他"

            df["交易標的分類"] = df["交易標的"].apply(classify_target)

            # 儲存清洗後的檔案
            cleaned_filename = f"cleaned_{filename}"
            df.to_csv(os.path.join(output_dir, cleaned_filename), index=False, encoding="utf-8-sig")

            # 搬移原始檔案
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_subdir = os.path.join(archive_dir, f"archived_{timestamp}")
            os.makedirs(archive_subdir, exist_ok=True)
            shutil.move(filepath, os.path.join(archive_subdir, filename))

            print(f"✅ 已處理並清洗：{filename}")

        except Exception as e:
            print(f"⚠️ 無法處理 {filename}：{e}")

import csv
import json
import os
import pandas as pd
import re
import shutil
from typing import Callable

from utils.logger import log_warning

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
        for f in removed_files:
            print(f"✅已刪除以下檔案：{f}")
    else:
        print("☑️沒有檔案需要刪除。")


def get_house_type(diff_year):
    if diff_year <= 3:
        return "新屋"
    elif diff_year <= 10:
        return "新古屋"
    elif diff_year <= 20:
        return "中古屋"
    else:
        return "老屋"


def format_row(row, filename, idx=None, folder=None):
    trade_object = str(row['交易標的'])
    building_type = str(row['建物型態'])
    prefix_trade_object = trade_object.split('(', maxsplit=1)[0]
    prefix_building_type = building_type.split('(', maxsplit=1)[0]

    try:
        square_feet = float(row['建物移轉總面積平方公尺'])
        ping = 0.0
        if square_feet > 0.0:
            ping = round(square_feet / 3.305785, 2)
    except Exception as e:
        msg = f"Folder[{folder}] File[{filename}:{idx}] Error converting 建物坪數: {e}"
        log_warning(msg)
        print(msg)
        
    try:
        parking_space_square_feet = float(row['車位移轉總面積平方公尺'])
        car_ping = 0.0
        if parking_space_square_feet > 0.0:
            car_ping = round(parking_space_square_feet / 3.305785, 2)
    except Exception as e:
        msg = f"Folder[{folder}] File[{filename}:{idx}] Error converting 車位坪數: {e}"
        log_warning(msg)
        print(msg)

    try:
        category = house_type = "其他"
        if '房' in trade_object:
            category = "房地"
        elif '土' in trade_object:
            category = house_type = "土地"
        elif '車' in trade_object:
            category = house_type = "車位"
    except Exception as e:
        msg = f"Folder[{folder}] File[{filename}:{idx}] Error converting 分類: {e}"
        log_warning(msg)
        print(msg)

    try:
        parking_space = "無"
        if '車' in trade_object:
            parking_space = "有"
    except Exception as e:
        msg = f"Folder[{folder}] File[{filename}:{idx}] Error converting 停車位: {e}"
        log_warning(msg)
        print(msg)

    try:
        elevator = "無"
        if '有電梯' in building_type:
            elevator = "有"
    except Exception as e:
        msg = f"Folder[{folder}] File[{filename}:{idx}] Error converting 電梯: {e}"
        log_warning(msg)
        print(msg)

    trade_date, trade_year, trade_month, trade_day = "", "", "", ""
    try:
        trade_row = row['交易年月日']
        if pd.notna(trade_row):
            trade_str = str(row['交易年月日']).strip()
            match = re.match(r"(\d+)", trade_str)
            if match:
                trade = match.group(1)
                if trade.isdigit() and len(trade) >= 6:
                    trade_day = trade[-2:].zfill(2)
                    trade_month = trade[-4:-2].zfill(2)
                    trade_year = str(int(trade[:-4]) + 1911)
                    trade_date = f"{trade_year}{trade_month}{trade_day}"
    except Exception as e:
        msg = f"Folder[{folder}] File[{filename}:{idx}] Error processing date 交易年月日=[{row['交易年月日']}], error: {e}"
        log_warning(msg)
        print(msg)

    build_date = ""
    try:
        build_raw = row['建築完成年月']
        if pd.notna(build_raw):
            build_str = str(row['建築完成年月']).strip()
            match = re.match(r"(\d+)", build_str)
            if match:
                build = match.group(1)
                if build.isdigit() and len(build) >= 6:
                    build_day = build[-2:].zfill(2)
                    build_month = build[-4:-2].zfill(2)
                    build_year = str(int(build[:-4]) + 1911)
                    build_date = f"{build_year}{build_month}{build_day}"
    except Exception as e:
        msg = f"Folder[{folder}] File[{filename}:{idx}] Error processing date 建築完成年月=[{row['建築完成年月']}], error: {e}"
        log_warning(msg)
        print(msg)

    house_age = ""
    house_type = "預售屋"
    if not filename.endswith('b.csv'):
        try:
            if build_date != "":
                trade_dt = pd.to_datetime(trade_date, format='%Y%m%d', errors='coerce')
                build_dt = pd.to_datetime(build_date, format='%Y%m%d', errors='coerce')
                diff_days = (trade_dt - build_dt).days
                if diff_days >= 0:
                    diff_year = round((diff_days / 365.25), 1)
                    house_age = str(diff_year)
                    house_type = get_house_type(diff_year)
        except Exception as e:
            msg = f"Folder[{folder}] File[{filename}:{idx}] Error calculating house age: {e}"
            log_warning(msg)
            print(msg)

    return pd.Series([prefix_trade_object, prefix_building_type, ping, car_ping, 
                    category, parking_space, elevator, trade_date, trade_year, trade_month,
                    trade_day, build_date, house_age, house_type])


def clean_real_estate_csv_files_in_dir(directory: str):
    done_base_dir = os.path.join("ngui", "preprocessing", "cleaned")
    directory_name = os.path.basename(directory)
    done_dir = os.path.join(done_base_dir, directory_name)
    os.makedirs(done_dir, exist_ok=True)

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            # 跳過第二列（英文標題）
            df = pd.read_csv(
                file_path, 
                encoding='utf-8', 
                skiprows=[1], 
                on_bad_lines='skip', 
                quoting=csv.QUOTE_NONE,
                engine='python',
                quotechar='"',
                escapechar='\\',
            )

            # 欄位名稱兼容處理
            if '車位移轉總面積(平方公尺)' in df.columns:
                df = df.rename(columns={'車位移轉總面積(平方公尺)': '車位移轉總面積平方公尺'})

            columns_to_keep = [
                '鄉鎮市區', '交易標的', '交易年月日', '建物型態', '主要用途',
                '建築完成年月', '建物移轉總面積平方公尺', '總價元', 
                '車位移轉總面積平方公尺', '車位總價元',
            ]
            df_cleaned = df.loc[:, columns_to_keep].copy()

            df_cleaned[['交易標的', '建物型態', '建物坪數', '車位坪數', '分類',
                        '停車位', '電梯', '交易年月日', '交易年', '交易月',
                        '交易日', '建築完成年月', '房齡', '屋況']] = \
                    df_cleaned.apply(
                        lambda row, filename=file_path, folder=directory_name: \
                            format_row(row, filename=filename, idx=row.name, folder=folder),
                        axis=1
                    )

            cleaned_path = os.path.join(directory, filename.replace('.csv', '_cleaned.csv'))
            df_cleaned.to_csv(cleaned_path, index=False, encoding='utf-8')
            print(f"資料清洗完成，已另存為 {cleaned_path}")

            # 搬移清洗完畢檔案到 done 資料夾
            shutil.move(cleaned_path, os.path.join(done_dir, filename.replace('.csv', '_cleaned.csv')))
            print(f"清洗完畢檔案已搬移到 {os.path.join(done_dir, filename.replace('.csv', '_cleaned.csv'))}")

        except Exception as e:
            msg = f"清洗失敗 {directory_name}/{filename}: {e}"
            log_warning(msg)
            print(msg)


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

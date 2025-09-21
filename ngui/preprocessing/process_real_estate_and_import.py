import os
import pandas as pd
import shutil
import sqlite3
import re
import csv

from utils.logger import log_warning, log_info
from config.paths import RAW_DATA_DIR, OLD_DATA_DIR, DB_PATH

def get_house_type(diff_year):
    if diff_year <= 3:
        return "新屋"
    if diff_year <= 10:
        return "新古屋"
    if diff_year <= 20:
        return "中古屋"
    return "老屋"

def format_row(row, filename, idx=None, folder=None):
    trade_object = str(row['交易標的'])
    building_type = str(row['建物型態'])
    prefix_trade_object = trade_object.split('(', maxsplit=1)[0]
    prefix_building_type = building_type.split('(', maxsplit=1)[0]

    ping = 0.0
    unit_ping_thousand_price = 0.0
    try:
        square_feet = float(row['建物移轉總面積平方公尺'])
        total_price_row = float(row['總價元'])
        if square_feet > 0.0:
            ping = round(square_feet / 3.305785, 2)
            if ping > 0:
                unit_ping_price = total_price_row / ping
                unit_ping_thousand_price = round(unit_ping_price / 10000, 1)
    except Exception as e:
        msg = f"{filename}:{idx} Error converting 建物坪數: {e}"
        log_warning(msg)
        print(msg)

    total_thousand_price = 0.0
    try:
        total_price_row = float(row['總價元'])
        if total_price_row > 0.0:
            total_thousand_price = round(total_price_row / 10000, 1)
    except Exception as e:
        msg = f"{filename}:{idx} Error converting 總價元: {e}"
        log_warning(msg)
        print(msg)

    car_thousand_price = 0.0
    try:
        car_price_row = float(row['車位總價元'])
        if car_price_row > 0.0:
            car_thousand_price = round(car_price_row / 10000, 1)
    except Exception as e:
        msg = f"{filename}:{idx} Error converting 車位總價元: {e}"
        log_warning(msg)
        print(msg)

    car_ping = 0.0
    try:
        parking_space_square_feet_row = float(row['車位移轉總面積平方公尺'])
        if parking_space_square_feet_row > 0.0:
            car_ping = round(parking_space_square_feet_row / 3.305785, 2)
    except Exception as e:
        msg = f"{filename}:{idx} Error converting 車位坪數: {e}"
        log_warning(msg)
        print(msg)

    category = house_type = "其他"
    try:
        if '房' in trade_object:
            category = "房地"
        elif '土' in trade_object:
            category = house_type = "土地"
        elif '車' in trade_object:
            category = house_type = "車位"
    except Exception as e:
        msg = f"{filename}:{idx} Error converting 分類: {e}"
        log_warning(msg)
        print(msg)

    parking_space = "無"
    try:
        if '車' in trade_object:
            parking_space = "有"
    except Exception as e:
        msg = f"{filename}:{idx} Error converting 停車位: {e}"
        log_warning(msg)
        print(msg)

    elevator = "無"
    try:
        if '有電梯' in building_type:
            elevator = "有"
    except Exception as e:
        msg = f"{filename}:{idx} Error converting 電梯: {e}"
        log_warning(msg)
        print(msg)

    trade_date, trade_year, trade_month, trade_day = "", "", "", ""
    trade_row = row['交易年月日']
    try:
        if pd.notna(trade_row):
            trade_str = str(trade_row).strip()
            match = re.match(r"(\d+)", trade_str)
            if match:
                trade = match.group(1)
                if trade.isdigit() and len(trade) >= 6:
                    trade_day = trade[-2:].zfill(2)
                    trade_month = trade[-4:-2].zfill(2)
                    trade_year = str(int(trade[:-4]) + 1911)
                    trade_date = f"{trade_year}{trade_month}{trade_day}"
    except Exception as e:
        msg = f"{filename}:{idx} Error processing date 交易年月日=[{row['交易年月日']}], error: {e}"
        log_warning(msg)
        print(msg)

    build_date = ""
    build_row = row['建築完成年月']
    try:
        if pd.notna(build_row):
            build_str = str(build_row).strip()
            match = re.match(r"(\d+)", build_str)
            if match:
                build = match.group(1)
                if build.isdigit() and len(build) >= 6:
                    build_day = build[-2:].zfill(2)
                    build_month = build[-4:-2].zfill(2)
                    build_year = str(int(build[:-4]) + 1911)
                    build_date = f"{build_year}{build_month}{build_day}"
    except Exception as e:
        msg = f"{filename}:{idx} Error processing date 建築完成年月=[{row['建築完成年月']}], error: {e}"
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
            msg = f"{filename}:{idx} Error calculating house age: {e}"
            log_warning(msg)
            print(msg)

    return pd.Series([prefix_trade_object, prefix_building_type, ping, total_thousand_price, 
                    unit_ping_thousand_price, car_ping, car_thousand_price, category, 
                    parking_space, elevator, trade_date, trade_year, trade_month, trade_day, 
                    build_date, house_age, house_type])

CITY_CODE_MAP = {
    "c": "基隆", "a": "臺北", "f": "新北", "h": "桃園", "o": "新竹", 
    "j": "新竹", "k": "苗栗", "b": "臺中", "m": "南投", "n": "彰化", 
    "p": "雲林", "i": "嘉義", "q": "嘉義", "d": "臺南", "e": "高雄",
    "t": "屏東", "g": "宜蘭", "u": "花蓮", "v": "臺東", "x": "澎湖",
    "w": "金門", "z": "連江",
}

def get_city_name(filename: str) -> str:
    match = re.match(r"([a-z])_lvr_land_[ab]\.csv", filename.lower())
    return CITY_CODE_MAP.get(match.group(1), "未知縣市") if match else "未知縣市"

def map_dtype_to_sql(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        return "REAL"
    else:
        return "TEXT"

def clean_and_import_file(file_path: str, season_folder: str, conn: sqlite3.Connection):
    filename = os.path.basename(file_path)
    city = get_city_name(filename)
    if city == "未知縣市":
        print(f"❌ 無法判斷縣市：{filename}")
        return

    try:
        df = pd.read_csv(
            file_path,
            encoding='utf-8',
            skiprows=[1],
            on_bad_lines='skip',
            quoting=csv.QUOTE_NONE,
            engine='python',
            quotechar='"',
        )

        if '車位移轉總面積(平方公尺)' in df.columns:
            df = df.rename(columns={'車位移轉總面積(平方公尺)': '車位移轉總面積平方公尺'})

        columns_to_keep = [
            '鄉鎮市區', '交易標的', '交易年月日', '建物型態', '主要用途',
            '建築完成年月', '建物移轉總面積平方公尺', '總價元',
            '車位移轉總面積平方公尺', '車位總價元',
        ]
        df_cleaned = df.loc[:, columns_to_keep].copy()

        df_cleaned[['交易標的', '建物型態', '建物坪數', '建物總價萬元', '建物每坪單價萬元',
                    '車位坪數', '車位總價萬元', '分類', '停車位', '電梯', '交易年月日',
                    '交易年', '交易月', '交易日', '建築完成年月', '房齡', '屋況']] = \
            df_cleaned.apply(
                lambda row, filename=file_path, folder=filename: \
                            format_row(row, filename=filename, idx=row.name, folder=folder),
                axis=1
            )

        df_cleaned.insert(0, "縣市", city)

        float_columns = [
            "建物坪數", "建物總價萬元", "建物每坪單價萬元",
            "車位坪數", "車位總價萬元", "房齡",
            "建物移轉總面積平方公尺", "車位移轉總面積平方公尺"
        ]
        int_columns = ["總價元", "車位總價元"]

        for col in float_columns:
            if col in df_cleaned.columns:
                df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors="coerce")

        for col in int_columns:
            if col in df_cleaned.columns:
                df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors="coerce", downcast="integer")

        columns_def = ", ".join([f'"{col}" {map_dtype_to_sql(dtype)}' for col, dtype in df_cleaned.dtypes.items()])
        conn.execute(f'''
            CREATE TABLE IF NOT EXISTS "{city}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                {columns_def}
            )
        ''')

        df_cleaned.to_sql(city, conn, if_exists="append", index=False)
        print(f"✅ 已匯入 {season_folder}/{filename} -> 表 {city} 共 {len(df_cleaned)} 筆")

    except Exception as e:
        msg = f"❌ 清洗或匯入失敗 {season_folder}/{filename}，錯誤：{e}"
        log_warning(msg)
        print(msg)

def apply_clean_and_import_file():
    # 確保 RAW 與 OLD 資料夾存在
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(OLD_DATA_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    for folder in os.listdir(RAW_DATA_DIR):
        folder_path = os.path.join(RAW_DATA_DIR, folder)
        if not os.path.isdir(folder_path):
            continue

        if not os.listdir(folder_path):
            print(f"資料夾 {folder_path} 為空，將被刪除")
            os.rmdir(folder_path)
            continue

        old_folder_path = os.path.join(OLD_DATA_DIR, folder)
        os.makedirs(old_folder_path, exist_ok=True)

        for file in os.listdir(folder_path):
            if file.endswith(".csv"):
                try:
                    clean_and_import_file(os.path.join(folder_path, file), folder, conn)
                    shutil.move(os.path.join(folder_path, file), os.path.join(old_folder_path, file))
                    print(f"✅ 檔案 {file} 處理完成，已移動到 {old_folder_path}")
                except Exception as e:
                    print(f"❌ 處理檔案 {file} 時出錯，錯誤：{e}")
                    continue

        if not os.listdir(folder_path):
            print(f"資料夾 {folder_path} 內已無檔案，將被刪除")
            os.rmdir(folder_path)

    conn.commit()
    conn.close()

    print("✅ 所有檔案處理完成")
    log_info("✅ 所有檔案處理完成")
    
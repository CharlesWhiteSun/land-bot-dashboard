import os
import pandas as pd
import sqlite3
import re

from utils.logger import log_warning


# 資料夾與 DB 設定
CLEANED_DIR = os.path.join("ngui", "preprocessing", "cleaned")
DB_DIR = os.path.join("ngui", "database")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "real_estate.sqlite")

# 縣市代碼對照表
CITY_CODE_MAP = {
    "C": "基隆市", "A": "臺北市", "F": "新北市", "H": "桃園縣", "O": "新竹市",
    "J": "新竹縣", "K": "苗栗縣", "B": "臺中市", "M": "南投縣", "N": "彰化縣",
    "P": "雲林縣", "I": "嘉義市", "Q": "嘉義縣", "D": "臺南市", "E": "高雄市",
    "T": "屏東縣", "G": "宜蘭縣", "U": "花蓮縣", "V": "臺東縣", "X": "澎湖縣",
    "W": "金門縣", "Z": "連江縣"
}

# 交易類別對照表
TRADE_TYPE_MAP = {
    "a": "不動產買賣",
    "b": "預售屋買賣"
}

# 季別轉換
def season_label(folder_name: str) -> str:
    if folder_name == "latest_notice":
        return "最新一期"
    match = re.match(r"(\d+)[sS](\d)", folder_name)
    if match:
        year, season = match.groups()
        return f"{year}年度第{season}季"
    return "未知季別"

# 匯入單一 CSV 檔案
def import_csv_to_sqlite(csv_path: str, season: str, conn):
    filename = os.path.basename(csv_path)
    parts = filename.split("_")
    
    if len(parts) < 4:
        msg = f"❌無效檔案名稱：{filename}，應為格式 a_lvr_land_a_cleaned.csv"
        log_warning(msg)
        print(msg)
        return
    
    city_code = parts[0].lower()
    trade_code = parts[3][0].lower()

    city = CITY_CODE_MAP.get(city_code.upper())
    trade_type = TRADE_TYPE_MAP.get(trade_code)

    if not city or not trade_type:
        msg = f"❌無法解析檔案名稱：{filename}，可能是縣市代碼或交易類別錯誤"
        log_warning(msg)
        print(msg)
        return
    
    table_name = f"{city}_{trade_type}"
    table_name = table_name.replace(" ", "")  # 移除空格
    
    try:
        df = pd.read_csv(csv_path)
        df["季別"] = season
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"✅ 已匯入：{csv_path} → {table_name}（{len(df)} 筆）")
    except Exception as e:
        msg = f"❌匯入失敗：{csv_path}，錯誤：{e}"
        log_warning(msg)
        print(msg)

# 主執行函式
def import_all_cleaned_csv():
    conn = sqlite3.connect(DB_PATH)

    for folder_name in os.listdir(CLEANED_DIR):
        folder_path = os.path.join(CLEANED_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        season = season_label(folder_name)

        for filename in os.listdir(folder_path):
            if filename.endswith("_cleaned.csv"):
                csv_path = os.path.join(folder_path, filename)
                import_csv_to_sqlite(csv_path, season, conn)

    conn.close()
    print(f"\n🎉 所有資料已匯入完畢，儲存於 {DB_PATH}")

if __name__ == "__main__":
    import_all_cleaned_csv()

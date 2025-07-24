import os
import pandas as pd

from utils.logger import log_warning


def merge_cleaned_csv_files():
    """
    合併 ngui/preprocessing/cleaned 資料夾下的所有清洗後的 CSV 檔案。
    假設每個檔案的命名格式為：a_lvr_land_a_cleaned.csv
    """
    CITY_CODE_MAP = {
        "A": "臺北市", "B": "臺中市", "C": "基隆市", "D": "臺南市", "E": "高雄市", "F": "新北市", "G": "宜蘭縣",
        "H": "桃園縣", "I": "嘉義市", "J": "新竹縣", "K": "苗栗縣", "M": "南投縣", "N": "彰化縣", "O": "新竹市",
        "P": "雲林縣", "Q": "嘉義縣", "T": "屏東縣", "U": "花蓮縣", "V": "臺東縣", "W": "金門縣", "X": "澎湖縣", "Z": "連江縣"
    }
    TRADE_TYPE_MAP = {
        "a": "不動產買賣",
        "b": "預售屋買賣",
    }

    CLEANED_ROOT = os.path.join("ngui", "preprocessing", "cleaned")
    MERGED_OUTPUT_PATH = os.path.join("ngui", "preprocessing", "merged_all.csv")

    all_dataframes = []

    for season_dir in os.listdir(CLEANED_ROOT):
        season_path = os.path.join(CLEANED_ROOT, season_dir)
        if not os.path.isdir(season_path):
            continue  # 忽略非資料夾

        for file in os.listdir(season_path):
            if not file.endswith("_cleaned.csv"):
                continue  # 忽略非清洗檔案

            try:
                # 解析檔名：範例 a_lvr_land_a_cleaned.csv
                parts = file.split("_")
                city_code = parts[0].upper()
                trade_type_key = parts[-2].lower()  # 倒數第二個部分為 a/b

                city_name = CITY_CODE_MAP.get(city_code, "未知縣市")
                trade_type = TRADE_TYPE_MAP.get(trade_type_key, "其他")

                df = pd.read_csv(os.path.join(season_path, file), encoding="utf-8")

                df["縣市"] = city_name
                df["季別"] = season_dir
                df["交易類別"] = trade_type

                all_dataframes.append(df)

                print(f"✅ 合併：{season_dir}/{file}")

            except Exception as e:
                msg = f"⚠️錯誤於 {season_dir}/{file}：{e}"
                log_warning(msg)
                print(msg)

    if all_dataframes:
        merged_df = pd.concat(all_dataframes, ignore_index=True)
        merged_df.to_csv(MERGED_OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"\n✅ 完成合併，儲存於：{MERGED_OUTPUT_PATH}")
    else:
        print("⚠️ 沒有找到可合併的資料")


if __name__ == "__main__":
    merge_cleaned_csv_files()
    print("合併清洗後的 CSV 檔案完成。")
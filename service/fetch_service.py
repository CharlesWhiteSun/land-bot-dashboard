import os
import json
import shutil
import time
import zipfile
from datetime import datetime
from typing import List, Tuple

from api.routes.real_estate import fetch_options_route, fetch_latest_notice_route, download_zip_route
from ngui.preprocessing.real_estate_cleaner import *
from utils.fetch_manager import check_data
from utils.logger import log_info

def file_unzip(base_path: str, file_name: str):
    extract_dir_path = os.path.join(base_path, file_name)
    zip_path_name = os.path.join(base_path, f"{file_name}.zip")

    if not os.path.exists(zip_path_name):
        msg = f"❌[解壓縮失敗] 該系統路徑下找不到壓縮檔: {zip_path_name}"
        print(msg)
        log_info(msg)
        return
    
    # 建立目標資料夾
    os.makedirs(extract_dir_path, exist_ok=True)

    # 解壓縮所有檔案至資料夾中
    with zipfile.ZipFile(zip_path_name, 'r') as zip_ref:
        zip_ref.extractall(extract_dir_path)

    msg = f"✅[解壓縮完成] 所有檔案已存入 {extract_dir_path} 資料夾底下"
    print(msg)
    log_info(msg)


def unzip_all_season_zips(base_path):
    json_path = os.path.join("api", "data", "real_estate", "raw", "fetch_options_route.json")

    if not os.path.exists(json_path):
        print(f"❌ 找不到設定檔: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    history_seasons = data.get("historySeason_id", {})
    if not history_seasons:
        print("❌ 找不到 historySeason_id 資料")
        return

    for season in history_seasons.keys():
        file_unzip(base_path, season)
    
    
def delete_path_recursive(base_path: str, name: str) -> Tuple[bool, str]:
    try:
        target = os.path.join(base_path, name)
        if not os.path.exists(target):
            return True, f"☑️[無須刪除] 該路徑不存在: {target}"
        
        if os.path.isfile(target):
            os.remove(target)
            return True, f"🗑️[已刪除檔案] {target}"
        elif os.path.isdir(target):
            shutil.rmtree(target)
            return True, f"✅[已刪除資料夾] {target}"
        else:
            return False, f"⚠️[未知類型] 無法判斷是檔案或資料夾: {target}"

    except Exception as e:
        return False, f"❌[刪除失敗] 發生錯誤: {str(e)}"
    
def delete_all_real_estate_raw_zip():
    base_path = os.path.join("api", "data", "real_estate", "raw")

    _, msg = delete_path_recursive(base_path, 'latest_notice.zip')
    print(msg)

    # 處理 historySeason_id 對應壓縮檔與資料夾
    json_path = os.path.join(base_path, "fetch_options_route.json")
    if not os.path.exists(json_path):
        print(f"❌ 無法找到 {json_path}，略過 historySeason_id 處理")
        return
    
    with open(json_path, "r", encoding="utf-8") as f:
        content = json.load(f)

    season_dict = content.get("historySeason_id", {})
    if not season_dict:
        print("⚠️無 historySeason_id 資料，略過處理")
        return

    for season in season_dict.keys():
        # 刪除壓縮檔與資料夾
        _, msg = delete_path_recursive(base_path, f'{season}.zip')
        print(msg)


def delete_all_real_estate_raw_folder():
    base_path = os.path.join("api", "data", "real_estate", "raw")

    _, msg = delete_path_recursive(base_path, 'latest_notice')
    print(msg)

    # 處理 historySeason_id 對應壓縮檔與資料夾
    json_path = os.path.join(base_path, "fetch_options_route.json")
    if not os.path.exists(json_path):
        print(f"❌ 無法找到 {json_path}，略過 historySeason_id 處理")
        return
    
    with open(json_path, "r", encoding="utf-8") as f:
        content = json.load(f)

    season_dict = content.get("historySeason_id", {})
    if not season_dict:
        print("⚠️無 historySeason_id 資料，略過處理")
        return

    for season in season_dict.keys():
        _, msg = delete_path_recursive(base_path, season)
        print(msg)
    

def move_folder_to_dest(base_path: str, folder_name: str, dest_dir: str) -> Tuple[bool, str]:
    target = os.path.join(base_path, folder_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_folder_name = f"{folder_name}_{timestamp}"
    dest_path = os.path.join(dest_dir, dest_folder_name)

    try:
        if not os.path.exists(target):
            return True, f"☑️[無須搬移] 該資料夾不存在: {target}"
        
        os.makedirs(dest_dir, exist_ok=True)
        shutil.move(target, dest_path)
        return True, f"✅[已搬移] {dest_path}"
    
    except Exception as e:
        return False, f"❌[搬移失敗] 發生錯誤: {str(e)}"
    

def move_all_season_folders(base_path: str, dest_dir: str):
    json_path = os.path.join("api", "data", "real_estate", "raw", "fetch_options_route.json")

    if not os.path.exists(json_path):
        print(f"❌ 找不到檔案: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    history_seasons = data.get("historySeason_id", {})
    if not history_seasons:
        print("❌ 找不到 historySeason_id 資料")
        return

    for season in history_seasons.keys():
        _, message = move_folder_to_dest(base_path, season, dest_dir)
        print(message)


def batch_download_zip_from_json(
    json_path: str,
    retry_limit: int = 1,
    sleep_interval: float = 1.0
) -> None:
    if not os.path.exists(json_path):
        print(f"❌檔案不存在：{json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    season_dict = data.get("historySeason_id")
    if not season_dict:
        print("❌找不到 historySeason_id 欄位")
        return

    failed_keys: List[str] = []

    for season in season_dict:
        attempt = 0
        success = False
        while attempt <= retry_limit:
            print(f"⏳ 嘗試下載 {season}（第 {attempt+1} 次）...")
            success, msg, _ = download_zip_route.download_season_zip(season)
            if success:
                print(f"✅成功下載：{season}")
                break
            else:
                print(f"⚠️下載失敗：{msg}")
                attempt += 1
                time.sleep(sleep_interval)
        if not success:
            failed_keys.append(season)

    if failed_keys:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fail_path = os.path.join("api", "data", "real_estate", "raw", f"download_failed_{timestamp}.json")
        with open(fail_path, "w", encoding="utf-8") as f:
            json.dump({"failed": failed_keys}, f, ensure_ascii=False, indent=2)
        print(f"❗ 失敗紀錄已儲存：{fail_path}")
    else:
        print("🎉 所有壓縮檔皆成功下載")


def fetch_func():
    # 抓取最新資料內容字串
    news = fetch_latest_notice_route.info_json()
    if not news['success']:
        msg = f"❌[失敗][本期下載-資料內容字串] 暫停此次更新。錯誤原因: {news['error']}"
        print(msg)
        log_info(msg)
        return

    # 檢查是否有需要更新
    need_to_update, message = check_data(news['content'])
    if not need_to_update:
        msg = f"☑️[無須更新][本期下載-資料內容字串] {message}"
        print(msg)
        log_info(msg)
        return
    msg = f"✅[已更新][本期下載-資料內容字串] {message}"
    print(msg)
    log_info(msg)

    # 如果有新資料則刪除舊資料夾
    delete_all_real_estate_raw_folder()

    # 抓取最新資料 zip
    resp = fetch_latest_notice_route.latest_notice_zip()
    if not resp['success']:
        msg = f"❌[下載失敗][本期下載 zip] 錯誤原因: {resp['error']}"
        print(msg)
        log_info(msg)
        return
    
    # 解壓縮新資料
    raw_path = 'api/data/real_estate/raw'
    file_unzip(raw_path, 'latest_notice')

    # 抓取歷史資料發布日期 option 字串
    opts = fetch_options_route.fetch_options_and_save()
    if not opts['success']:
        msg = f"❌[更失敗][歷史資料-發布日期 option 字串] 暫停此次更新。錯誤原因: {opts['error']}"
        print(msg)
        log_info(msg)
        return  
    
    msg = f"☑️[無須更新][歷史資料-發布日期 option 字串] 共取得 {len(opts['data'])} 筆"
    if opts['updated']:
        msg = f"✅[已更新][歷史資料-發布日期 option 字串] 共取得 {len(opts['data'])} 筆"
    print(msg)
    log_info(msg)

    # 抓取歷史資料 zip，解壓縮
    batch_download_zip_from_json(f'{raw_path}/fetch_options_route.json')
    unzip_all_season_zips(raw_path)

    # 把壓縮檔移除
    delete_all_real_estate_raw_zip()

    # 移除最新、歷史資料中不需要分析的檔案
    apply_function_to_real_estate_dirs(remove_irrelevant_csv_files)

    # 清洗最新、歷史資料中的 CSV 檔案
    apply_function_to_real_estate_dirs(clean_real_estate_csv_files_in_dir)

    # 之後資料清洗完也要考慮把舊資料夾移除，只留分析好的資料
    # 之後資料清洗完也要考慮把舊資料夾移除，只留分析好的資料
    # 之後資料清洗完也要考慮把舊資料夾移除，只留分析好的資料

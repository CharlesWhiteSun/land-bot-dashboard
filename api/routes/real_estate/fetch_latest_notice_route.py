import os
import json
import requests
from datetime import datetime
from fastapi import APIRouter, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.logger import log_info, log_error
from utils.trace import generate_trace_id
from utils.notice_parser import parse_notice_to_dict
from enums.error_code import ErrorCode

router = APIRouter()

@router.get("/fetch_latest_notice")
def fetch_latest_notice():
    url = "https://plvr.land.moi.gov.tw/DownloadOpenData"

    raw_dir = os.path.join("api", "data", "real_estate", "raw")
    old_dir = os.path.join("api", "data", "real_estate", "old")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(old_dir, exist_ok=True)

    json_path = os.path.join(raw_dir, "latest_notice.json")
    zip_path = os.path.join(raw_dir, "latest_notice.zip")
    trace_id = generate_trace_id()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--allow-insecure-localhost')

    driver = None

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # 抓取公告文字
        span = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#tab_opendata_active_content span.text-danger"))
        )
        raw_text = span.text.strip()
        parsed = parse_notice_to_dict(raw_text)

        # 比對舊資料
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                existing = json.load(f)

            if existing == parsed:
                log_info("📄 公告內容未變更，略過更新")
                return {
                    "message": "公告內容未變更，略過更新",
                    "content": parsed
                }

            # 備份舊資料
            timestamp = datetime.now().strftime("%Y%m%d-%H%M")
            os.rename(json_path, os.path.join(old_dir, f"{timestamp}_latest_notice.json"))
            if os.path.exists(zip_path):
                os.rename(zip_path, os.path.join(old_dir, f"{timestamp}_latest_notice.zip"))

        # 儲存新 JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)

        # 下載 ZIP
        zip_url = "https://plvr.land.moi.gov.tw//Download?type=zip&fileName=lvr_landcsv.zip"
        response = requests.get(zip_url, timeout=30)

        if response.status_code != 200:
            trace_id = generate_trace_id()
            log_error(ErrorCode.FILE_NOT_FOUND.value, f"HTTP {response.status_code}", trace_id)
            raise HTTPException(status_code=404, detail="下載失敗，請稍後再試")

        with open(zip_path, "wb") as f:
            f.write(response.content)

        log_info("✅ 成功更新公告")
        return {
            "message": "✅ 成功更新公告",
            "json_path": json_path,
            "zip_path": zip_path,
            "content": parsed
        }

    except Exception as e:
        trace_id = generate_trace_id()
        log_error(ErrorCode.UNKNOWN_ERROR.value, str(e), trace_id)
        raise HTTPException(status_code=500, detail=f"下載發生錯誤：{str(e)}") from e

    finally:
        if driver:
            driver.quit()

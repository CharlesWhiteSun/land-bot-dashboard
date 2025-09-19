import os
import json
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.logger import log_info, log_error
from utils.trace import generate_trace_id
from utils.notice_parser import parse_notice_to_dict
from enums.error_code import ErrorCode

from fastapi import APIRouter
from utils.response_helper import success_response, error_response


def info_json() -> dict:
    url = "https://plvr.land.moi.gov.tw/DownloadOpenData"
    trace_id = generate_trace_id()
    raw_dir = os.path.join("api", "data", "real_estate", "raw")
    old_dir = os.path.join("api", "data", "real_estate", "old")
    json_path = os.path.join(raw_dir, "latest_notice.json")
    zip_path = os.path.join(raw_dir, "latest_notice.zip")

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(old_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--use-gl=swiftshader")
    chrome_options.add_argument("--enable-webgl")
    chrome_options.add_argument("--ignore-gpu-blacklist")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--allow-insecure-localhost')
    chrome_options.add_argument("--window-size=1920,1080")

    driver = None

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        span = WebDriverWait(driver, 10, poll_frequency=0.25).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#tab_opendata_active_content span.text-danger"))
        )
        raw_text = span.text.strip()
        new = parse_notice_to_dict(raw_text)
        old = None

        # 檢查舊資料
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                old = json.load(f)
        if old == new:
            log_info("☑️[無須更新][本期下載-資料內容字串] 內容未變更")
            return {
                "success": True,
                "updated": False,
                "content": new
            }
        
        # 備份舊資料
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        if os.path.exists(json_path):
            os.rename(json_path, os.path.join(old_dir, f"{timestamp}_latest_notice.json"))
        if os.path.exists(zip_path):
            os.rename(zip_path, os.path.join(old_dir, f"{timestamp}_latest_notice.zip"))

        # 儲存新 JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(new, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "updated": True,
            "content": new
        }

    except Exception as e:
        log_error(ErrorCode.UNKNOWN_ERROR.value, str(e), trace_id)
        return {
            "success": False,
            "trace_id": trace_id,
            "error": str(e)
        }

    finally:
        if driver:
            driver.quit()


def latest_notice_zip() -> dict:
    try:
        # 下載最新資料壓縮檔
        zip_url = "https://plvr.land.moi.gov.tw/Download?type=zip&fileName=lvr_landcsv.zip"
        response = requests.get(zip_url, timeout=30)

        trace_id = generate_trace_id()
        raw_dir = os.path.join("api", "data", "real_estate", "raw")
        zip_path = os.path.join(raw_dir, "latest_notice.zip")

        if response.status_code != 200:
            log_error(ErrorCode.FILE_NOT_FOUND.value, f"HTTP {response.status_code}", trace_id)
            return {
                "success": False,
                "trace_id": trace_id,
                "error": f"❌[下載失敗] HTTP {response.status_code}"
            }

        with open(zip_path, "wb") as f:
            f.write(response.content)

        log_info("✅[下載成功]")
        return {
            "success": True,
            "updated": True,
            "content": None
        }

    except Exception as e:
        log_error(ErrorCode.UNKNOWN_ERROR.value, str(e), trace_id)
        return {
            "success": False,
            "trace_id": trace_id,
            "error": str(e)
        }

router = APIRouter()

@router.get("/fetch_latest_notice")
async def fetch_latest_notice():
    result = info_json()

    if result["success"]:
        return success_response({
            "updated": result.get("updated", False),
            "content": result.get("content", result['content'])
        })
    
    return error_response(
        error_code=ErrorCode.UNKNOWN_ERROR.value,
        message=result.get("error", "抓取失敗"),
        trace_id=result.get("trace_id", ""),
        status_code=500
    )
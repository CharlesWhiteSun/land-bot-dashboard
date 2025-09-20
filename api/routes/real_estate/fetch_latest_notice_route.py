import os
import json
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

from fastapi import APIRouter
from utils.logger import log_info, log_error
from utils.trace import generate_trace_id
from utils.notice_parser import parse_notice_to_dict
from enums.error_code import ErrorCode
from utils.response_helper import success_response, error_response
from config.paths import RAW_DATA_DIR, OLD_DATA_DIR

router = APIRouter()

def info_json() -> dict:
    url = "https://plvr.land.moi.gov.tw/DownloadOpenData"
    trace_id = generate_trace_id()
    json_path = os.path.join(RAW_DATA_DIR, "latest_notice.json")
    zip_path = os.path.join(RAW_DATA_DIR, "latest_notice.zip")

    print(json_path)

    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(OLD_DATA_DIR, exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)

            # 等待元素渲染出來
            span_text = page.locator("#tab_opendata_active_content span.text-danger").inner_text(timeout=10000)
            browser.close()

        # 解析公告文字
        new = parse_notice_to_dict(span_text)
        old = None

        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                old = json.load(f)

        if old == new:
            log_info("☑️[無須更新][本期下載-資料內容字串] 內容未變更")
            return {"success": True, "updated": False, "content": new}

        # 備份舊檔
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        if os.path.exists(json_path):
            os.rename(json_path, os.path.join(OLD_DATA_DIR, f"{timestamp}_latest_notice.json"))
        if os.path.exists(zip_path):
            os.rename(zip_path, os.path.join(OLD_DATA_DIR, f"{timestamp}_latest_notice.zip"))

        # 儲存新 JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(new, f, ensure_ascii=False, indent=2)

        return {"success": True, "updated": True, "content": new}

    except Exception as e:
        log_error(ErrorCode.UNKNOWN_ERROR.value, str(e), trace_id)
        return {"success": False, "trace_id": trace_id, "error": str(e)}


def latest_notice_zip() -> dict:
    trace_id = generate_trace_id()
    try:
        zip_url = "https://plvr.land.moi.gov.tw/Download?type=zip&fileName=lvr_landcsv.zip"
        response = requests.get(zip_url, timeout=30)
        zip_path = os.path.join(RAW_DATA_DIR, "latest_notice.zip")
        os.makedirs(RAW_DATA_DIR, exist_ok=True)

        if response.status_code != 200:
            log_error(ErrorCode.FILE_NOT_FOUND.value, f"HTTP {response.status_code}", trace_id)
            return {"success": False, "trace_id": trace_id, "error": f"HTTP {response.status_code}"}

        with open(zip_path, "wb") as f:
            f.write(response.content)

        log_info("✅[下載成功]")
        return {"success": True, "updated": True, "content": None}

    except Exception as e:
        log_error(ErrorCode.UNKNOWN_ERROR.value, str(e), trace_id)
        return {"success": False, "trace_id": trace_id, "error": str(e)}


@router.get("/fetch_latest_notice")
async def fetch_latest_notice():
    result = info_json()
    if result["success"]:
        return success_response({"updated": result.get("updated", False), "content": result['content']})
    return error_response(
        error_code=ErrorCode.UNKNOWN_ERROR.value,
        message=result.get("error", "抓取失敗"),
        trace_id=result.get("trace_id", ""),
        status_code=500
    )

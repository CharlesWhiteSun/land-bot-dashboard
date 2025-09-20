import os
import json
import requests
from fastapi import APIRouter
from playwright.sync_api import sync_playwright

from enums.error_code import ErrorCode
from utils.logger import log_error
from utils.trace import generate_trace_id
from utils.response_helper import success_response, error_response
from config.paths import RAW_DATA_DIR


router = APIRouter()

DATA_FILE = os.path.join(RAW_DATA_DIR, "fetch_options_route.json")


def save_or_update_data(new_data: dict) -> bool:
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        return True  # 第一次寫入，視為有更新

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        existing_data = json.load(f)

    updated = False
    for key, val in new_data["historySeason_id"].items():
        if key not in existing_data.get("historySeason_id", {}):
            existing_data["historySeason_id"][key] = val
            updated = True

    if updated:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

    return updated


def fetch_options_and_save() -> dict:
    trace_id = generate_trace_id()
    try:
        url = "https://plvr.land.moi.gov.tw/DownloadOpenData"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)

            # 切換到「歷史資料」分頁
            page.locator('a.btndl[aria-controls="tab_opendata_history_content"]').click()

            # 等待 select 出現
            select_locator = page.locator("#historySeason_id")
            select_locator.wait_for(timeout=10000)

            # 抓取所有 <option>
            options = select_locator.locator("option").all()
            result = {
                "historySeason_id": {
                    opt.get_attribute("value"): opt.inner_text().strip()
                    for opt in options if opt.get_attribute("value")
                }
            }
            browser.close()

        if not result["historySeason_id"]:
            msg = "抓取失敗，歷史 Season 選單為空"
            log_error(ErrorCode.UNKNOWN_ERROR.value, msg, trace_id)
            return {"success": False, "trace_id": trace_id, "error": msg}

        updated = save_or_update_data(result)
        return {"success": True, "data": result["historySeason_id"], "updated": updated}

    except Exception as e:
        log_error(ErrorCode.UNKNOWN_ERROR.value, f"抓取失敗：{str(e)}", trace_id)
        return {"success": False, "trace_id": trace_id, "error": str(e)}



@router.get("/fetch_options")
async def fetch_options():
    result = fetch_options_and_save()

    if result["success"]:
        return success_response({
            "historySeason_id": result["data"],
            "updated": result["updated"]
        })

    return error_response(
        error_code=ErrorCode.UNKNOWN_ERROR.value,
        message="資料抓取失敗，請稍後再試",
        trace_id=result["trace_id"],
        status_code=500
    )

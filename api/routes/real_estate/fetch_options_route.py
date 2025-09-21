import os
import json
import requests
from fastapi import APIRouter
import asyncio
from playwright.async_api import async_playwright

from enums.error_code import ErrorCode
from utils.logger import log_error
from utils.trace import generate_trace_id
from config.paths import RAW_DATA_DIR


router = APIRouter()
DATA_FILE = os.path.join(RAW_DATA_DIR, "fetch_options_route.json")


def need_to_update_or_not(new_data: dict) -> bool:
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


async def get_history_data_and_save() -> dict:
    trace_id = generate_trace_id()
    try:
        url = "https://plvr.land.moi.gov.tw/DownloadOpenData"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)

            # 切換到「歷史資料」分頁
            await page.locator('a.btndl[aria-controls="tab_opendata_history_content"]').click()

            # 等待 select 出現
            select_locator = page.locator("#historySeason_id")
            await select_locator.wait_for(timeout=10000)

            # 正確方式：拿 element handles
            option_handles = await select_locator.locator("option").element_handles()

            result = {"historySeason_id": {}}
            for opt in option_handles:
                value = await opt.get_attribute("value")
                if value:
                    text = (await opt.inner_text()).strip()
                    result["historySeason_id"][value] = text

            await browser.close()

        if not result["historySeason_id"]:
            msg = "抓取失敗，歷史 Season 選單為空"
            log_error(ErrorCode.UNKNOWN_ERROR.value, msg, trace_id)
            return {"success": False, "trace_id": trace_id, "error": msg}

        need_to_updated = need_to_update_or_not(result)
        return {"success": True, "data": result["historySeason_id"], "updated": need_to_updated}

    except Exception as e:
        log_error(ErrorCode.UNKNOWN_ERROR.value, f"抓取失敗：{str(e)}", trace_id)
        return {"success": False, "trace_id": trace_id, "error": str(e)}
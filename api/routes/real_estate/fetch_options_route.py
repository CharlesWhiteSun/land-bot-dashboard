from fastapi import APIRouter, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from utils.logger import log_error
from enums.error_code import ErrorCode
import traceback
import os
import json

router = APIRouter()

DATA_DIR = os.path.join("api", "data", "real_estate", "raw")
DATA_FILE = os.path.join(DATA_DIR, "fetch_options_route.txt")


def save_or_update_data(new_data: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    # 檔案不存在：直接建立並寫入
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)
        return

    # 檔案存在：讀取後比較是否有缺少 key
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        existing_data = json.load(f)

    # 比較並補齊缺漏的 key-value
    updated = False
    for key, val in new_data["historySeason_id"].items():
        if key not in existing_data.get("historySeason_id", {}):
            existing_data["historySeason_id"][key] = val
            updated = True

    if updated:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)


@router.get("/fetch_options")
async def fetch_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://plvr.land.moi.gov.tw/DownloadOpenData")

        # 點擊「非本期下載」tab
        history_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.btndl[aria-controls="tab_opendata_history_content"]'))
        )
        history_tab.click()

        # 等待下拉選單出現
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "historySeason_id"))
        )

        # 解析 HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")
        select_element = soup.find("select", {"id": "historySeason_id"})
        if not select_element:
            raise HTTPException(status_code=404, detail="找不到 historySeason_id 元素")

        result = {
            "historySeason_id": {
                opt["value"]: opt.text.strip()
                for opt in select_element.find_all("option")
                if opt.get("value")
            }
        }

        # 檢查檔案並儲存/更新
        save_or_update_data(result)

        return result

    except Exception as e:
        tb_str = traceback.format_exc()
        log_error(ErrorCode.UNKNOWN_ERROR.value, f"Selenium 抓取失敗：{str(e)}", "")
        raise HTTPException(status_code=500, detail=f"抓取失敗：{str(e)}\nStacktrace:\n{tb_str}") from e

    finally:
        if driver:
            driver.quit()

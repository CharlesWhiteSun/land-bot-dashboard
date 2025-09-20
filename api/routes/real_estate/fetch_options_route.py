import os
import json
from bs4 import BeautifulSoup
from fastapi import APIRouter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
import tempfile

from enums.error_code import ErrorCode
from utils.logger import log_error
from utils.trace import generate_trace_id
from utils.response_helper import success_response, error_response
from config.paths import CHROMEDRIVER_DIR, RAW_DATA_DIR


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
    chrome_options = Options()
    tmp_user_data_dir = tempfile.mkdtemp(prefix="chrome_", dir=RAW_DATA_DIR)
    chrome_options.add_argument(f"--user-data-dir={tmp_user_data_dir}")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--log-level=3")  # ERROR 以下訊息不會出現
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--remote-debugging-port=9222")

    driver = None
    try:
        os.makedirs(CHROMEDRIVER_DIR, exist_ok=True)
        chromedriver_path = chromedriver_autoinstaller.install(path=CHROMEDRIVER_DIR)
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get("https://plvr.land.moi.gov.tw/DownloadOpenData")

        history_tab = WebDriverWait(driver, 10, poll_frequency=0.25).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'a.btndl[aria-controls="tab_opendata_history_content"]'))
        )
        history_tab.click()

        WebDriverWait(driver, 10, poll_frequency=0.25).until(
            EC.presence_of_element_located((By.ID, "historySeason_id"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        select_element = soup.find("select", {"id": "historySeason_id"})
        if not select_element:
            trace_id = generate_trace_id()
            msg = 'Selenium 抓取失敗'
            log_error(ErrorCode.UNKNOWN_ERROR.value, msg, trace_id)
            return {
                "success": False,
                "trace_id": trace_id,
                "error": msg
            }

        result = {
            "historySeason_id": {
                opt["value"]: opt.text.strip()
                for opt in select_element.find_all("option")
                if opt.get("value")
            }
        }

        updated = save_or_update_data(result)
        return {
            "success": True,
            "data": result["historySeason_id"],
            "updated": updated
        }

    except Exception as e:
        trace_id = generate_trace_id()
        log_error(ErrorCode.UNKNOWN_ERROR.value, f"Selenium 抓取失敗：{str(e)}", trace_id)
        return {
            "success": False,
            "trace_id": trace_id,
            "error": str(e)
        }

    finally:
        if driver:
            driver.quit()


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

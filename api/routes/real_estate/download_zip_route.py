import os
import requests
from fastapi import APIRouter, Query
from typing import Tuple

from utils.logger import log_error
from enums.error_code import ErrorCode
from utils.trace import generate_trace_id
from utils.response_helper import success_response, error_response
from config.paths import RAW_DATA_DIR  # 統一使用全域可寫入資料夾

# ===== 核心下載函式 =====
def download_season_zip(season: str) -> Tuple[bool, str, str]:
    url = f"https://plvr.land.moi.gov.tw/DownloadSeason?season={season}&type=zip&fileName=lvr_landcsv.zip"
    trace_id = generate_trace_id()

    # 使用全域資料夾
    save_dir = RAW_DATA_DIR
    zip_path = os.path.join(save_dir, f"{season}.zip")
    os.makedirs(save_dir, exist_ok=True)

    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            log_error(ErrorCode.FILE_NOT_FOUND.value, f"下載失敗: {response.status_code}", trace_id)
            return False, f"下載失敗，狀態碼：{response.status_code}", trace_id

        with open(zip_path, "wb") as f:
            f.write(response.content)

        return True, f"{season}.zip 下載並儲存成功", ""

    except Exception as e:
        log_error(ErrorCode.UNKNOWN_ERROR.value, str(e), trace_id)
        return False, f"下載過程出錯：{str(e)}", trace_id


# ===== FastAPI Router =====
router = APIRouter()


@router.get("/download_zip")
async def download_history_zip_by_season(season: str = Query(..., min_length=1, max_length=10)):
    success, message, trace_id = download_season_zip(season)

    if not success:
        return error_response(
            error_code=ErrorCode.FILE_NOT_FOUND.value,
            message=message,
            trace_id=trace_id,
            status_code=404
        )

    return success_response(message=message)

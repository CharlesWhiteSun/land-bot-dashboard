import os
import requests
from fastapi import APIRouter, HTTPException, Query
from utils.logger import log_error
from enums.error_code import ErrorCode
from utils.trace import generate_trace_id
from utils.response_helper import success_response, error_response

router = APIRouter()

@router.get("/download_zip")
def download_real_estate_zip(season: str = Query(..., min_length=5, max_length=5)):
    url = f"https://plvr.land.moi.gov.tw/DownloadSeason?season={season}&type=zip&fileName=lvr_landcsv.zip"

    save_dir = os.path.join("api", "data", "real_estate", "raw")
    os.makedirs(save_dir, exist_ok=True)

    zip_path = os.path.join(save_dir, f"{season}.zip")

    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            trace_id = f"DL-{season}"
            log_error(ErrorCode.FILE_NOT_FOUND.value, f"下載失敗: {response.status_code}", trace_id)
            return error_response(
                error_code=ErrorCode.FILE_NOT_FOUND.value,
                message="資料下載失敗，請稍後再試",
                trace_id=trace_id,
                status_code=404
            )

        # 儲存檔案
        with open(zip_path, "wb") as f:
            f.write(response.content)

        return success_response(
            data=None, 
            message=f"{season}.zip 下載並儲存成功"
        )

    except Exception as e:
        trace_id = generate_trace_id()
        log_error(ErrorCode.UNKNOWN_ERROR.value, str(e), trace_id)
        return error_response(
            error_code=ErrorCode.UNKNOWN_ERROR.value,
            message="資料抓取失敗，請稍後再試",
            trace_id=trace_id,
            status_code=500
        )

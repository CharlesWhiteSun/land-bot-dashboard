import os
import requests
from fastapi import APIRouter, HTTPException, Query
from utils.logger import log_error
from enums.error_code import ErrorCode

router = APIRouter()

@router.get("/download_zip")
def download_real_estate_zip(season: str = Query(..., min_length=5, max_length=5)):
    url = f"https://plvr.land.moi.gov.tw/DownloadSeason?season={season}&type=zip&fileName=lvr_landcsv.zip"

    save_dir = os.path.join(os.path.dirname(__file__), "raw")
    os.makedirs(save_dir, exist_ok=True)

    zip_path = os.path.join(save_dir, f"{season}.zip")

    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            trace_id = f"DL-{season}"
            log_error(ErrorCode.FILE_NOT_FOUND.value, f"下載失敗: {response.status_code}", trace_id)
            raise HTTPException(status_code=404, detail=f"找不到壓縮檔案：{season}")

        # 儲存檔案
        with open(zip_path, "wb") as f:
            f.write(response.content)

        return {"message": f"{season}.zip 下載並儲存成功", "path": zip_path}

    except Exception as e:
        trace_id = f"DL-{season}"
        log_error(ErrorCode.UNKNOWN_ERROR.value, str(e), trace_id)
        raise HTTPException(status_code=500, detail=f"檔案下載失敗：{str(e)}") from e

from fastapi import FastAPI
from api.routes.real_estate import fetch_options_route
from api.routes.real_estate import download_zip_route
from api.routes.real_estate import fetch_latest_notice_route
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from ngui.preprocessing.process_real_estate_and_import import *
from utils.logger import log_info
from utils.response_helper import success_response, error_response
from service.fetch_service import *

scheduler = BackgroundScheduler()

# def interval_s3():
#     print("🕒 [APScheduler] 每 3 秒印出這段話")

def cron_h2m0():
    log_info("📅 排程任務執行：每日 AM 02:00 任務已觸發")

    # fetch_func()
    
    print("📅 每日排程：AM 02:00 任務已執行")

@asynccontextmanager
async def _lifespan(_: FastAPI):
    print("⚡ 伺服器啟動，執行一次性任務")
    
    fetch_func() # 執行下載地產資料的動作
    apply_clean_and_import_file() # 加入資料清洗與匯入資料庫的邏輯

    log_info("⚡ FastAPI 伺服器啟動，一次性任務已執行完成")

    print("🚀 FastAPI 啟動，啟動 APScheduler...")
    # scheduler.add_job(interval_s3, "interval", seconds=3)
    scheduler.add_job(cron_h2m0, "cron", hour=2, minute=0)
    scheduler.start()
    log_info("🚀 FastAPI 伺服器啟動，APScheduler 已新增排程，相關排程將會定時啟動")

    yield
    print("🛑 FastAPI 關閉，關閉 APScheduler...")
    scheduler.shutdown()
    log_info("🛑 FastAPI 伺服器關閉，並關閉相關 APScheduler 排程")


app = FastAPI(lifespan=_lifespan)

@app.get("/")
def read_root():
    return success_response(message="FastAPI, APScheduler with Lifespan 已經啟動!")

app.include_router(fetch_options_route.router, prefix="/api")
app.include_router(download_zip_route.router, prefix="/api")
app.include_router(fetch_latest_notice_route.router, prefix="/api")

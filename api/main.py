from fastapi import FastAPI
from api.routes.real_estate import fetch_options_route
from api.routes.real_estate import download_zip_route
from api.routes.real_estate import fetch_latest_notice_route


app = FastAPI()
app.include_router(fetch_options_route.router, prefix="/api")
app.include_router(download_zip_route.router, prefix="/api")
app.include_router(fetch_latest_notice_route.router, prefix="/api")


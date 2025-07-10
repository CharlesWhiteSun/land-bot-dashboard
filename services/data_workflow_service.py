import streamlit as st

from enums.error_code import ErrorCode
from services.real_estate_data_service import RealEstateDataService
from utils.ui_error_handler import UIErrorHandler
from utils.trace import generate_trace_id
from utils.logger import log_error
from providers.enum_error_provider import EnumErrorProvider


def load_initial_data() -> bool:

    err_handler = UIErrorHandler(EnumErrorProvider())

    try:
        # 驗證資料是否可載入
        temp_service = RealEstateDataService()
        _ = temp_service.load_city_data("台北市")
        return True

    except FileNotFoundError as e:
        trace_id = generate_trace_id()
        log_error(ErrorCode.FILE_NOT_FOUND.value, str(e), trace_id)
        err_handler.show_error(ErrorCode.FILE_NOT_FOUND, trace_id)

    except ValueError as e:
        trace_id = generate_trace_id()
        log_error(ErrorCode.MISSING_COLUMNS.value, str(e), trace_id)
        err_handler.show_error(ErrorCode.MISSING_COLUMNS, trace_id)

    except Exception as e:
        trace_id = generate_trace_id()
        log_error(ErrorCode.UNKNOWN_ERROR.value, str(e), trace_id)
        err_handler.show_error(ErrorCode.UNKNOWN_ERROR, trace_id)

    return False


def run_data_service():
    err_handler = UIErrorHandler(EnumErrorProvider())
    data_service = RealEstateDataService()

    city = st.sidebar.selectbox("請選擇縣市", ["台北市", "台中市", "高雄市"])

    try:
        df = data_service.load_city_data(city)
        st.success(f"成功載入 {len(df)} 筆資料")
        st.dataframe(df.head())

    except FileNotFoundError as e:
        trace_id = generate_trace_id()
        log_error(ErrorCode.FILE_NOT_FOUND.value, str(e), trace_id)
        err_handler.show_error(ErrorCode.FILE_NOT_FOUND, trace_id)

    except ValueError as e:
        trace_id = generate_trace_id()
        log_error(ErrorCode.MISSING_COLUMNS.value, str(e), trace_id)
        err_handler.show_error(ErrorCode.MISSING_COLUMNS, trace_id)

    except Exception as e:
        trace_id = generate_trace_id()
        log_error(ErrorCode.UNKNOWN_ERROR.value, str(e), trace_id)
        err_handler.show_error(ErrorCode.UNKNOWN_ERROR, trace_id)

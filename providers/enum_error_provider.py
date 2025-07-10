from typing import Dict
from interface.error_provider_interface import ErrorProviderInterface
from enums.error_code import ErrorCode

ERROR_MESSAGES = {
    ErrorCode.FILE_NOT_FOUND: {
        "title": "找不到資料檔案",
        "message": "無法在指定位置找到資料檔案。",
        "suggest": "請確認資料路徑是否正確或資料是否尚未下載。"
    },
    ErrorCode.MISSING_COLUMNS: {
        "title": "欄位遺失或格式錯誤",
        "message": "必要欄位缺失或格式不正確。",
        "suggest": "請檢查資料是否完整。"
    },

    ErrorCode.NETWORK_ERROR: {
        "title": "網路連線錯誤",
        "message": "無法連線至外部資源或連線逾時。",
        "suggest": "請確認您的網路狀態，或稍後再試。"
    },

    ErrorCode.DB_CONNECTION_ERROR: {
        "title": "資料庫連線錯誤",
        "message": "系統無法連接至資料庫。",
        "suggest": "請檢查資料庫服務或設定。"
    },

    ErrorCode.TEXT_PARSE_ERROR: {
        "title": "文字解析錯誤",
        "message": "處理文字時發生格式錯誤或無法解析的內容。",
        "suggest": "請檢查輸入內容是否符合格式。"
    },
    ErrorCode.REGEX_COMPILE_ERROR: {
        "title": "正規表達式語法錯誤",
        "message": "編譯正規表達式時發生錯誤。",
        "suggest": "請聯絡開發人員檢查正規式語法。"
    },
    ErrorCode.REGEX_NO_MATCH: {
        "title": "無法比對文字格式",
        "message": "無法從文字中比對到正規化的規則。",
        "suggest": "請確認來源文字格式是否異動，或回報此問題。"
    },

    ErrorCode.SERVER_BUSY_ERROR: {
        "title": "伺服器忙碌或錯誤",
        "message": "伺服器當前無法處理請求，可能過載或維護中。",
        "suggest": "請稍後再試，或聯絡系統管理員。"
    },
    
    ErrorCode.UNKNOWN_ERROR: {
        "title": "未知錯誤",
        "message": "系統發生未知錯誤。",
        "suggest": "請重新啟動或聯絡管理員。"
    },
}

class EnumErrorProvider(ErrorProviderInterface):
    def get_error(self, code: ErrorCode, trace_id: str = None) -> Dict[str, str]:
        error = ERROR_MESSAGES.get(code, ERROR_MESSAGES[ErrorCode.UNKNOWN_ERROR]).copy()
        if trace_id:
            error["trace_id"] = trace_id
        return error

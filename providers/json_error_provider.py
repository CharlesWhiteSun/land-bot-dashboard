import json
from typing import Dict
from interface.error_provider_interface import ErrorProviderInterface

class JsonErrorProvider(ErrorProviderInterface):
    def __init__(self, json_path: str):
        self.error_dict = self._load_errors(json_path)

    def _load_errors(self, path: str) -> Dict[str, Dict[str, str]]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {
                "E999": {
                    "title": "未知錯誤",
                    "message": "系統發生未知錯誤。",
                    "suggest": "請重新啟動或聯絡管理員。"
                }
            }

    def get_error(self, code: str, trace_id: str = None) -> Dict[str, str]:
        error = self.error_dict.get(code, self.error_dict.get("E999"))
        if trace_id:
            error['trace_id'] = trace_id
        return error

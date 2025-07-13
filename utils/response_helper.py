from fastapi.responses import JSONResponse
from typing import Optional, Any

def success_response(data: Any = None, message: str = "成功") -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": message,
            "data": data,
            "error_code": None,
            "trace_id": None
        }
    )

def error_response(error_code: str, message: str, trace_id: Optional[str] = None, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "data": None,
            "error_code": error_code,
            "trace_id": trace_id
        }
    )

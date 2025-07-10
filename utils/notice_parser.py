import re
from typing import Dict

from utils.logger import log_error
from utils.trace import generate_trace_id
from enums.error_code import ErrorCode


def parse_notice_to_dict(text: str) -> Dict[str, Dict[str, str]]:
    """
    將公告文字轉換為結構化物件：
    例如：
    資料內容：登記日期 114年6月11日至 114年6月20日之買賣案件，
             及訂約日期 114年5月11日至 114年5月20日之租賃案件，
             及交易日期114年5月11日至 114年5月20日之預售屋案件
    =>
    {
        "登記日期": {"start": "114-6-11", "end": "114-6-20"},
        "訂約日期": {"start": "114-5-11", "end": "114-5-20"},
        "交易日期": {"start": "114-5-11", "end": "114-5-20"}
    }
    """
    pattern = r"(登記日期|訂約日期|交易日期)\s*([0-9]+)年([0-9]+)月([0-9]+)日[至到 ]+([0-9]+)年([0-9]+)月([0-9]+)日"

    try:
        matches = re.findall(pattern, text)
    except re.error as e:
        trace_id = generate_trace_id()
        log_error(ErrorCode.REGEX_COMPILE_ERROR.value, str(e), trace_id)
        raise ValueError(f"正規表達式錯誤：{str(e)} | TraceID: {trace_id}") from e

    if not matches:
        trace_id = generate_trace_id()
        log_error(ErrorCode.REGEX_NO_MATCH.value, "找不到符合公告格式的文字", trace_id)
        raise ValueError(f"公告文字格式錯誤，無法比對出日期區間 | TraceID: {trace_id}")

    result = {}
    for match in matches:
        label, y1, m1, d1, y2, m2, d2 = match
        result[label] = {
            "start": f"{y1}-{m1}-{d1}",
            "end": f"{y2}-{m2}-{d2}"
        }

    return result
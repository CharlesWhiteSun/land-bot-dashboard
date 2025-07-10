import unittest
import re
from utils import logger
import logging


class TestLogger(unittest.TestCase):
    def setUp(self):
        class MockHandler(logging.Handler):
            def __init__(self):
                super().__init__()
                self.last_record = None

            def emit(self, record):
                self.last_record = record

        self.mock_handler = MockHandler()
        self.mock_handler.setLevel(logging.DEBUG)

        # 備份原本的 handlers
        self.original_handlers = logger.logger.handlers
        logger.logger.handlers = [self.mock_handler]

    def tearDown(self):
        # 還原原本 handlers
        logger.logger.handlers = self.original_handlers

    def _assert_log_called_with(self, level_name: str, expected_msg_pattern: str):
        log_record = self.mock_handler.last_record
        self.assertIsNotNone(log_record, "沒有接收到 log 訊息")
        self.assertEqual(log_record.levelname, level_name)
        self.assertRegex(log_record.getMessage(), expected_msg_pattern)

    def test_log_error_without_trace_id(self):
        logger.log_error("E001", "找不到資料檔案")
        self._assert_log_called_with("ERROR", r"ErrorCode=E001.*找不到資料檔案")

    def test_log_error_with_trace_id(self):
        logger.log_error("E002", "測試有 trace_id", trace_id="abc-123")
        self._assert_log_called_with("ERROR", r"TraceID=abc-123.*ErrorCode=E002.*測試有 trace_id")

    def test_log_warning(self):
        logger.log_warning("這是一個警告訊息")
        self._assert_log_called_with("WARNING", r"這是一個警告訊息")

    def test_log_info(self):
        logger.log_info("這是一個資訊訊息")
        self._assert_log_called_with("INFO", r"這是一個資訊訊息")

    def test_log_debug(self):
        logger.log_debug("這是一個除錯訊息")
        self._assert_log_called_with("DEBUG", r"這是一個除錯訊息")


if __name__ == "__main__":
    unittest.main()

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse
import time

BLOCKED_PAGE_HTML = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>存取受限</title>
    <style>
        body {
            background: linear-gradient(135deg, #ff4b1f, #1fddff);
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        h1 {
            font-size: 4rem;
            margin-bottom: 0.5rem;
        }
        p {
            font-size: 1.5rem;
            margin-bottom: 2rem;
        }
        .retry-button {
            background: #fff;
            color: #ff4b1f;
            border: none;
            padding: 1rem 2rem;
            font-size: 1.25rem;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            text-decoration: none;
        }
        .retry-button:hover {
            background-color: #f0f0f0;
        }
        small {
            margin-top: 3rem;
            font-size: 0.9rem;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <h1>🚫 存取受限</h1>
    <p>您的 IP 由於過於頻繁的請求，已被暫時封鎖<br> - 請稍後再試 - </p>
    <a href="/" class="retry-button">回首頁</a>
    <p>若有任何疑問請聯絡站長</p>
</body>
</html>
"""

class IPBlacklistMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, block_time_seconds=60, max_requests=10, interval_seconds=10):
        super().__init__(app)
        self.block_time_seconds = block_time_seconds  # 封鎖時間（秒）
        self.max_requests = max_requests              # 允許最大請求數
        self.interval_seconds = interval_seconds      # 監控時間區間（秒）

        self.ip_access_log = {}    # 紀錄IP請求時間，格式: {ip: [timestamp1, timestamp2, ...]}
        self.ip_blocked_until = {} # 封鎖IP到期時間，格式: {ip: timestamp}

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        now = time.time()

        # 檢查 IP 是否被封鎖中
        if ip in self.ip_blocked_until:
            if now < self.ip_blocked_until[ip]:
                # 尚未解封，回傳封鎖頁面
                return HTMLResponse(content=BLOCKED_PAGE_HTML, status_code=403)
            else:
                # 解封，清除紀錄
                del self.ip_blocked_until[ip]
                self.ip_access_log[ip] = []

        # 紀錄本次請求時間
        if ip not in self.ip_access_log:
            self.ip_access_log[ip] = []
        self.ip_access_log[ip].append(now)

        # 清除過期的請求時間 (超過 interval_seconds)
        self.ip_access_log[ip] = [t for t in self.ip_access_log[ip] if now - t <= self.interval_seconds]

        # 判斷是否超過最大請求數，若超過則封鎖 IP
        if len(self.ip_access_log[ip]) > self.max_requests:
            self.ip_blocked_until[ip] = now + self.block_time_seconds
            return HTMLResponse(content=BLOCKED_PAGE_HTML, status_code=403)

        # 繼續執行請求
        response = await call_next(request)
        return response
